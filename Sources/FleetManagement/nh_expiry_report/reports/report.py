from odoo import models, fields, api

class report(models.AbstractModel):
    _name = 'report.nh_expiry_report.report'

    @api.multi
    def get_report_values(self, docids, data=None):
        docargs = data
        return docargs