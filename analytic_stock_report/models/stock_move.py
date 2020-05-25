# -*- coding: utf-8 -*-

from odoo import fields, models

#class AnalyticAccount(models.Model):
#    _inherit = 'stock.move'
    
#    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    x_studio_cuenta_analitica = fields.Many2one('account.analytic.account', string='Analytic Account')