from odoo import models, fields, api
import json

class FleetVehicleLocationHistoryMap(models.TransientModel):
    _name = "fleet_tracking.fleet_history_map"


    wizard_id = fields.Many2one('fleet_tracking.fleet_history_wizard', ondelete='cascade')
    positions = fields.Text(compute="get_history")

    @api.multi
    def get_history(self):
        result = []

        for vehicle in self.wizard_id.vehicle_ids:
            vec_result = {
                "id": vehicle.id,
                "name": "<b>"+vehicle.name+"</b><br/>",
                "drivername": vehicle.driver_id.name,
                "positions": []
            }
            vec_positions = self.env['fleet.vehicle.location.history'].search([
                ('vehicle_id', '=', vehicle.id),
                ('date_localization', '<=', self.wizard_id.end_date),
                ('date_localization', '>=', self.wizard_id.start_date)
            ])
            for pos in vec_positions:
                temp = {
                    "latitude": pos.vehicle_latitude,
                    "longitude": pos.vehicle_longitude,
                    #"date": pos.date_localization
                }
                vec_result['positions'].append(temp)
            result.append(vec_result)

        #logging.info(result)
        self.positions = json.dumps(result)
