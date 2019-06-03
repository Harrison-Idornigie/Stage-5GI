from odoo import fields, models, api, _


class DailyTripWizard(models.TransientModel):
    _name = "fleet_tracking.daily_trip_wizard"

    vehicle_id = fields.Many2one("fleet.vehicle", string="Vehicles", required=True, ondelete='cascade')
    date = fields.Date(string="Date", default=fields.Date.today, required=True)

    @api.multi
    def display_trip(self):
        context = self.env.context.copy()
        view_map_id = self.env.ref('fleet_tracking.daily_trip_map_view')
        res = self.env['fleet_tracking.daily_trip_map'].create({'wizard_id': self.id})

        return {
            'name': _('Vehicle Daily Trip'),
            'type': 'ir.actions.act_window',
            'res_model': 'fleet_tracking.daily_trip_map',
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(view_map_id.id, 'form')],
            'target': 'new',
            'res_id': res.id,
            'context': context,
        }