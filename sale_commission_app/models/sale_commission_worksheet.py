# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from datetime import datetime,date
from odoo.http import request
from odoo.exceptions import UserError, ValidationError

class sale_commission_worksheet(models.Model):
	_name ="sale.commission.worksheet"
	_description = "Create the Worksheet as per the Commmission Records"

	name = fields.Char('',readonly=True)
	sale_member = fields.Many2one('res.users', string='Users', required=True)
	partner_id = fields.Many2one('res.partner', string='Partner', required=True)
	start_date = fields.Date(string="Start Date")
	company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
	end_date = fields.Date(string="End Date")
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
		partner_id = self.partner_id
		account_invoice_id = account_invoice.create({
				'partner_id':partner_id.id,
				'type':'in_invoice',
				'currency_id':self.currency.id,
				'user_id':self.sale_member.id,
		})
		order_lines = []
		for line in self.sale_commission_line:
			order_lines.append((0, 0, {
				'move_id':account_invoice_id.id,
				'product_id':line.product_id.id,
				'account_id':line.product_id.categ_id.property_account_income_categ_id.id,
				'name':line.product_id.name,
				'price_unit':line.amount
			}))
		account_invoice_id.write({'invoice_line_ids': order_lines})
		self.write({'state':'invoiced'})



	def cancel_button(self):
		self.write({'state':'draft'})


	@api.depends('currency','sale_commission_line.amount')
	def _onchange_currency_id(self):
		total_amount = []
		for order in self:
			for lines in order.sale_commission_line:
				amount = lines.currency._convert(lines.amount, order.currency, order.company_id, fields.Date.today())
				lines.amount_in_currency = amount > 0 and amount or 0.0
				lines.source_currency = order.currency.id
				total_amount.append(lines.amount_in_currency)
			order.commission_amount = sum(total_amount)

	@api.onchange('sale_member','start_date','end_date','commission_invoice_name')
	def _onchange_product_member(self):
		company = self.company_id
		if not self.start_date and not self.end_date and not self.commission_invoice_name:
			domain = [('member_id','=',self.sale_member.id)]
		elif self.start_date and self.end_date and not self.commission_invoice_name:
			domain = [('member_id','=',self.sale_member.id),('create_date','>=',self.start_date),('create_date','<=',self.end_date)]
		elif self.start_date and not self.commission_invoice_name:
			domain = [('member_id','=',self.sale_member.id),('create_date','>=',self.start_date)]
		elif self.commission_invoice_name:
			domain = [('member_id','=',self.sale_member.id),('source_document','=',self.commission_invoice_name.name)]
		else:
			domain = [('member_id','=',self.sale_member.id),('create_date','>=',self.start_date),('create_date','<=',self.end_date), ('source_document','=',self.commission_invoice_name.number)]
		sale_commission = self.env['sale.commission.line'].sudo().search(domain)
		commission_line = self.env['commission.line']
		date_order = fields.Datetime.now()
		order_lines = [(5, 0, 0)]
		date = request.env.context.get('date') or fields.Date.today()
		for record in sale_commission:
			data = self._compute_line_data_for_record_change(record)
			currency_amount = self.currency._convert(record.amount_total, record.currency_id, company, date)
			data.update({
						'product_id' : record.product_id.id,
						'date':record.create_date,
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
	product_id = fields.Many2one('product.product','Product')

	@api.onchange('source_currency','amount')
	def _onchange_currency(self):
		company = self.env.company
		for line in self:
			if line.source_currency:
				amount = line.currency._convert(line.amount, line.source_currency, company, fields.Date.today())
				line.amount_in_currency = amount > 0 and amount or 0.0

