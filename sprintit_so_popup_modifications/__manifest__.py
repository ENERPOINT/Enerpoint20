# -*- coding: utf-8 -*-
##############################################################################
#
#    ODOO Open Source Management Solution
#
#    ODOO Addon module by Sprintit Ltd
#    Copyright (C) 2019 Sprintit Ltd (<http://sprintit.fi>).
#
##############################################################################


{
    'name': 'SprintIT SO popup modifications',
    'version': '0.1',
    'license': 'LGPL-3',
    'category': 'Stock',
    'summary': """Module adds details on warning popup for not enough inventory.""",
    'description': 'Not enough inventory popup customization',
    'author': 'SprintIT Ltd., Kalpesh Gajera',
    'maintainer': 'SprintIT Ltd.',
    "website" : "https://sprintit.fi/in-english",
    'depends': ['sale_stock'
    ],
    'data': [
    ],
    'installable': True,
    'auto_install': False,
    # for Odoo Appstore
    'images': ['static/description/cover.jpg',],
    'currency': 'EUR',
    'price': 0.0,
 }

