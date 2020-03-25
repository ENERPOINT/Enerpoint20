# -*- coding: utf-8 -*-

{
    'name': 'invoice_validation_odooee',
    'summary': '',
    'description': '''
    ''',
    'author': 'IT Admin',
    'version': '13.0.1.0.0',
    'category': 'Accounting',
    'depends': [
        'l10n_mx_edi','account'
    ],
    'data': [
        'views/account_move_view.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'AGPL-3',
}
