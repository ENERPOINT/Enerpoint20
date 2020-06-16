# -*- coding: utf-8 -*-
##############################################################################
#
#    ODOO Open Source Management Solution
#
#    ODOO Addon module by Sprintit Ltd
#    Copyright (C) 2019 Sprintit Ltd (<http://sprintit.fi>).
#
##############################################################################
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools import float_compare
from odoo import models, fields, api, _


class Product(models.Model):
    _inherit = "product.product"

    def get_incoming_picking(self, lot_id, owner_id, package_id,
                             from_date=False, to_date=False):
        domain_quant_loc, domain_move_in_loc, domain_move_out_loc = self._get_domain_locations()
        domain_quant = [('product_id', 'in', self.ids)] + domain_quant_loc
        dates_in_the_past = False
        # only to_date as to_date will correspond to qty_available
        to_date = fields.Datetime.to_datetime(to_date)
        if to_date and to_date < fields.Datetime.now():
            dates_in_the_past = True

        domain_move_in = [('product_id', 'in', self.ids)] + domain_move_in_loc
        if lot_id is not None:
            domain_quant += [('lot_id', '=', lot_id)]
        if owner_id is not None:
            domain_quant += [('owner_id', '=', owner_id)]
            domain_move_in += [('restrict_partner_id', '=', owner_id)]
        if package_id is not None:
            domain_quant += [('package_id', '=', package_id)]
        if dates_in_the_past:
            domain_move_in_done = list(domain_move_in)
        if from_date:
            domain_move_in += [('date', '>=', from_date)]
        if to_date:
            domain_move_in += [('date', '<=', to_date)]

        Move = self.env['stock.move']
        Quant = self.env['stock.quant']
        domain_move_in_todo = [('state', 'in', (
            'waiting', 'confirmed', 'assigned',
            'partially_available'))] + domain_move_in

        moves_in_res = dict(
            (item['product_id'][0], item['product_qty']) for item in
            Move.read_group(domain_move_in_todo, ['product_id', 'product_qty'],
                            ['product_id'], orderby='id'))
        moves_in = Move.search(
            domain_move_in_todo, order='date_expected', limit=1)
        nearest_picking_qty = (False, 0)
        if len(moves_in) >= 1:
            nearest_picking_qty = (moves_in[0].picking_id, moves_in[
                0].product_uom_qty)

        res = dict()
        for product in self.with_context(prefetch_fields=False):
            product_id = product.id
            res[product_id] = {'nearest_picking': nearest_picking_qty}
        return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_uom_qty', 'product_uom', 'route_id')
    def _onchange_product_id_check_availability(self):
        if not self.product_id or not self.product_uom_qty or not self.product_uom:
            self.product_packaging = False
            return {}
        if self.product_id.type == 'product':
            precision = self.env['decimal.precision'].precision_get(
                'Product Unit of Measure')
            product = self.product_id.with_context(
                warehouse=self.order_id.warehouse_id.id,
                lang=self.order_id.partner_id.lang or self.env.user.lang or 'en_US'
            )
            product_qty = self.product_uom._compute_quantity(
                self.product_uom_qty, self.product_id.uom_id)
            if float_compare(
                    product.qty_available - product.outgoing_qty,
                    product_qty,
                    precision_digits=precision) == -1:
                is_available = self._check_routing()
                if not is_available:
                    message = _(
                        'You plan to sell %s %s of %s but you only have %s %s available in %s warehouse.') % \
                              (self.product_uom_qty, self.product_uom.name,
                               self.product_id.name,
                               product.qty_available - product.outgoing_qty,
                               product.uom_id.name,
                               self.order_id.warehouse_id.name)
                    # We check if some products are available in other warehouses.
                    if float_compare(
                            product.qty_available - product.outgoing_qty,
                            self.product_id.qty_available -
                            self.product_id.outgoing_qty,
                            precision_digits=precision) == -1:
                        message += _(
                            '\nThere are %s %s available across all warehouses.\n\n') % \
                                   (self.product_id.qty_available -
                                    self.product_id.outgoing_qty,
                                    product.uom_id.name)
                        for warehouse in self.env['stock.warehouse'].search(
                                []):
                            quantity = self.product_id.with_context(
                                warehouse=warehouse.id).qty_available
                            quantity -= self.product_id.with_context(
                                warehouse=warehouse.id).outgoing_qty
                            if quantity > 0:
                                message += "%s: %s %s\n" % (
                                    warehouse.name, quantity,
                                    self.product_id.uom_id.name)
                    nearest_picking = self.product_id.get_incoming_picking(
                        self._context.get('lot_id'),
                        self._context.get('owner_id'),
                        self._context.get('package_id'),
                        self._context.get('from_date'),
                        self._context.get('to_date'))
                    nearest_picking, picking_qty = nearest_picking.get(
                        self.product_id.id, {}).get('nearest_picking',
                                                    (False, 0))
                    user_lang = self.env['res.lang'].sudo().search([
                        ('code', '=', self.env.user.lang)])
                    scheduled_date = nearest_picking and \
                                     nearest_picking.scheduled_date or ''
                    if user_lang and scheduled_date:
                        scheduled_date = nearest_picking.scheduled_date.strftime(
                            '%s %s' % (
                                user_lang.date_format, user_lang.time_format
                            ))

                    message += _(
                        "\n\n%s: %s %s\n%s: %s %s\n%s: %s %s\n%s: %s %s\n%s: "
                        "%s" % (
                            'Required QTY', self.product_uom_qty,
                            self.product_id.uom_id.name,
                            'On Hand QTY', self.product_id.qty_available,
                            self.product_id.uom_id.name,
                            'Available QTY', self.product_id.qty_available -
                            self.product_id.outgoing_qty,
                            self.product_id.uom_id.name,
                            'Total Incoming QTY',
                            self.product_id.incoming_qty,
                            self.product_id.uom_id.name,
                            'Next Incoming Date & QTY', scheduled_date and
                            '%s ( %s %s )' % (
                                scheduled_date,
                                picking_qty,
                                self.product_id.uom_id.name) or
                            'No Incoming Order'
                        ))

                    warning_mess = {
                        'title': _('Not enough inventory!'),
                        'message': message
                    }
                    return {'warning': warning_mess}
        return {}
