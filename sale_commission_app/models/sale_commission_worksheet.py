# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from datetime import datetime,date
from odoo.http import request
from odoo.exceptions import UserError, ValidationError

class sale_commission_worksheet(models.Model):
	_name ="sale.commission.worksheet"
	_description = "Create the Worksheet as per the Commmission Records"

	name = fields.Char('',readonly=True)
	sale_member = fields.Many2one('res.users', string='Partner', required=True)
	start_date = fields.Date(string="Start Date")
	company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
	end_date = fields.Date(string="End Date")
	commission_product_name = fields.Many2one('product.product', string="Product", required=True)
	commission_amount = fields.Monetary(string="Total Amount",currency_field="currency", compute="_onchange_currency_id")
	currency = fields.Many2one('res.currency', string="Currency", default=lambda self: self.env.user.company_id.currency_id ,required=True)
	commission_invoice_name = fields.Many2one('account.move', string="Invoice")
	is_commission_paid = fields.Boolean(string="Is Commission Paid?")
	state = fields.Selection([('draft','Draft'),('invoiced','Invoiced')],string="state",default='draft')
	sale_commission_line = fields.One2many('commission.line','sale_commission_worksheet')

	@api.model
	def create(self,vals):
		vals['name'] = self.env['ir.sequence'].next_by_code('sequence.code')
		res = super(sale_commission_worksheet, self).create(vals)
		return res

	def create_invoice_bill(self):
		if not self.sale_commission_line:
			raise ValidationError(_('No Invoice Line'))
		account_invoice = self.env['account.move']
		name = self.env['res.partner'].search([('name','=', self.sale_member.name)])
		vendor = account_invoice.create({'partner_id':name.id,
								'type':'in_invoice',
								'currency_id':self.currency.id,
								})
		account_move = self.env['account.move.line'].create({'move_id':vendor.id,
						 'product_id':self.commission_product_name.id,
						 'account_id':self.commission_product_name.categ_id.property_account_income_categ_id.id,
						 'name':self.commission_product_name.name,
						 'price_unit':self.commission_amount,
						 'price_subtotal':self.commission_amount,
						 })
		for lines in vendor.invoice_line_ids:
			subtotal = lines._get_price_total_and_subtotal(lines.price_unit, lines.quantity, lines.discount, self.currency, self.commission_product_name, name.id, lines.tax_ids, lines.move_id.type)
			lines.update({'price_subtotal':subtotal.get('price_subtotal')})
			vendor.update({'amount_untaxed':lines.price_subtotal,
							'amount_total':lines.price_subtotal})
		self.write({'state':'invoiced'})

	def cancel_button(self):
		self.write({'state':'draft'})

	@api.onchange('sale_commission_line')
	def _onchange_commission(self):
		total_amount = []
		for lines in self.sale_commission_line:
			if lines.state == 'draft':
				total_amount.append(lines.amount_in_currency)
		self.commission_amount = sum(total_amount)

	@api.depends('currency')
	def _onchange_currency_id(self):
		total_amount = []
		company = self.env.company
		for order in self:
			for lines in order.sale_commission_line:
				amount = lines.currency._convert(lines.amount, order.currency, company, fields.Date.today())
				lines.amount_in_currency = amount > 0 and amount or 0.0
				lines.source_currency = order.currency.id
				if lines.state == 'draft':
					total_amount.append(lines.amount_in_currency)
			order.commission_amount = sum(total_amount)

	@api.onchange('sale_member','commission_product_name','start_date','end_date','commission_invoice_name')
	def _onchange_product_member(self):
		company = self.env.company
		if not self.start_date and not self.end_date and not self.commission_invoice_name:
			domain = [('member_id','=',self.sale_member.name),('product_id','=',self.commission_product_name.id)]
		elif self.start_date and self.end_date and not self.commission_invoice_name:
			domain = [('member_id','=',self.sale_member.name),('product_id','=',self.commission_product_name.id),('create_date','>=',self.start_date),('create_date','<=',self.end_date)]
		elif self.start_date and not self.commission_invoice_name:
			domain = [('member_id','=',self.sale_member.name),('product_id','=',self.commission_product_name.id),('create_date','>=',self.start_date)]
		elif self.commission_invoice_name:
			domain = [('member_id','=',self.sale_member.name),('product_id','=',self.commission_product_name.id),('source_document','=',self.commission_invoice_name.name)]
		else:
			domain = [('member_id','=',self.sale_member.name),('product_id','=',self.commission_product_name.id),('create_date','>=',self.start_date),('create_date','<=',self.end_date), ('source_document','=',self.commission_invoice_name.number)]
		sale_commission = self.env['sale.commission.line'].search(domain)
		commission_line = self.env['commission.line']
		date_order = fields.Datetime.now()
		order_lines = [(5, 0, 0)]
		date = request.env.context.get('date') or fields.Date.today()
		for record in sale_commission:
			data = self._compute_line_data_for_record_change(record)
			currency_amount = self.currency._convert(record.amount_total, record.currency_id, company, date)
			data.update({'date':record.create_date,
						'user_type':record.user_id,
						'amount':currency_amount,
						'currency':record.currency_id,
						'amount_in_currency':currency_amount,
						'source_document':record.source_document,
						'state':record.state})
			order_lines.append((0, 0, data))
		self.sale_commission_line = order_lines

	def _compute_line_data_for_record_change(self, record):
		return {
			'source_currency':record.currency_id,
		}


class commission_line(models.Model):
	_name = "commission.line"
	_description ="Commission Lines of Records"

	date = fields.Date(string='Date')
	user_type = fields.Char(string="User")
	company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
	amount = fields.Monetary(string="Amount",currency_field='currency')
	source_currency = fields.Many2one('res.currency',string="Commission Currency")
	currency = fields.Many2one('res.currency', string="Company Currency", relatable='company_id.currency_id')
	amount_in_currency = fields.Monetary(string="Currency Amount", currency_field="source_currency")
	source_document = fields.Char(string="Source Document")
	state = fields.Char(string="Status")
	is_commission_paid = fields.Boolean(string='Is Commission Paid')
	sale_commission_worksheet= fields.Many2one('sale.commission.worksheet')

	@api.onchange('source_currency','amount')
	def _onchange_currency(self):
		company = self.env.company
		for line in self:
			if line.source_currency:
				amount = line.currency._convert(line.amount, line.source_currency, company, fields.Date.today())
				line.amount_in_currency = amount > 0 and amount or 0.0

