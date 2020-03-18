# -*- coding: utf-8 -*-

{
    'name' : 'Odoo Digital Signature for Sales, Purchase, Invoices and Inventory',
    'author': "Edge Technologies",
    'version' : '13.0.1.0',
    'live_test_url':'https://youtu.be/J_HwVQRp7_0',
    'images':['static/description/main_screenshot.png'],
    'summary' : 'Digital Signature Documents helps to add Digital Sign on Sales, Digital Signature on Purchase, Digital Signature on Invoices And Digital Signature on Inventory along with Digital Sign on PDF reports for all in one Digital sign',
    'description' : """
                        This module helps to Gives Digital Signature in Sales, Purchase,
                        Invoices and Inventory, including PDF Reports,According to Given Configuration.
    """,
    'depends': ['base','sale_management','purchase','account','stock','web_digital_sign'],
    "license" : "AGPL-3",
    'data': [
        'views/sale_digital_signature.xml',
        'views/purchase_digital_signature.xml',
        'views/inventory_digital_signature.xml',
        'views/invoice_digital_signature.xml',
        'reports/sale_digital_signature.xml',
        'reports/purchase_digital_signature.xml',
        'reports/inventory_digital_signature.xml',
        'reports/invoice_digital_signature.xml',
    ],
    'installable' : True,
    'auto_install' : False,
    'price': 8.00,
    'currency': 'EUR',
    'category' : 'Extra Tools',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
