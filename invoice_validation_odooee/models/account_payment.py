# -*- coding: utf-8 -*-

from odoo import _, models

class AccountPayment(models.Model):
    _inherit = 'account.payment'
    
    def l10n_mx_edi_is_required(self):
        is_to_sign="True"
        for invoice in self.invoice_ids:
            if not invoice.l10n_mx_edi_pac_status or invoice.l10n_mx_edi_pac_status == 'to_sign':
                is_to_sign=False
        if is_to_sign:
            res =super(AccountPayment,self).l10n_mx_edi_is_required()
            return res
        else:
            return False
                        
                
            
            
        
    