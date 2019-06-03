from odoo import models, fields, api
import logging

class RealTrackWizard(models.TransientModel):
    _name = "fleet_tracking.real_track_wizard"

    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicule", ondelete='cascade')
    vehicle_id_value = fields.Integer(compute="get_id")
    url_traccar_server = fields.Char(compute="get_traccar_url")
    traccar_device_id = fields.Integer(compute="get_traccar_id")
    last_latitude = fields.Float(compute="get_last_latitude", digits=(16, 8))
    last_longitude = fields.Float(compute="get_last_longitude", digits=(16, 8))

    def get_id(self):
        for rec in self:
            rec.vehicle_id_value = rec.vehicle_id.id

    @api.model
    def get_traccar_url(self):
        url_traccar_server = self.env['ir.config_parameter'].sudo().get_param('traccar_server_url')
        for rec in self:
            rec.url_traccar_server = url_traccar_server

    def get_traccar_id(self):
        for rec in self:
            rec.traccar_device_id = rec.vehicle_id.traccar_device_id

    def get_last_latitude(self):
        for rec in self:
            rec.last_latitude = rec.vehicle_id.vehicle_latitude

    def get_last_longitude(self):
        for rec in self:
            rec.last_longitude = rec.vehicle_id.vehicle_longitude