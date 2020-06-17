# -*- coding: utf-8 -*-

from odoo import models, fields
from datetime import date

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    last_currency_id = fields.Many2one('res.currency', 'Last Currency Set', copy=False)
    
    def write(self, vals):
        new_currency_id = vals.get('currency_id')
        if new_currency_id:
            mv_old_currency_dict = {}
            for move in self:
                if new_currency_id != move.currency_id.id:
                    if move.currency_id not in mv_old_currency_dict:
                        mv_old_currency_dict.update({move.currency_id: move})
                    else:
                        mv_old_currency_dict[move.currency_id] += move
            
        res = super(AccountMove, self).write(vals)
        if new_currency_id and mv_old_currency_dict:
            for currency, moves in mv_old_currency_dict.items():
                super(AccountMove, moves).write({'last_currency_id': currency.id})
        return res
    
    def action_actualizar_precios(self):
        if self.currency_id and self.last_currency_id and self.currency_id.id != self.last_currency_id.id:
            from_currency = self.last_currency_id
            to_currency = self.currency_id
            company = self.company_id
            #today_date = date.today()
            rate_invoice_date = self.invoice_date
            update_lines = []
            
            for line in self.invoice_line_ids:
                converted_unit_price = from_currency._convert(line.price_unit, to_currency, company, rate_invoice_date)
                update_lines.append((1, line.id, {'price_unit': converted_unit_price}))
            self.write({'invoice_line_ids': update_lines})
        return True
    
    