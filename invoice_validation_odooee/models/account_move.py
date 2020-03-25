# -*- coding: utf-8 -*-

from odoo import _, models
from odoo.addons.l10n_mx_edi.models.account_invoice import AccountMove
from odoo.exceptions import UserError

class AccountMoveMX(models.Model):
    _inherit = 'account.move'
    
    def post(self):
        return super(AccountMove, self).post()
    
    def action_generar_cfdi(self):
        for move in self.filtered(lambda move: move.l10n_mx_edi_is_required()):

            # Line having a negative amount is not allowed.
            for line in move.invoice_line_ids:
                if line.price_subtotal < 0:
                    raise UserError(_("Invoice lines having a negative amount are not allowed to generate the CFDI. Please create a credit note instead."))

            date_mx = self.env['l10n_mx_edi.certificate'].sudo().get_mx_current_datetime()
            if not move.invoice_date:
                move.invoice_date = date_mx.date()
                move.with_context(
                    check_move_validity=False)._onchange_invoice_date()
            if not move.l10n_mx_edi_time_invoice:
                move.l10n_mx_edi_time_invoice = date_mx
            move._l10n_mx_edi_update_hour_timezone()

        # Generates the cfdi attachments for mexican companies when validated.
        version = self.l10n_mx_edi_get_pac_version().replace('.', '-')
        trans_field = 'transaction_ids' in self._fields
        for move in self.filtered(lambda move: move.l10n_mx_edi_is_required()):
            if move.type == 'out_refund' and move.reversed_entry_id and not move.reversed_entry_id.l10n_mx_edi_cfdi_uuid:
                move.message_post(
                    body='<p style="color:red">' + _(
                        'The invoice related has no valid fiscal folio. For this '
                        'reason, this refund didn\'t generate a fiscal document.') + '</p>',
                    subtype='account.mt_invoice_validated')
                continue

            move.l10n_mx_edi_cfdi_name = ('%s-%s-MX-Invoice-%s.xml' % (move.journal_id.code, move.invoice_payment_ref, version)).replace('/', '')
            subscription = 'subscription_id' in move.invoice_line_ids._fields and move.invoice_line_ids.filtered('subscription_id')
            if subscription or (trans_field and move.mapped('transaction_ids.payment_id')):
                move = move.with_context(disable_after_commit=True)
            move._l10n_mx_edi_retry()
        
        return True
    
        