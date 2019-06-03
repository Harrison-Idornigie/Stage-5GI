# -*- coding: utf-8 -*-
import datetime
from odoo import models, fields, api, exceptions, _


class wizard(models.TransientModel):
    _name = 'nh_analytic_report.wizard'

    account_ids = fields.Many2many('account.analytic.account', string="Analytic Account")
    start_date = fields.Date(string="Start Date", default=fields.Date.today, required=True)
    end_date = fields.Date(string="End Date", default=fields.Date.today, required=True)
    has_accounts = fields.Boolean(compute='_check_if_account', track_visibility='onchange')

    @api.depends('account_ids')
    def _check_if_account(self):
        for r in self:
            if r.account_ids:
                r.has_accounts = True
            else:
                r.has_accounts = False

    @api.multi
    def get_analytics(self):
        analytics = []
        accounts = []
        if self.has_accounts:
            ids = []
            for ac in self.account_ids:
                ids.append(ac.id)
            accounts = self.env['account.analytic.account'].search([('id', 'in', ids)])
        else:
            accounts = self.env['account.analytic.account'].search([('id', '>=', 0)])

        for account in accounts:
            analytic = {'name': account.name, 'balance': account.balance, 'lines':[]}
            analytic_lines = self.env['account.analytic.line'].search([('account_id', '=', account.id)])
            if not analytic_lines:
                continue
            for line in analytic_lines:
                temp = {}
                date_time_str = line.date
                date_time_obj = datetime.datetime.strptime(date_time_str, '%Y-%m-%d')
                temp['date'] = date_time_obj.strftime("%A %d. %B %Y")
                #temp['reference'] = line.ref
                temp['description'] = line.name
                temp['general_account'] = line.general_account_id.code
                #temp['quantity'] = line.unit_amount
                temp['amount'] = line.amount
                analytic['lines'].append(temp)
            analytics.append(analytic)


        return analytics

    @api.multi
    def print_pdf(self):
        datas = {
            'start_date': self.start_date,
            'end_date': self.end_date,
            'analytics': self.get_analytics()
        }

        return {
            'type': 'ir.actions.report',
            'name': 'nh_analytic_report.report',
            'res_model': 'report.nh_analytic_report.report',
            'model': 'report.nh_analytic_report.report',
            'report_type': 'qweb-pdf',
            'report_name': 'nh_analytic_report.report',
            'data': datas,
        }

    @api.constrains('start_date', 'end_date')
    def _check_start_end(self):
        for r in self:
            if r.end_date < r.start_date:
                raise exceptions.ValidationError(_("The Start Date should be lower or equal to the End Date"))
