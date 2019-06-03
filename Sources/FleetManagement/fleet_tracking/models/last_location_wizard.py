from odoo import models, fields
from odoo.addons import decimal_precision as dp

class LastLocationWizard(models.TransientModel):
    _name = "fleet_tracking.last_location_wizard"

    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicule", ondelete='cascade')
    vehicle_id_value = fields.Integer(compute="get_id")
    vehicle_latitude = fields.Float(string='Geo Latitude', compute="get_lat", digits=(16, 8))
    vehicle_longitude = fields.Float(string='Geo Longitude', compute="get_lng", digits=(16, 8))

    def get_id(self):
        for rec in self:
            rec.vehicle_id_value = rec.vehicle_id.id

    def get_lat(self):
        for rec in self:
            rec.vehicle_latitude = rec.vehicle_id.vehicle_latitude

    def get_lng(self):
        for rec in self:
            rec.vehicle_longitude = rec.vehicle_id.vehicle_longitude