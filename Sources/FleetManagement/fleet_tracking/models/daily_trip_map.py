from odoo import models, fields, api
import json

class DailyTripMap(models.TransientModel):
    _name = "fleet_tracking.daily_trip_map"

    wizard_id = fields.Many2one('fleet_tracking.daily_trip_wizard', ondelete='cascade')
    positions = fields.Text(compute="get_positions")

    @api.multi
    def get_positions(self):
        result = []
        vec_positions = self.env['fleet.vehicle.location.history'].search([
            ('vehicle_id', '=', self.wizard_id.vehicle_id.id),
            ('date_localization', '<=', self.wizard_id.date + " 23:59:59"),
            ('date_localization', '>=', self.wizard_id.date + " 00:00:00")
        ])
        for pos in vec_positions:
            temp = {
                "latitude": pos.vehicle_latitude,
                "longitude": pos.vehicle_longitude,
                #"date": pos.date_localization
            }
            result.append(temp)

        self.positions = json.dumps(result)
