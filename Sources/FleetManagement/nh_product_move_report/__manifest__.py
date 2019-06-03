# -*- coding: utf-8 -*-
{
    'name': "nh_product_move_report",

    'summary': """ Report of stock moves for a product""",

    'description': """
        This a module that allows to export a report of stock moves of a product.
        \nIt takes as parameters:
            - The date from which we want to see the stock moves
            - The date on which we want to stop seeing the stock moves
    """,

    'author': "IT Services",
    'website': "http://www.its-nh.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Inventory',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'branch'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'reports/reports.xml',
        'reports/layout.xml',

        'reports/reports_templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}