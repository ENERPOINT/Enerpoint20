# -*- coding: utf-8 -*-
from odoo import models, api
from datetime import date
from odoo.tools.float_utils import float_round

class ResCurrency(models.Model):
    _inherit = 'res.currency'
    
    @api.model
    def get_usd_currency_rate(self):
        
        currency_exist = self.sudo().search([('name','=','USD')], limit=1)
        rate = 0.0
        if currency_exist:
            rate = float_round(self._get_conversion_rate(currency_exist, self.env.user.company_id.currency_id, self.env.user.company_id, date.today()), precision_digits=2)
            
        return rate 
    
