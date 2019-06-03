from odoo import models, api, fields, exceptions, _
from odoo.modules import get_module_resource
import logging
import requests
from datetime import datetime, timedelta
import json
import pytz


_logger = logging.getLogger(__name__)

PATH_CONFIG_FILE = get_module_resource('fleet_tracking', 'config.json')

file = open(PATH_CONFIG_FILE, encoding='utf-8').read()
configs = json.loads(file)

FIRST_TIME = configs['FIRST_TIME']
PREVIOUS_DATE = configs['PREVIOUS_DATE']

def fetch_positions_history(cookie, deviceId, toDate, timezone):
    global PREVIOUS_DATE
    global FIRST_TIME

    if FIRST_TIME:
        params = {'deviceId': [int(deviceId)], 'from': "2000-01-01T00:00:00Z", 'to': toDate}
    else:
        params = {'deviceId': [int(deviceId)], 'from': PREVIOUS_DATE, 'to': toDate}
    headers = {'Cookie': cookie[0], 'Content-Type': 'application/json', 'Accept': 'application/json'}
    response = requests.get(cookie[1] + '/api/reports/route', headers=headers, params=params)
    result = []
    for position in response.json():
        if position['deviceId'] == deviceId:
            datetime_obj = datetime.strptime(position['fixTime'], "%Y-%m-%dT%H:%M:%S.%f+0000")
            datetime_obj_tz = datetime_obj.astimezone(timezone)
            result.append({
                'lat': float(position['latitude']),
                'long': float(position['longitude']),
                'time': datetime_obj_tz.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            })
    return result


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    def change_color_on_kanban(self):
        """    this method is used to change color index :return: index of color for kanban view    """
        for record in self:
            active_time_str = None
            if record.date_localization:
                inactivity_period_duration = self.env['ir.config_parameter'].sudo().get_param('inactivity_period_duration', default='30')
                active_time_str = fields.Datetime.to_string(datetime.now() - timedelta(minutes=int(inactivity_period_duration)))
            if record.gps_tracking and record.vehicle_latitude and record.vehicle_longitude and record.date_localization >= active_time_str:
                color = 5
                state = 'Tracking'
            elif record.gps_tracking:
                color = 7
                state = 'Tracking, not active'
            elif not record.gps_tracking:
                color = 2
                state = 'Not tracking'
            else:
                color = 0
                state = 'Unknown'
            record.kanban_color = color
            record.kanban_state = state

    vehicle_latitude = fields.Float(string='Geo Latitude', digits=(16, 8))
    vehicle_longitude = fields.Float(string='Geo Longitude', digits=(16, 8))
    date_localization = fields.Datetime(string='Last Time Geolocated')
    traccar_uniqueID = fields.Char(string='Traccar unique ID')
    traccar_device_id = fields.Integer(string='Traccar device ID')
    gps_tracking = fields.Boolean(string='Tracking', default=False)
    location_history_ids = fields.One2many('fleet.vehicle.location.history', 'vehicle_id', string='Location History', copy=False, readonly=True)

    working_hours_from = fields.Float(string='Shift Starting Hour')
    working_hours_to = fields.Float(string='Shift Ending Hour')
    date_inactive_filter = fields.Date(string='On Date', store=False)

    pre_tracking_odometer = fields.Float(string='Odometer Before Tracking Started',
                            help='Odometer status when the vehicle was started to be tracked on (each location update then updates the odometer).')

    kanban_color = fields.Integer('Color Index', compute="change_color_on_kanban")
    kanban_state = fields.Char('Tracking State', compute="change_color_on_kanban")


    def login(self):
        ir_config_obj = self.env['ir.config_parameter'].sudo()
        url = ir_config_obj.get_param('traccar_server_url', default='http://127.0.0.1:8082')
        traccar_username = ir_config_obj.get_param('traccar_username', default='admin')
        traccar_password = ir_config_obj.get_param('traccar_password', default='admin')

        response = requests.post(url + '/api/session', data={'email': traccar_username, 'password': traccar_password})
        res = response.headers.get('Set-Cookie'), url

        # check if there's an Odoo group in Traccar, which we link all the devices from Odoo and all geofences to
        self.check_odoo_traccar_group(res)

        return res

    def check_odoo_traccar_group(self, cookie):
        ir_config_obj = self.env['ir.config_parameter'].sudo()
        headers = {'Cookie': cookie[0], 'Content-Type': 'application/json', 'Accept': 'application/json'}
        group_id = False
        OdooTraccarGroupId = ir_config_obj.get_param('odoo_traccar_groupId')
        try:
            if OdooTraccarGroupId:
                response = requests.get(cookie[1] + '/api/groups', headers=headers)
                data = response.json()
                group_id = False
                for group in data:
                    if str(OdooTraccarGroupId) == str(group['id']):
                        group_id = True
            if not group_id:
                group = {'name': 'Odoo Group'}
                response = requests.post(cookie[1] + '/api/groups', headers=headers, data=json.dumps(group))
                data = response.json()
                group_id = data and data['id'] or False
                if group_id:
                    ir_config_obj.set_param('odoo_traccar_groupId', (group_id))
        except:
            _logger.exception("Traccar - Odoo group retrieval failed.")

    @api.one
    def remove_device(self, cookie, uniqueID):
        headers = {'Cookie': cookie[0], 'Content-Type': 'application/json', 'Accept': 'application/json'}
        response = requests.get(cookie[1] + '/api/devices', headers=headers)
        data = response.json()
        for device in data:
            if uniqueID == device['uniqueId']:
                response = requests.delete(cookie[1] + '/api/devices/' + str(device['id']), headers=headers)

    @api.one
    def add_device(self, cookie, uniqueID):
        headers = {'Cookie': cookie[0], 'Content-Type': 'application/json', 'Accept': 'application/json'}
        response = requests.get(cookie[1] + '/api/devices', headers=headers)
        data = response.json()
        device_id = False
        for device in data:
            if uniqueID == device['uniqueId']:
                device_id = device['id']

        if not device_id:
            OdooTraccarGroupId = self.env['ir.config_parameter'].sudo().get_param('odoo_traccar_groupId')
            device = {'name': self.name, 'uniqueId': uniqueID}
            if OdooTraccarGroupId: device.update(groupId=OdooTraccarGroupId)
            response = requests.post(cookie[1] + '/api/devices', headers=headers, data=json.dumps(device))
            data = response.json()
            device_id = data and data['id'] or False
        self.write({'traccar_device_id': device_id})

    @api.model
    def get_location_history(self):
        global PREVIOUS_DATE
        global FIRST_TIME

        tz = pytz.timezone(self.env.user.partner_id.tz)
        toDate = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        logging.info(toDate+"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")

        try:
            cookie = self.login()
            for vehicle in self.env['fleet.vehicle'].search([('gps_tracking', '=', True)]):
                logging.info("FETCHING FOR " + str(vehicle.traccar_device_id) + ".....................................................")
                positions = fetch_positions_history(cookie, vehicle.traccar_device_id, toDate, tz)
                logging.info('REGISTERING POSITIONS' + str(positions) + ".....................................................")
                for position in positions:
                    self.env['fleet.vehicle.location.history'].create({
                        'vehicle_id': vehicle.id,
                        'name': vehicle.name,
                        'vehicle_latitude': position['lat'],
                        'vehicle_longitude': position['long'],
                        'date_localization': position['time'],
                        'driver_name': str(vehicle.driver_id.name)
                    })
                if positions:
                    last_position = positions[-1]
                    vehicle.write({
                        'vehicle_latitude': last_position['lat'],
                        'vehicle_longitude': last_position['long'],
                        'date_localization': last_position['time']
                    })
            logging.info("MODIFING CONFIGURATIONS .....................................................")
            configs={ "PREVIOUS_DATE": toDate }
            if FIRST_TIME:
                FIRST_TIME = False
                configs.update({
                    "FIRST_TIME": False
                })
            else:
                configs.update({
                    "FIRST_TIME": False
                })
            PREVIOUS_DATE = toDate
            with open(PATH_CONFIG_FILE, 'w', encoding='utf-8') as outfile:
                json.dump(configs, outfile, indent=4, ensure_ascii=False)
        except Exception as e:
            logging.info(e)
            logging.info("000000000000000000000000000000000000000000000000000000000000000000000000000000000000")

    @api.multi
    def track_vehicle(self):
        self.ensure_one()
        context = self.env.context.copy()
        vehicles = [self.id]
        view_map_id = self.env.ref('fleet_tracking.real_track_wizard_view')
        res = self.env['fleet_tracking.real_track_wizard'].create({'vehicle_id': vehicles[0]})
        return {
            'name': _('Track Vehicle'),
            'type': 'ir.actions.act_window',
            'res_model': 'fleet_tracking.real_track_wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'views': [(view_map_id.id, 'form')],
            'res_id': res.id,
            'context': context,
            'target': 'inline',
            'domain': [('id', 'in', vehicles)]
        }

    @api.multi
    def last_location(self):
        self.ensure_one()
        context = self.env.context.copy()
        vehicles = [self.id]
        view_map_id = self.env.ref('fleet_tracking.last_location_wizard_view')
        res = self.env['fleet_tracking.last_location_wizard'].create({'vehicle_id': vehicles[0]})
        return {
            'name': _('Vehicle Last Location'),
            'type': 'ir.actions.act_window',
            'res_model': 'fleet_tracking.last_location_wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'views': [(view_map_id.id, 'form')],
            'res_id': res.id,
            'context': context,
            'target': 'new',
            'domain': [('id', 'in', vehicles)]
        }

    @api.multi
    def daily_trip(self):
        self.ensure_one()
        context = self.env.context.copy()
        vehicles = [self.id]
        view_wizard_id = self.env.ref('fleet_tracking.daily_trip_wizard_view')
        res = self.env['fleet_tracking.daily_trip_wizard'].create({'vehicle_id': vehicles[0]})
        return {
            'name': _('Vehicle Daily Trip'),
            'type': 'ir.actions.act_window',
            'res_model': 'fleet_tracking.daily_trip_wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'views': [(view_wizard_id.id, 'form')],
            'res_id': res.id,
            'context': context,
            'target': 'new',
            'domain': [('id', 'in', vehicles)]
        }

    @api.multi
    def toggle_gps_tracking(self):
        """ Inverse the value of the field ``gps_tracking`` on the records in ``self``. """
        for record in self:
            if not record.traccar_uniqueID:
                raise exceptions.Warning(_('You have not provided a Traccar device unique ID, please click Edit and enter it before adding/removing a device!'))
            record.gps_tracking = not record.gps_tracking

            try:
                cookie = record.login()
                uniqueID = record.traccar_uniqueID
                if record.gps_tracking:
                    record.add_device(cookie, uniqueID)
                else:
                    record.remove_device(cookie, uniqueID)
            except:
                raise exceptions.Warning(_("Could not connect to Traccar, please check your Traccar Settings!"))
