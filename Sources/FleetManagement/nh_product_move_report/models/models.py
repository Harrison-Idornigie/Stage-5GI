# -*- coding: utf-8 -*-
import base64
from datetime import datetime, timedelta
import time

import openpyxl
from odoo import models, fields, api, exceptions, _

from odoo.modules import get_module_resource
import logging


class wizard(models.TransientModel):
    _name = 'nh_product_move_report.wizard'

    product_id = fields.Many2one('product.product', string="Product", required=True)
    start_date = fields.Date(string="Start Date", default=fields.Date.today, required=True)
    end_date = fields.Date(string="End Date", default=fields.Date.today, required=True)
    branch_id = fields.Many2one('res.branch',string="Branch", required=True)
    warehouse_id = fields.Many2one('stock.warehouse', string="Warehouse", required=True)
    location_ids = fields.Many2many('stock.location', string="Locations")
    include_virtual_locs = fields.Boolean(string="Include Virtual Locations", default=True)

    file = fields.Binary('File', readonly=True)
    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')
    name = fields.Char(string='File name', readonly=True)

    @api.onchange("branch_id")
    def _get_warehouse_domain(self):
        """
        This method is for changing the domain of the location once the warehouse changes
        :return:

        """
        logging.info ("warehouse have changed")
        if self.branch_id:
            logging.info("The branch is "+self.branch_id.name)

            warehouse_domain = self.env['stock.warehouse'].search([('branch_id', '=', self.branch_id.id)])
            logging.info("IDS are " + str(warehouse_domain.ids))

            return {'domain': {'warehouse_id': [('id', 'in', warehouse_domain.ids)]}, 'value': {'warehouse_id': None}}

    @api.onchange("warehouse_id", "include_virtual_locs")
    def _get_location_domain(self):
        """
        This method is for changing the domain of the location once the warehouse changes
        :return:
        """
        if self.warehouse_id:
            loc_domain = []
            if self.include_virtual_locs:
                loc_domain = self.env['stock.location'].search(
                    [('location_id', '=', self.warehouse_id.view_location_id.id)])
            else:
                loc_domain = self.env['stock.location'].search(
                    ['&', ('location_id', '=', self.warehouse_id.view_location_id.id), ('usage', '=', 'internal')])
            ids = []
            for loc in loc_domain:
                ids.append(loc.id)
            return {'domain': {'location_ids': [('id', 'in', ids)]}, 'value': {'location_ids': None}}

    @api.multi
    def get_moves(self):
        """
        The methods is for getting the move lines organised by location
        :return:
        """
        result = []
        locations = self.location_ids
        if not locations:
            locations = self.env['stock.location'].search([('location_id', '=', self.warehouse_id.view_location_id.id)])

        moves_locs = self.env['stock.move.line'].search(['&', ('product_id', '=', self.product_id.id),
                                                         '&', ('date', '<=', self.end_date),
                                                         '&', ('date', '>=', self.start_date),
                                                         ('state', 'in', ['done', ])])
        for loc in locations:
            result_loc = {'location': loc.display_name,
                          'location_moves': [],
                          'initial_qty': self.product_id.with_context(
                              {'to_date': self.start_date + " 00:00:00", 'location': loc.id}).qty_available,

                          'final_qty': self.product_id.with_context(
                              {'to_date': self.end_date + " 23:59:59", 'location': loc.id}).qty_available}

            for move in moves_locs:
                if self.check_loc_child_of_loc(loc, move.location_id) or self.check_loc_child_of_loc(loc, move.location_dest_id):

                    date_time_obj = datetime.strptime(move.write_date + ".0", '%Y-%m-%d %H:%M:%S.%f')
                    temp_mv = {
                        'running_balance': self.product_id.with_context(
                            {
                                'to_date': (date_time_obj + timedelta(seconds=1)).strftime("%Y-%m-%d %H:%M:%S"),
                                'location': loc.id
                            }).qty_available,
                        'date': date_time_obj.strftime("%A %d. %B %Y %H:%M:%S"),
                        'provenance': move.location_id.display_name,
                        'destination': move.location_dest_id.display_name}

                    if move.move_id.partner_id:
                        temp_mv['partner'] = move.move_id.partner_id.name
                    else:
                        temp_mv['partner'] = ''
                    temp_mv['reference'] = move.reference

                    """
                        ici je choisis ou mettre la quantité traitéé, dans inward ou dans outward.
                        je dis que si la source est source de l'emplacement en cours de traitement alors c'est un outward
                        sinon c'est in inward
                        qu'en est-il des mouvement internes? car ici les deux conditions sont vraies
                    """
                    if self.check_loc_child_of_loc(loc, move.location_id):
                        temp_mv['outward'] = move.qty_done
                        temp_mv['inward'] = ''
                    else:
                        temp_mv['inward'] = move.qty_done
                        temp_mv['outward'] = ''
                    temp_mv['lot_number'] = move.lot_id.name
                    if move.lot_id.life_date:
                        temp_mv['life_date'] = move.lot_id.life_date
                    else:
                        temp_mv['life_date'] = ''
                    result_loc['location_moves'].append(temp_mv)

            if not result_loc['location_moves']:
                continue
            result.append(result_loc)

        return result

    def check_loc_child_of_loc(self, parent, child):
        """
        This method returns true in the location 'parent' is really the father of the location 'child' or equal to it and false if not
        :param parent:
        :param child:
        :return:
        """
        if parent.parent_left < child.parent_left and parent.parent_left < child.parent_right and parent.parent_right > child.parent_left and parent.parent_right > child.parent_right:
            return True
        if parent.id == child.id:
            return True
        return False

    @api.multi
    def print_pdf(self):
        datas = {
            'branch': self.branch_id.name,
            'warehouse': '{}/{}'.format(self.warehouse_id.name, self.warehouse_id.code),
            'product_name': self.product_id.product_tmpl_id.name,
            'uom': self.product_id.product_tmpl_id.uom_id.name,
            'category': self.product_id.product_tmpl_id.categ_id.name,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'group_moves': self.get_moves()
        }

        return {
            'type': 'ir.actions.report',
            'name': 'nh_product_move_report.report',
            'res_model': 'report.nh_product_move_report.report',
            'model': 'report.nh_product_move_report.report',
            'report_type': 'qweb-pdf',
            'report_name': 'nh_product_move_report.report',
            'data': datas,
        }

    @api.multi
    def generate_excel(self):
        datas = {
            'branch': self.branch_id.name,
            'warehouse': '{}/{}'.format(self.warehouse_id.name, self.warehouse_id.code),
            'product_name': self.product_id.product_tmpl_id.name,
            'uom': self.product_id.product_tmpl_id.uom_id.name,
            'category': self.product_id.product_tmpl_id.categ_id.name,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'group_moves': self.get_moves()
        }

        path = get_module_resource('nh_product_move_report', 'static/template/product_moves_report.xlsx')
        xfile = openpyxl.load_workbook(path)
        sheet = xfile['Rapport']
        sheet['E5'] = 'From {} To {}'.format(datas['start_date'], datas['end_date'])
        sheet['B8'] = 'Branch : {}'.format(datas['branch'])
        sheet['B9'] = 'Warehouse : {}'.format(datas['warehouse'])
        sheet['E8'] = 'Product Name : {}'.format(datas['product_name'])
        sheet['E9'] = 'Category : {}'.format(datas['category'])
        sheet['H8'] = 'Unity of Measure : {}'.format(datas['uom'])

        group_moves = datas['group_moves']

        cols = [['A', 'date', 'DATE'], ['B', 'reference', 'REFERENCE'], ['C', 'provenance', 'PROVENANCE'],
                ['D', 'destination', 'DESTINATION'],
                ['E', 'partner', 'PARTENAIRE'], ['F', 'lot_number', 'NUMERO DE LOT'],
                ['G', 'life_date', 'DATE DE PEREMPTION'], ['H', 'inward', 'ENTREE'],
                ['I', 'outward', 'SORTIE'], ['J', 'running_balance', 'QUANTITE COURANTE'], ['K', '', 'OBSERVATION']]

        row_loc_start = 12
        for loc in group_moves:
            sheet['A' + str(row_loc_start)] = 'Location : {}'.format(loc['location'])
            for j in range(len(cols)):
                sheet[cols[j][0] + str(row_loc_start + 1)] = cols[j][2]
            sheet['A' + str(row_loc_start + 2)] = 'Initial Quantity'
            sheet['J' + str(row_loc_start + 2)] = str(loc['initial_qty'])

            moves = loc['location_moves']
            for i in range(len(moves)):
                for col in cols[:-1]:
                    sheet[col[0] + str(i + row_loc_start + 3)] = moves[i][col[1]]
            sheet['A' + str(i + row_loc_start + 4)] = 'Final Quantity'
            sheet['J' + str(i + row_loc_start + 4)] = str(loc['final_qty'])
            row_loc_start = i + row_loc_start + 7

        current_date = time.strftime("%Y_%m_%d")
        self.name = u'PRODUCT_MOVES_REPORT-' + u'V-' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ".xlsx"
        chemin = get_module_resource('nh_product_move_report', 'static/created_excel_reports', '')
        nomFichier = chemin + '_' + str(current_date) + '.xlsx'
        xfile.save(nomFichier)

        with open(nomFichier, "rb") as f:
            encodedFile = base64.b64encode(f.read())

        data = encodedFile
        self.write(
            {
                'state': 'get',
                'file': data,
                'name': self.name,
            }
        )

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'nh_product_move_report.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }

    @api.constrains('start_date', 'end_date')
    def _check_start_end(self):
        """
        The method is to ensure that the start date is lesser than the end date
        :return:
        """
        for r in self:
            if r.end_date < r.start_date:
                raise exceptions.ValidationError(_("The Start Date should be lower or equal to the End Date"))
