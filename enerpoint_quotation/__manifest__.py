# -*- coding: utf-8 -*-
##############################################################################
#                 @author Duvan Zavaleta
#
##############################################################################

{
    'name': 'Enerpoint Quotation',
    'version': '13.1',
    'description': ''' Change the quotation format
    ''',
    'category': 'Sales',
    'author': 'IT Admin',
    'website': 'www.itadmin.com.mx',
    'depends': [
        'base',
        'sale',
    ],
    'data': [
        'report/enerpoint_quotation.xml',
    ],
    'application': False,
    'installable': True,
    'price': 0.00,
    'currency': 'USD',
    'license': 'OPL-1',	
}
