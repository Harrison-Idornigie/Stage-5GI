# -*- coding: utf-8 -*-
{
    'name': "Fleet Tracking",
    'version': "1.0",
    'summary': """
        Tracking GPS de flotte automobile
    """,

    'description': """
        Module permettant le control de Flotte Automobile couplé au serveur Traccar.
    """,

    'author': "IT Services",
    'website': "http://www.its-nh.com",
    'category': 'Industries',
    'depends': ['base','fleet'],

    'data': [
        # 'security/ir.model.access.csv',
        'views/templates.xml',
        'views/cron_location_history.xml',
        'views/fleet_vehicle_view.xml',
        'views/real_track_wizard.xml',
        'views/fleet_vehicle_location_history_view.xml',
        'views/fleet_vehicle_location_history_wizard.xml',
        'views/res_config.xml',
        'views/last_location_wizard.xml',
        'views/daily_trip_view.xml',
        'views/daily_trip_wizard.xml',
    ],

    'demo': [
        'demo/demo.xml',
    ],
}