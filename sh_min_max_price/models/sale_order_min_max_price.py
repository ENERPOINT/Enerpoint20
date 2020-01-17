# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields,models,api
from odoo.exceptions import UserError

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    pro_min_sale_price = fields.Float("Precio de venta mínimo")
    pro_max_sale_price = fields.Float("Precio de venta máximo")

#class ProductProduct(models.Model):
#    _inherit = 'product.product'
#    
#    pro_min_sale_price = fields.Float("Minimum Sale Price")
#    pro_max_sale_price = fields.Float("Maximum Sale Price")
        
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    pro_min_sale_price = fields.Float(related="product_id.pro_min_sale_price",string="Precio mínimo",readonly=True)
    pro_max_sale_price = fields.Float(related="product_id.pro_max_sale_price",string="Precio máximo",readonly=True)

    @api.onchange('product_id')
    def product_id_change(self): 
        
        if self.product_id:        
            res = super(SaleOrderLine,self).product_id_change()
            
            self.pro_min_sale_price = self.product_id.pro_min_sale_price
            self.pro_max_sale_price = self.product_id.pro_max_sale_price
            
            return res

    @api.onchange('price_unit')
    def product_price_change(self):
 
        if self.price_unit :
                  
            if (self.pro_min_sale_price > 0 and  self.price_unit < self.pro_min_sale_price ) or (self.pro_max_sale_price > 0 and self.price_unit > self.pro_max_sale_price ):
                self._cr.commit()  
                warning_mess = {
                    'message' : ('El precio de venta debe estar entre ' + str(self.pro_min_sale_price ) + " - " + str(self.pro_max_sale_price) + '.'),
                    'title': "Warning" 
                }
                return {'warning': warning_mess}         

class SaleOrder(models.Model):
    _inherit='sale.order'
    
    def _action_confirm(self):     
        
        res = super(SaleOrder,self)._action_confirm()
        
        if self and self.order_line:
            for rec in self.order_line:
                
                if rec.price_unit :            
                    if (rec.pro_min_sale_price > 0 and rec.price_unit < rec.pro_min_sale_price ) or (rec.pro_max_sale_price > 0 and rec.price_unit > rec.pro_max_sale_price):
                        
                        allow_price = self.user_has_groups('sh_min_max_price.group_sale_order_product_price')
                        
                        if not allow_price:
                            raise UserError("El precio de la venta debe encontrarse entre los precios mínimos y máximos")        
                                                    
        return res
