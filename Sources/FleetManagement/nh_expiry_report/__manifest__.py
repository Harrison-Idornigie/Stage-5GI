# -*- coding: utf-8 -*-
{
    'name': "nh_expiry_report",

    'summary': """
        Report for expired articles
    """,

    'description': """
        This is a module that allows to print a report of Articles that will expire in a given time
        \nIt takes as parameters:
            - The Branch where we are looking for articles
            - The Warehouse where we are looking for articles
            - Optionaly the locations where we are looking for articles (if not given the module takes all the locations
            of the warehouse selected)  
    """,

    'author': "IT Services",
    'website': "http://www.its-nh.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Inventory',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock','branch'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        #'views/templates.xml',
        'reports/reports.xml',
        'reports/reports_templates.xml',
        'reports/layout.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}