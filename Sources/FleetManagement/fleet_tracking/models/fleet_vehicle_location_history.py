from odoo import models, api, fields
from datetime import timedelta


class FleetVehicleLocationHistory(models.Model):
    _name = "fleet.vehicle.location.history"
    _order = 'date_localization desc'

    @api.multi
    def _compute_inactive(self):
        for rec in self:
            rec.inactive_period = False
            if not rec.vehicle_id or (rec.vehicle_latitude == 0 and rec.vehicle_longitude == 0) or not rec.date_localization:
                continue

            ir_config_param = self.env['ir.config_parameter'].sudo()
            inactivity_period_duration = ir_config_param.get_param('inactivity_period_duration', default='30')
            on_date = rec.date_localization
            on_date_dt = fields.Datetime.from_string(on_date)
            date_localization_from = on_date_dt - timedelta(minutes=int(inactivity_period_duration))
            date_localization_from_str = fields.Datetime.to_string(date_localization_from)

            all_history_records = self.search([('vehicle_id','=',rec.vehicle_id.id), ('date_localization','>=',date_localization_from_str), ('date_localization','<=',rec.date_localization)])
            if all_history_records:
                inactive = False
                for h in all_history_records:
                    if round(h.vehicle_latitude, 4) != round(rec.vehicle_latitude, 4) or round(h.vehicle_longitude, 4) != round(rec.vehicle_longitude, 4): # if locations are close enough
                        inactive = False
                        break
                    else:
                        inactive = True
                if inactive: rec.inactive_period = True

    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle', required=True, ondelete='cascade')
    name = fields.Char(string='Name', required=True)
    driver_name = fields.Char(string='Driver Name')
    image_small = fields.Binary(related='vehicle_id.image_small', string="Logo (small)")
    vehicle_latitude = fields.Float(string='Geo Latitude', digits=(16, 8))
    vehicle_longitude = fields.Float(string='Geo Longitude', digits=(16, 8))
    date_localization = fields.Datetime(string='Located on')
    inactive_period = fields.Boolean(string='Inactive Period', compute='_compute_inactive', store=False)

    all_day = fields.Boolean(string='All Day', default=True)