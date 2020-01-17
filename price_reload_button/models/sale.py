# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'


    #def unlink(self):
    #    res = super(sale_management, self).unlink()
    #    return self.action_refresh()

    def action_refresh(self):
    	for line in self.mapped('order_line'):
            dict = line._convert_to_write(line.read()[0])
            if 'product_tmpl_id' in line._fields:
                dict['product_tmpl_id'] = line.product_tmpl_id
            line2 = self.env['sale.order.line'].new(dict)
            # Esto aisla los valores cambiados y ejecuta el calculo de nuevo:
            line2.product_uom_change()
            line2._onchange_discount()
            line.write({
                'price_unit': line2.price_unit,
                'discount': line2.discount,
            })