# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Odoo Website Product Attachments(Documents)',
    'summary': """App allow customer to Download Product's Documents/Attachments on website shop Documents/Attachments Product Documents on Shop Display Product Attachments on Shop multiple attachments User Guides upload file attachments upload Documents document attached""" ,
    'category': 'eCommerce',
    'version': '13.0.0.1',
    "price": 8,
    "currency": 'EUR',
    'author': 'BrowseInfo',
    'description': """
        This Module is allow customer to Download Product's Documents/Attachments on website.
        Website Product Documents
        Product Documents on Website Shop Product Attachments on Website Shop Product Documents/Attachments on Website Shop
        Product Documents on Shop Product Attachments on Shop Product Documents/Attachments on Shop.
        Show Product Documents on Website Shop Show Product Attachments on Website Shop Show Product Documents/Attachments on Website Shop
        Show Product Documents on Shop Show Product Attachments on Shop Show Product Documents/Attachments on Shop.
        Visible Product Documents on Website Shop visible Product Attachments on Website Shop visible Product Documents/Attachments on Website Shop
        visible Product Documents on Shop visible Product Attachments on Shop visible Product Documents/Attachments on Shop.
        Show Product Document on Website Shop Show Product Attachment on Website Shop,Show Product Document/Attachment on Website Shop
        Show Product Document on Shop Show Product Attachment on Shop Show Product Document/Attachment on Shop.
        Visible Product Document on Website Shop visible Product Attachment on Website Shop,visible Product Document/Attachment on Website Shop
        visible Product Document on Shop visible Product Attachment on Shop visible Product Document/Attachment on Shop.
        Product Document on Website Shop Product Attachment on Website Shop Product Document/Attachment on Website Shop
        Product Document on Shop Product Attachment on Shop Product Document/Attachment on Shop
        Display Product Documents on Website Shop Display Product Attachments on Website Shop,Product Documents/Attachments on Website Shop
        Display Product Documents on Shop Display Product Attachments on Shop Display Product Documents/Attachments on Shop
        Display Product Document on Website Shop Display Product Attachment on Website Shop Product Document/Attachment on Website Shop
        Display Product Document on Shop Display Product Attachment on Shop Display Product Document/Attachment on Shop     

Product Attachments
 Product Documents
 item Attachments(Documents
product category document
document attached
add/show multiple attachments on website
add multiple attachments on website
multiple attachments
 User Guides
 pdf User Guides
 warning 
 Attachments
 upload file attchements
 upload files 


""",
    'depends': ['website','website_sale','product','sale_management'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_attachment.xml',
        'views/template.xml',
    ],
    'application': True,
    'installable': True,
    'live_test_url':'https://youtu.be/QWtARa2BjgU',
    "images":["static/description/Banner.png"],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
