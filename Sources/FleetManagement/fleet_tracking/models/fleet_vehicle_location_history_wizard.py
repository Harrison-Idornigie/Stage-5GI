from odoo import fields, models, api, exceptions, _


class FleetVehicleLocationHistoryWizard(models.TransientModel):
    _name = "fleet_tracking.fleet_history_wizard"

    vehicle_ids = fields.Many2many("fleet.vehicle", string="Vehicles", required=True)
    start_date = fields.Datetime(string="Start Date", required=True)
    end_date = fields.Datetime(string="End Date", required=True)

    @api.constrains('start_date', 'end_date')
    def _check_start_end(self):
        """
        The method is to ensure that the start date is lesser than the end date
        :return:
        """
        for r in self:
            if r.end_date < r.start_date:
                raise exceptions.ValidationError(_("The Start Date should be lower or equal to the End Date"))

    @api.multi
    def display_history(self):
        context = self.env.context.copy()
        view_map_id = self.env.ref('fleet_tracking.fleet_vehicle_location_history_map')
        res = self.env['fleet_tracking.fleet_history_map'].create({'wizard_id': self.id})

        return {
            'name': _('Vehicle Location History'),
            'type': 'ir.actions.act_window',
            'res_model': 'fleet_tracking.fleet_history_map',
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(view_map_id.id, 'form')],
            'target': 'inline',
            'res_id': res.id,
            'context': context,
        }