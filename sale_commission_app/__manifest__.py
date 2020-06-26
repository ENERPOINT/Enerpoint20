
# -*- coding: utf-8 -*-

{
    "name" : "Sales commission based on Target Amount App",
    "author": "Edge Technologies",
    "version" : "13.0.1.2",
    "live_test_url":'https://youtu.be/G14Y547coGE',
    "images":["static/description/main_screenshot.png"],
    'summary': 'Sale commission based on Target Sale order commission based on Target Sales order commission based on Target commission on sales commission based on invoice Commission based on target sale amount targeted amount sales commission based on payment commission',
    "description": """ This module contains Information about Commission On Sale/Invoice/Payment. """,
    "license" : "OPL-1",
    "depends" : ['base','sale','sale_management','account'],

    "data": [
             'security/ir.model.access.csv',
             'views/sale_commision_view.xml',
             'views/account_payment.xml',
             'views/sale_commision_worksheet.xml',
             'report/sale_commision_report.xml',
             'views/sale_commission_line_view.xml',
             'report/worksheet_template.xml'
            ],

    "auto_install": False,
    "installable": True,
    "price": 45,
    "currency": 'EUR',
    "category" : "Sales",
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
