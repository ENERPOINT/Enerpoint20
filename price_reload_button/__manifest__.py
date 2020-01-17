# -*- coding: utf-8 -*-
##############################################################################
#                 @author Duvan Zavaleta
#
##############################################################################

{
    'name': 'Price Reload Button Module',
    'version': '13.1',
    'description': ''' Update the price according to pricelist
    ''',
    'category': 'sale',
    'author': 'IT Admin',
    'website': 'www.itadmin.com.mx',
    'depends': [
        'sale', 'account'
    ],
    'data': [
        'views/sale_view.xml',
        'views/account_move_view.xml',
    ],
    'application': False,
    'installable': True,
    'price': 0.00,
    'currency': 'USD',
    'license': 'OPL-1',	
}
