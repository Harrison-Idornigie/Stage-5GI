from odoo import models, fields, api
import  logging

class report(models.AbstractModel):
    _name = 'report.nh_analytic_report.report'

    @api.multi
    def get_report_values(self, docids, data=None):
        docargs = data
        return docargs