# -*- coding: utf-8 -*-
{
    'name': "nh_analytic_report",

    'summary': """ Analytic Accounting Report""",

    'description': """
        This is a module for printing report of Analytic Accounting during a period. It is possible to use it on a specific account
        or on all the accounts
        \nIt takes as parameters:
            - The start date
            - The end date
            - The set of accounts on which the module should print the accounting (this field is optional), when this field is empty
            the module prints the accounting of all the accounts
    """,

    'author': "IT Services",
    'website': "http://www.its-nh.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Inventory',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'analytic', 'account'],

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