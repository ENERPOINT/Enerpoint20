# -*- coding: utf-8 -*-
{
    'name': 'Precio mínimo y máximo en ventas',
    
    'author' : 'IT Admin',
    
    'website': 'www.itadmin.com.mx',
	
	'support': 'soporte@itadmin.com.mx',
        
    'version': '13.0.1',
    
    'category': 'Sales',
    
    'summary': 'Módulo para precios mínimos y máximos en productos',
    
    'description': """Module""",
    
    'depends': ['sale_management'],
    
    'data': [
        'views/sale_order_min_max_price.xml',
        'data/sale_order_price_group.xml',
        ],
    
    'images': ['static/description/background.png',],              
    
    'auto_install':False,
    'installable':True,
    'application':True,    

    "price": 15,
    "currency": "EUR"        
}
