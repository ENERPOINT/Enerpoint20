# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from datetime import datetime,date
from odoo.exceptions import UserError, ValidationError

class SaleCommissionLine(models.Model):
	_name = "sale.commission.line"
	_rec_name = "sales_commission"
	_description = "All the Records of Commission"

	sales_commission = fields.Char("Ref",readonly=True, index=True, default=lambda self: _(''))
	sale_team_id = fields.Many2one('crm.team',string='Sales Team')
	member_id = fields.Char(string='Sales User')
	product_id = fields.Many2one('product.product', string='Product')
	source_document = fields.Char(string="Source Order") 
	amount_total = fields.Monetary(string='Total')
	currency_id = fields.Many2one("res.currency", string="Order Currency")
	user_id = fields.Char(string='Sales User Type')
	state = fields.Selection([('draft','Draft'),('exception','Exception')],default="draft",copy=False)
	create_date = fields.Date('Create Date', default=fields.Date.context_today)

	@api.model
	def create(self,vals):
		vals['sales_commission'] = self.env['ir.sequence'].next_by_code('seq.code')
		res = super(SaleCommissionLine, self).create(vals) 
		return res


class SaleOrder(models.Model):
	_inherit = "sale.order"

	def action_confirm(self):
		res = super(SaleOrder, self).action_confirm()
		product_commission = self.env['sale.commission.line'].search([])
		apply_sale_commission = self.env['ir.config_parameter'].sudo().get_param('sale_commission_app.apply_sale_commission')
		calculation_method = self.env['ir.config_parameter'].sudo().get_param('sale_commission_app.calculation_method')
		if self.env.user.has_group('sale_commission_app.group_show_commission_view'):
			for record in self:
				if apply_sale_commission == 'sales_confirmation':
					if calculation_method == 'product':
						for line in record.order_line:
							for com_lines in line.product_id.product_commission_ids:
								if line.product_id._is_commission:
									if not record.team_id.user_id:
										raise ValidationError(_('Please Define Sale Team Manager as Team Leader in Sales Team'))
									if record.team_id.user_id:
										if line.product_id.account_type == 'fixed_amount':
											if line.price_subtotal >= com_lines.initiate_total and line.price_subtotal <= com_lines.end_total:
												product_commission.create({'product_id':line.product_id.id,
																		   'sale_team_id':record.team_id.id,
																		   'member_id': record.team_id.user_id.name,
																		   'source_document':record.name,
																		   'amount_total':com_lines.manager_commission_amount,
																		   'currency_id':self.env.user.company_id.currency_id.id,
																		   'user_id':'Sales Manager',
																		   })
										if line.product_id.account_type == 'by_percentage':
											percent_amount = (line.price_subtotal * com_lines.sales_manager_commission) / 100
											if line.price_subtotal > com_lines.initiate_total and line.price_subtotal < com_lines.end_total:
												product_commission.create({'product_id':line.product_id.id,
																		   'sale_team_id':record.team_id.id,
																		   'member_id': record.team_id.user_id.name,
																		   'source_document':record.name,
																		   'amount_total':percent_amount,
																		   'currency_id':self.env.user.company_id.currency_id.id,
																		   'user_id':'Sales Manager'
																		   })
									if record.user_id:
										if line.product_id.account_type == 'fixed_amount':
											if line.price_subtotal >= com_lines.initiate_total and line.price_subtotal <= com_lines.end_total:
												product_commission.create({'product_id':line.product_id.id,
																		   'sale_team_id':record.team_id.id,
																		   'member_id': record.user_id.name,
																		   'source_document':record.name,
																		   'amount_total':com_lines.sale_person_commission_amount,
																		   'currency_id':self.env.user.company_id.currency_id.id,
																		   'user_id':'Sales Person',
																		   })
										if line.product_id.account_type == 'by_percentage':
											percent_amount = (line.price_subtotal * com_lines.sales_person_commission) / 100
											if line.price_subtotal >= com_lines.initiate_total and line.price_subtotal <= com_lines.end_total:
												product_commission.create({'product_id':line.product_id.id,
																		   'sale_team_id':record.team_id.id,
																		   'member_id': record.user_id.name,
																		   'source_document':record.name,
																		   'amount_total':percent_amount,
																		   'currency_id':self.env.user.company_id.currency_id.id,
																		   'user_id':'Sales Person'
																		   })

					if calculation_method == 'sales_team':
						for lines in record.order_line:
							for com_lines in lines.product_id:
								for sale_com in record.team_id.sale_team_commission_ids:
									if record.team_id._is_commission:
										if not record.team_id.user_id:
											raise ValidationError(_('Please Define Sale Team Manager as Team Leader in Sales Team'))
										if record.team_id.user_id:
											if record.team_id.account_type == 'fixed_amount':
												if lines.price_subtotal >= sale_com.initiate_total and lines.price_subtotal <= sale_com.end_total:
													product_commission.create({'product_id':lines.product_id.id,
																			   'sale_team_id':record.team_id.id,
																			   'member_id': record.team_id.user_id.name,
																			   'source_document':record.name,
																			   'amount_total':sale_com.manager_commission_amount,
																			   'currency_id':self.env.user.company_id.currency_id.id,
																			   'user_id':'Sales Manager'
																			   })
											if record.team_id.account_type == 'by_percentage':
												percent_amount = (lines.price_subtotal * sale_com.sales_manager_commission) / 100
												if lines.price_subtotal >= sale_com.initiate_total and lines.price_subtotal <= sale_com.end_total:
													product_commission.create({'product_id':lines.product_id.id,
																			   'sale_team_id':record.team_id.id,
																			   'member_id': record.team_id.user_id.name,
																			   'source_document':record.name,
																			   'amount_total':percent_amount,
																			   'currency_id':self.env.user.company_id.currency_id.id,
																			   'user_id':'Sales Manager'
																			   })
										if record.user_id:
											if record.team_id.account_type == 'fixed_amount':
												if lines.price_subtotal >= sale_com.initiate_total and lines.price_subtotal <= sale_com.end_total:
													product_commission.create({'product_id':lines.product_id.id,
																			   'sale_team_id':record.team_id.id,
																			   'member_id': record.user_id.name,
																			   'source_document':record.name,
																			   'amount_total':sale_com.sale_person_commission_amount,
																			   'currency_id':self.env.user.company_id.currency_id.id,
																			   'user_id':'Sales Person'
																			   })
											if record.team_id.account_type == 'by_percentage':
												percent_amount = (lines.price_subtotal * sale_com.sales_person_commission) / 100
												if lines.price_subtotal >= sale_com.initiate_total and lines.price_subtotal <= sale_com.end_total:
													product_commission.create({'product_id':lines.product_id.id,
																			   'sale_team_id':record.team_id.id,
																			   'member_id': record.user_id.name,
																			   'source_document':record.name,
																			   'amount_total':percent_amount,
																			   'currency_id':self.env.user.company_id.currency_id.id,
																			   'user_id':'Sales Person'
																			   })

					if calculation_method == 'product_categ':
						for lines in record.order_line:
							for com_lines in lines.product_id.categ_id.sale_commission_ids:
								if lines.product_id.categ_id._is_commission:
									if not record.team_id.user_id:
										raise ValidationError(_('Please Define Sale Team Manager as Team Leader in Sales Team'))
									if record.team_id.user_id:
										if lines.product_id.categ_id.account_type == 'fixed_amount':
											if lines.price_subtotal >= com_lines.initiate_total and lines.price_subtotal <= com_lines.end_total:
												product_commission.create({'product_id':lines.product_id.id,
																		   'sale_team_id':record.team_id.id,
																		   'member_id': record.team_id.user_id.name,
																		   'source_document':record.name,
																		   'amount_total':com_lines.manager_commission_amount,
																		   'currency_id':self.env.user.company_id.currency_id.id,
																		   'user_id':'Sales Manager'
																		   })
												product_commission.write({'state':'exception'})
										if lines.product_id.categ_id.account_type == 'by_percentage':
											percent_amount = (lines.price_subtotal * com_lines.sales_manager_commission) / 100
											if lines.price_subtotal >= com_lines.initiate_total and lines.price_subtotal <= com_lines.end_total:
												product_commission.create({'product_id':lines.product_id.id,
																		   'sale_team_id':record.team_id.id,
																		   'member_id': record.team_id.user_id.name,
																		   'source_document':record.name,
																		   'amount_total':percent_amount,
																		   'currency_id':self.env.user.company_id.currency_id.id,
																		   'user_id':'Sales Manager'
																		   })
									if record.user_id:
										if lines.product_id.categ_id.account_type == 'fixed_amount':
											if lines.price_subtotal >= com_lines.initiate_total and lines.price_subtotal <= com_lines.end_total:
												product_commission.create({'product_id':lines.product_id.id,
																		   'sale_team_id':record.team_id.id,
																		   'member_id': record.user_id.name,
																		   'source_document':record.name,
																		   'amount_total':com_lines.sale_person_commission_amount,
																		   'currency_id':self.env.user.company_id.currency_id.id,
																		   'user_id':'Sales Person'
																		   })
										if lines.product_id.categ_id.account_type == 'by_percentage':
											percent_amount = (lines.price_subtotal * com_lines.sales_person_commission) / 100
											if lines.price_subtotal >= com_lines.initiate_total and lines.price_subtotal <= com_lines.end_total:
												product_commission.create({'product_id':lines.product_id.id,
																		   'sale_team_id':record.team_id.id,
																		   'member_id': record.user_id.name,
																		   'source_document':record.name,
																		   'amount_total':percent_amount,
																		   'currency_id':self.env.user.company_id.currency_id.id,
																		   'user_id':'Sales Person'
																		   })
				for res in product_commission.search([('source_document','=',record.name)]):
					res.write({'state':'exception'})

		return res

class Invoice(models.Model):
	_inherit = 'account.move'

	source_document = fields.Many2one('sale.commission.line', string="Source Document")

	def action_post(self):
		res = super(Invoice, self).action_post()
		product_commission = self.env['sale.commission.line']
		company = self.env['res.company'].browse(self.env.context.get('company_id')) or self.env.user.company_id
		apply_sale_commission = self.env['ir.config_parameter'].sudo().get_param('sale_commission_app.apply_sale_commission')
		calculation_method = self.env['ir.config_parameter'].sudo().get_param('sale_commission_app.calculation_method')
		apply_sale_commission = self.env['ir.config_parameter'].sudo().get_param('sale_commission_app.apply_sale_commission')
		if self.env.user.has_group('sale_commission_app.group_show_commission_view'):
			for record in self:
				if apply_sale_commission == 'invoice_validate':
					if company.currency_id.id == record.currency_id.id:
						for line in record.invoice_line_ids:
							if calculation_method == 'product':
								if line.product_id._is_commission:
									if not record.team_id.user_id:
										raise ValidationError(_('Please Define Sale Team Manager as Team Leader in Sales Team'))
									if record.team_id.user_id:
										if line.product_id.account_type == 'fixed_amount':
											for com_lines in line.product_id.product_commission_ids:
												if line.price_subtotal >= com_lines.initiate_total and line.price_subtotal <= com_lines.end_total:
													product_commission.create({'product_id':line.product_id.id,
															                   'state':'draft',
																			   'sale_team_id':record.team_id.id,
																			   'member_id': record.team_id.user_id.name,
																			   'source_document':record.name,
																			   'amount_total':com_lines.manager_commission_amount,
																			   'currency_id':record.currency_id.id or self.env.user.company_id.currency_id.id,
																			   'user_id':'Sales Manager'
																			   })

										if line.product_id.account_type == 'by_percentage':
											for com_lines in line.product_id.product_commission_ids:
												percent_amount = (line.price_subtotal * com_lines.sales_manager_commission) / 100
												if line.price_subtotal >= com_lines.initiate_total and line.price_subtotal <= com_lines.end_total:
													product_commission.create({'product_id':line.product_id.id,
														 					   'state':'draft',
																			   'sale_team_id':record.team_id.id,
																			   'member_id': record.team_id.user_id.name,
																			   'source_document':record.name,
																			   'amount_total':percent_amount,
																			   'currency_id':record.currency_id.id or self.env.user.company_id.currency_id.id,
																			   'user_id':'Sales Manager'
																			   })
									if record.user_id:
										if line.product_id.account_type == 'fixed_amount':
											for com_lines in line.product_id.product_commission_ids:
												if line.price_subtotal >= com_lines.initiate_total and line.price_subtotal <= com_lines.end_total:
													product_commission.create({'product_id':line.product_id.id,
															                   'state':'draft',
																			   'sale_team_id':record.team_id.id,
																			   'member_id': record.user_id.name,
																			   'source_document':record.name,
																			   'amount_total':com_lines.sale_person_commission_amount,
																			   'currency_id':record.currency_id.id or self.env.user.company_id.currency_id.id,
																			   'user_id':'Sales Person'
																			   })

										if line.product_id.account_type == 'by_percentage':
											for com_lines in line.product_id.product_commission_ids:
												percent_amount = (line.price_subtotal * com_lines.sales_person_commission) / 100
												if line.price_subtotal >= com_lines.initiate_total and line.price_subtotal <= com_lines.end_total:
													product_commission.create({'product_id':line.product_id.id,
														 					   'state':'draft',
																			   'sale_team_id':record.team_id.id,
																			   'member_id': record.user_id.name,
																			   'source_document':record.name,
																			   'amount_total':percent_amount,
																			   'currency_id':record.currency_id.id or self.env.user.company_id.currency_id.id,
																			   'user_id':'Sales Person'
																			   })

						if calculation_method == 'sales_team':
							for sale_com in record.team_id.sale_team_commission_ids:
								if record.team_id._is_commission:
									if not record.team_id.user_id:
										raise ValidationError(_('Please Define Sale Team Manager as Team Leader in Sales Team'))
									if record.team_id.user_id:
										if record.team_id.account_type == 'fixed_amount':
											if line.price_subtotal >= sale_com.initiate_total and line.price_subtotal <= sale_com.end_total:
												product_commission.create({'product_id':line.product_id.id,
																		   'state':'draft',
																		   'sale_team_id':record.team_id.id,
																		   'member_id': record.team_id.user_id.name,
																		   'source_document':record.name,
																		   'amount_total':sale_com.manager_commission_amount,
																		   'currency_id':record.currency_id.id or self.env.user.company_id.currency_id.id,
																		   'user_id':'Sales Manager'
																		   })
										if record.team_id.account_type == 'by_percentage':
											percent_amount = (line.price_subtotal * sale_com.sales_manager_commission) / 100
											if line.price_subtotal >= sale_com.initiate_total and line.price_subtotal <= sale_com.end_total:
												product_commission.create({'product_id':line.product_id.id,
													                       'state':'draft',
																		   'sale_team_id':record.team_id.id,
																		   'member_id': record.team_id.user_id.name,
																		   'source_document':record.name,
																		   'amount_total':percent_amount,
																		   'currency_id':record.currency_id.id or self.env.user.company_id.currency_id.id,
																		   'user_id':'Sales Manager'
																		   })
									if record.user_id:
										if record.team_id.account_type == 'fixed_amount':
											if line.price_subtotal >= sale_com.initiate_total and line.price_subtotal <= sale_com.end_total:
												product_commission.create({'product_id':line.product_id.id,
																		   'state':'draft',
																		   'sale_team_id':record.team_id.id,
																		   'member_id': record.user_id.name,
																		   'source_document':record.name,
																		   'amount_total':sale_com.sale_person_commission_amount,
																		   'currency_id':record.currency_id.id or self.env.user.company_id.currency_id.id,
																		   'user_id':'Sales Person'
																		   })
										if record.team_id.account_type == 'by_percentage':
											percent_amount = (line.price_subtotal * sale_com.sales_person_commission) / 100
											if line.price_subtotal >= sale_com.initiate_total and line.price_subtotal <= sale_com.end_total:
												product_commission.create({'product_id':line.product_id.id,
													                       'state':'draft',
																		   'sale_team_id':record.team_id.id,
																		   'member_id': record.user_id.name,
																		   'source_document':record.name,
																		   'amount_total':percent_amount,
																		   'currency_id':record.currency_id.id or self.env.user.company_id.currency_id.id,
																		   'user_id':'Sales Person'
																		   })
						if calculation_method == 'product_categ':
							for com_lines in line.product_id.categ_id.sale_commission_ids:
								if line.product_id.categ_id._is_commission:
									if not record.team_id.user_id:
										raise ValidationError(_('Please Define Sale Team Manager as Team Leader in Sales Team'))
									if record.team_id.user_id:
										if line.product_id.categ_id.account_type == 'fixed_amount':
											if line.price_subtotal >= com_lines.initiate_total and line.price_subtotal <= com_lines.end_total:
												product_commission.create({'product_id':line.product_id.id,
													                       'state':'draft',
																		   'sale_team_id':record.team_id.id,
																		   'member_id': record.team_id.user_id.name,
																		   'source_document':record.name,
																		   'amount_total':com_lines.manager_commission_amount,
																		   'currency_id':record.currency_id.id or self.env.user.company_id.currency_id.id,
																		   'user_id':'Sales Manager'
																		   })
										if line.product_id.categ_id.account_type == 'by_percentage':
											percent_amount = (line.price_subtotal * com_lines.sales_manager_commission) / 100
											if line.price_subtotal >= com_lines.initiate_total and line.price_subtotal <= com_lines.end_total:
												product_commission.create({'product_id':line.product_id.id,
													                       'state':'draft',
																		   'sale_team_id':record.team_id.id,
																		   'member_id': record.team_id.user_id.name,
																		   'source_document':record.name,
																		   'amount_total':percent_amount,
																		   'currency_id':record.currency_id.id or self.env.user.company_id.currency_id.id,
																		   'user_id':'Sales Manager'
																		   })
									if record.user_id:
										if line.product_id.categ_id.account_type == 'fixed_amount':
											if line.price_subtotal >= com_lines.initiate_total and line.price_subtotal <= com_lines.end_total:
												product_commission.create({'product_id':line.product_id.id,
													                       'state':'draft',
																		   'sale_team_id':record.team_id.id,
																		   'member_id': record.user_id.name,
																		   'source_document':record.name,
																		   'amount_total':com_lines.sale_person_commission_amount,
																		   'currency_id':record.currency_id.id or self.env.user.company_id.currency_id.id,
																		   'user_id':'Sales Person'
																		   })
										if line.product_id.categ_id.account_type == 'by_percentage':
											percent_amount = (line.price_subtotal * com_lines.sales_person_commission) / 100
											if line.price_subtotal >= com_lines.initiate_total and line.price_subtotal <= com_lines.end_total:
												product_commission.create({'product_id':line.product_id.id,
													                       'state':'draft',
																		   'sale_team_id':record.team_id.id,
																		   'member_id': record.user_id.name,
																		   'source_document':record.name,
																		   'amount_total':percent_amount,
																		   'currency_id':record.currency_id.id or self.env.user.company_id.currency_id.id,
																		   'user_id':'Sales Person'
																		   })
					else:
						for line in record.invoice_line_ids:
							if calculation_method == 'product':
								if line.product_id._is_commission:
									if not record.team_id.user_id:
										raise ValidationError(_('Please Define Sale Team Manager as Team Leader in Sales Team'))
									if record.team_id.user_id:
										if line.product_id.account_type == 'fixed_amount':
											for com_lines in line.product_id.product_commission_ids:
												amount = company.currency_id._convert(line.price_subtotal, record.currency_id, company, fields.Date.today())
												commission_amount = company.currency_id._convert(com_lines.manager_commission_amount, record.currency_id, company, fields.Date.today())
												if amount >= com_lines.initiate_total and amount <= com_lines.end_total:
													product_commission.create({'product_id':line.product_id.id,
															                   'state':'draft',
																			   'sale_team_id':record.team_id.id,
																			   'member_id': record.team_id.user_id.name,
																			   'source_document':record.name,
																			   'amount_total': commission_amount,
																			   'currency_id':record.currency_id.id or self.env.user.company_id.currency_id.id,
																			   'user_id':'Sales Manager'
																			   })

										if line.product_id.account_type == 'by_percentage':
											for com_lines in line.product_id.product_commission_ids:
												amount = company.currency_id._convert(line.price_subtotal, record.currency_id, company, fields.Date.today())
												percent_amount = (amount * com_lines.sales_manager_commission) / 100
												if amount >= com_lines.initiate_total and amount <= com_lines.end_total:
													amount = company.currency_id._convert(percent_amount, record.currency_id, company, fields.Date.today())
													product_commission.create({'product_id':line.product_id.id,
														 					   'state':'draft',
																			   'sale_team_id':record.team_id.id,
																			   'member_id': record.team_id.user_id.name,
																			   'source_document':record.name,
																			   'amount_total':percent_amount,
																			   'currency_id':record.currency_id.id or self.env.user.company_id.currency_id.id,
																			   'user_id':'Sales Manager'
																			   })
									if record.user_id:
										if line.product_id.account_type == 'fixed_amount':
											for com_lines in line.product_id.product_commission_ids:
												amount = company.currency_id._convert(line.price_subtotal, record.currency_id, company, fields.Date.today())
												commission_amount = company.currency_id._convert(com_lines.sale_person_commission_amount, record.currency_id, company, fields.Date.today())
												if amount >= com_lines.initiate_total and amount <= com_lines.end_total:
													product_commission.create({'product_id':line.product_id.id,
															                   'state':'draft',
																			   'sale_team_id':record.team_id.id,
																			   'member_id': record.user_id.name,
																			   'source_document':record.name,
																			   'amount_total': commission_amount,
																			   'currency_id':record.currency_id.id or self.env.user.company_id.currency_id.id,
																			   'user_id':'Sales Person'
																			   })

										if line.product_id.account_type == 'by_percentage':
											for com_lines in line.product_id.product_commission_ids:
												amount = company.currency_id._convert(line.price_subtotal, record.currency_id, company, fields.Date.today())
												percent_amount = (amount * com_lines.sales_person_commission) / 100
												if amount >= com_lines.initiate_total and amount <= com_lines.end_total:
													product_commission.create({'product_id':line.product_id.id,
														 					   'state':'draft',
																			   'sale_team_id':record.team_id.id,
																			   'member_id': record.user_id.name,
																			   'source_document':record.name,
																			   'amount_total':percent_amount,
																			   'currency_id':record.currency_id.id or self.env.user.company_id.currency_id.id,
																			   'user_id':'Sales Person'
																			   })

						if calculation_method == 'sales_team':
							for sale_com in record.team_id.sale_team_commission_ids:
								if record.team_id._is_commission:
									if not record.team_id.user_id:
										raise ValidationError(_('Please Define Sale Team Manager as Team Leader in Sales Team'))
									if record.team_id.user_id:
										if record.team_id.account_type == 'fixed_amount':
											amount = company.currency_id._convert(line.price_subtotal, record.currency_id, company, fields.Date.today())
											commission_amount = company.currency_id._convert(sale_com.manager_commission_amount, record.currency_id, company, fields.Date.today())
											if amount >= sale_com.initiate_total and amount <= sale_com.end_total:
												product_commission.create({'product_id':line.product_id.id,
																		   'state':'draft',
																		   'sale_team_id':record.team_id.id,
																		   'member_id': record.team_id.user_id.name,
																		   'source_document':record.name,
																		   'amount_total': commission_amount,
																		   'currency_id':record.currency_id.id or self.env.user.company_id.currency_id.id,
																		   'user_id':'Sales Manager'
																		   })
										if record.team_id.account_type == 'by_percentage':
											amount = company.currency_id._convert(line.price_subtotal, record.currency_id, company, fields.Date.today())
											percent_amount = (amount * sale_com.sales_manager_commission) / 100
											if amount >= sale_com.initiate_total and amount <= sale_com.end_total:
												product_commission.create({'product_id':line.product_id.id,
													                       'state':'draft',
																		   'sale_team_id':record.team_id.id,
																		   'member_id': record.team_id.user_id.name,
																		   'source_document':record.name,
																		   'amount_total':percent_amount,
																		   'currency_id':record.currency_id.id or self.env.user.company_id.currency_id.id,
																		   'user_id':'Sales Manager'
																		   })
									if record.user_id:
										if record.team_id.account_type == 'fixed_amount':
											amount = company.currency_id._convert(line.price_subtotal, record.currency_id, company, fields.Date.today())
											commission_amount = company.currency_id._convert(sale_com.sale_person_commission_amount, record.currency_id, company, fields.Date.today())
											if line.price_subtotal >= sale_com.initiate_total and line.price_subtotal <= sale_com.end_total:
												product_commission.create({'product_id':line.product_id.id,
																		   'state':'draft',
																		   'sale_team_id':record.team_id.id,
																		   'member_id': record.user_id.name,
																		   'source_document':record.name,
																		   'amount_total': commission_amount,
																		   'currency_id':record.currency_id.id or self.env.user.company_id.currency_id.id,
																		   'user_id':'Sales Person'
																		   })
										if record.team_id.account_type == 'by_percentage':
											amount = company.currency_id._convert(line.price_subtotal, record.currency_id, company, fields.Date.today())
											percent_amount = (amount * sale_com.sales_person_commission) / 100
											if amount >= sale_com.initiate_total and amount <= sale_com.end_total:
												product_commission.create({'product_id':line.product_id.id,
													                       'state':'draft',
																		   'sale_team_id':record.team_id.id,
																		   'member_id': record.user_id.name,
																		   'source_document':record.name,
																		   'amount_total':percent_amount,
																		   'currency_id':record.currency_id.id or self.env.user.company_id.currency_id.id,
																		   'user_id':'Sales Person'
																		   })
						if calculation_method == 'product_categ':
							for com_lines in line.product_id.categ_id.sale_commission_ids:
								if line.product_id.categ_id._is_commission:
									if not record.team_id.user_id:
										raise ValidationError(_('Please Define Sale Team Manager as Team Leader in Sales Team'))
									if record.team_id.user_id:
										if line.product_id.categ_id.account_type == 'fixed_amount':
											amount = company.currency_id._convert(line.price_subtotal, record.currency_id, company, fields.Date.today())
											commission_amount = company.currency_id._convert(com_lines.manager_commission_amount, record.currency_id, company, fields.Date.today())
											if amount >= com_lines.initiate_total and amount <= com_lines.end_total:
												product_commission.create({'product_id':line.product_id.id,
													                       'state':'draft',
																		   'sale_team_id':record.team_id.id,
																		   'member_id': record.team_id.user_id.name,
																		   'source_document':record.name,
																		   'amount_total': commission_amount,
																		   'currency_id':record.currency_id.id or self.env.user.company_id.currency_id.id,
																		   'user_id':'Sales Manager'
																		   })
										if line.product_id.categ_id.account_type == 'by_percentage':
											amount = company.currency_id._convert(line.price_subtotal, record.currency_id, company, fields.Date.today())
											percent_amount = (amount * com_lines.sales_manager_commission) / 100
											if amount >= com_lines.initiate_total and amount <= com_lines.end_total:
												product_commission.create({'product_id':line.product_id.id,
													                       'state':'draft',
																		   'sale_team_id':record.team_id.id,
																		   'member_id': record.team_id.user_id.name,
																		   'source_document':record.name,
																		   'amount_total':percent_amount,
																		   'currency_id':record.currency_id.id or self.env.user.company_id.currency_id.id,
																		   'user_id':'Sales Manager'
																		   })
									if record.user_id:
										if line.product_id.categ_id.account_type == 'fixed_amount':
											amount = company.currency_id._convert(line.price_subtotal, record.currency_id, company, fields.Date.today())
											commission_amount = company.currency_id._convert(com_lines.sale_person_commission_amount, record.currency_id, company, fields.Date.today())
											if amount >= com_lines.initiate_total and amount <= com_lines.end_total:
												product_commission.create({'product_id':line.product_id.id,
													                       'state':'draft',
																		   'sale_team_id':record.team_id.id,
																		   'member_id': record.user_id.name,
																		   'source_document':record.name,
																		   'amount_total': commission_amount,
																		   'currency_id':record.currency_id.id or self.env.user.company_id.currency_id.id,
																		   'user_id':'Sales Person'
																		   })
										if line.product_id.categ_id.account_type == 'by_percentage':
											amount = company.currency_id._convert(line.price_subtotal, record.currency_id, company, fields.Date.today())
											percent_amount = (amount * com_lines.sales_person_commission) / 100
											if amount >= com_lines.initiate_total and amount <= com_lines.end_total:
												product_commission.create({'product_id':line.product_id.id,
													                       'state':'draft',
																		   'sale_team_id':record.team_id.id,
																		   'member_id': record.user_id.name,
																		   'source_document':record.name,
																		   'amount_total':percent_amount,
																		   'currency_id':record.currency_id.id or self.env.user.company_id.currency_id.id,
																		   'user_id':'Sales Person'
				
																		   })

		return res

class Payment(models.Model):

	_inherit = 'account.payment'

	sale_team = fields.Many2one('crm.team', 'Sales Team', related="invoice_ids.team_id")
	sale_person = fields.Many2one('res.users', 'Sales Person', default=lambda self: self.env.user, readonly=True)

	def post(self):
		res = super(Payment, self).post()
		company = self.env['res.company'].browse(self.env.context.get('company_id')) or self.env.user.company_id
		product_commission = self.env['sale.commission.line']
		apply_sale_commission = self.env['ir.config_parameter'].sudo().get_param('sale_commission_app.apply_sale_commission')
		calculation_method = self.env['ir.config_parameter'].sudo().get_param('sale_commission_app.calculation_method')
		if self.env.user.has_group('sale_commission_app.group_show_commission_view'):
			for record in self:
				for lines in record.invoice_ids:
					if lines.type == 'out_invoice':
						if company.currency_id.id == record.currency_id.id:
							if apply_sale_commission == 'customer_payment':
								if calculation_method == 'product':
									for line in lines.invoice_line_ids:
										for li in line.product_id.product_commission_ids:
											if line.product_id._is_commission:
												if not record.sale_team.user_id:
													raise ValidationError(_('Please Define Sale Team Manager as Team Leader in Sales Team'))
												if record.sale_team.user_id:
													if line.product_id.account_type == 'fixed_amount':
														if record.amount >= li.initiate_total and record.amount <= li.end_total:
															product_commission.create({'product_id':line.product_id.id,
																                       'state':'draft',
																					   'sale_team_id':lines.team_id.id,
																					   'member_id':record.sale_team.user_id.name,
																					   'source_document':record.name,
																					   'amount_total':li.manager_commission_amount,
																					   'currency_id':record.currency_id.id or self.env.user.company_id.currency_id.id,
																					   'user_id':'Sales Manager',
																					   })
													if line.product_id.account_type == 'by_percentage':
														percent_amount = (record.amount * li.sales_manager_commission) / 100
														if record.amount >= li.initiate_total and record.amount <= li.end_total:
															product_commission.create({'product_id':line.product_id.id,
																                       'state':'draft',
																					   'sale_team_id':lines.team_id.id,
																					   'member_id':record.sale_team.user_id.name,
																					   'source_document':record.name,
																					   'amount_total':percent_amount,
																					   'currency_id':record.currency_id.id or self.env.user.company_id.currency_id.id,
																					   'user_id':'Sales Manager',
																					   })
												if record.sale_person:
													if line.product_id.account_type == 'fixed_amount':
														if record.amount >= li.initiate_total and line.price_subtotal <= li.end_total:
															product_commission.create({'product_id':line.product_id.id,
																                       'state':'draft',
																					   'sale_team_id':lines.team_id.id,
																					   'member_id':record.sale_person.name,
																					   'source_document':record.name,
																					   'amount_total':li.sale_person_commission_amount,
																					   'currency_id':record.currency_id.id or self.env.user.company_id.currency_id.id,
																					   'user_id':'Sales Person',
																					   })

													if line.product_id.account_type == 'by_percentage':
														percent_amount = (record.amount * li.sales_person_commission) / 100
														if record.amount >= li.initiate_total and record.amount <= li.end_total:
															product_commission.create({'product_id':line.product_id.id,
																                       'state':'draft',
																					   'sale_team_id':lines.team_id.id,
																					   'member_id':record.sale_person.name,
																					   'source_document':record.name,
																					   'amount_total':percent_amount,
																					   'currency_id':record.currency_id.id or self.env.user.company_id.currency_id.id,
																					   'user_id':'Sales Person',
																					   })

								if calculation_method == 'sales_team':
									for line in lines.invoice_line_ids:
										for li in lines.team_id.sale_team_commission_ids:
											if lines.team_id._is_commission:
												if not record.sale_team.user_id:
													raise ValidationError(_('Please Define Sale Team Manager as Team Leader in Sales Team'))
												if record.sale_team.user_id:
													if lines.team_id.account_type == 'fixed_amount':
														if record.amount >= li.initiate_total and record.amount <= li.end_total:
															product_commission.create({'product_id':line.product_id.id,
															                       'state':'draft',
																				   'sale_team_id':lines.team_id.id,
																				   'member_id':record.sale_team.user_id.name,
																				   'source_document':record.name,
																				   'amount_total':li.manager_commission_amount,
																				   'currency_id':record.currency_id.id or self.env.user.company_id.currency_id.id,
																				   'user_id':'Sales Manager',
																				   })
													if lines.team_id.account_type == 'by_percentage':
														percent_amount = (record.amount * li.sales_manager_commission) / 100
														if record.amount >= li.initiate_total and record.amount <= li.end_total:
															product_commission.create({'product_id':line.product_id.id,
																                       'state':'draft',
																					   'sale_team_id':lines.team_id.id,
																					   'member_id':record.sale_team.user_id.name,
																					   'source_document':record.name,
																					   'amount_total':percent_amount,
																					   'currency_id':record.currency_id.id or self.env.user.company_id.currency_id.id,
																					   'user_id':'Sales Manager',
																					   })
												if record.sale_person:
													if lines.team_id.account_type == 'fixed_amount':
														if record.amount >= li.initiate_total and record.amount <= li.end_total:
															product_commission.create({'product_id':line.product_id.id,
															                       'state':'draft',
																				   'sale_team_id':lines.team_id.id,
																				   'member_id':record.sale_person.name,
																				   'source_document':record.name,
																				   'amount_total':li.sale_person_commission_amount,
																				   'currency_id':record.currency_id.id or self.env.user.company_id.currency_id.id,
																				   'user_id':'Sales Person',
																				   })
													if lines.team_id.account_type == 'by_percentage':
														percent_amount = (record.amount * li.sales_person_commission) / 100
														if record.amount >= li.initiate_total and record.amount <= li.end_total:
															product_commission.create({'product_id':line.product_id.id,
																                       'state':'draft',
																					   'sale_team_id':lines.team_id.id,
																					   'member_id':record.sale_person.name,
																					   'source_document':record.name,
																					   'amount_total':percent_amount,
																					   'currency_id':record.currency_id.id or self.env.user.company_id.currency_id.id,
																					   'user_id':'Sales Person',
																					   })

								if calculation_method == 'product_categ':
									for line in lines.invoice_line_ids:
										for li in line.product_id.categ_id.sale_commission_ids:
											if line.product_id.categ_id._is_commission:
												if not record.sale_team.user_id:
													raise ValidationError(_('Please Define Sale Team Manager as Team Leader in Sales Team'))
												if record.sale_team.user_id:
													if line.product_id.categ_id.account_type == 'fixed_amount':
														if record.amount >= li.initiate_total and record.amount <= li.end_total:
															product_commission.create({'product_id':line.product_id.id,
															                       'state':'draft',
																				   'sale_team_id':lines.team_id.id,
																				   'member_id':record.sale_team.user_id.name,
																				   'source_document':record.name,
																				   'amount_total':li.manager_commission_amount,
																				   'currency_id':record.currency_id.id or self.env.user.company_id.currency_id.id,
																				   'user_id':'Sales Manager',
																				   })
													if line.product_id.categ_id.account_type == 'by_percentage':
														percent_amount = (record.amount * li.sales_manager_commission) / 100
														if record.amount >= li.initiate_total and record.amount <= li.end_total:
															product_commission.create({'product_id':line.product_id.id,
																                       'state':'draft',
																					   'sale_team_id':lines.team_id.id,
																					   'member_id':record.sale_team.user_id.name,
																					   'source_document':record.name,
																					   'amount_total':percent_amount,
																					   'currency_id':record.currency_id.id or self.env.user.company_id.currency_id.id,
																					   'user_id':'Sales Manager',
																					   })
												if record.sale_person:
													if line.product_id.categ_id.account_type == 'fixed_amount':
														if record.amount >= li.initiate_total and record.amount <= li.end_total:
															product_commission.create({'product_id':line.product_id.id,
															                       'state':'draft',
																				   'sale_team_id':lines.team_id.id,
																				   'member_id':record.sale_person.name,
																				   'source_document':record.name,
																				   'amount_total':li.sale_person_commission_amount,
																				   'currency_id':record.currency_id.id or self.env.user.company_id.currency_id.id,
																				   'user_id':'Sales Person',
																				   })
													if line.product_id.categ_id.account_type == 'by_percentage':
														percent_amount = (record.amount * li.sales_person_commission) / 100
														if record.amount >= li.initiate_total and record.amount <= li.end_total:
															product_commission.create({'product_id':line.product_id.id,
																                       'state':'draft',
																					   'sale_team_id':lines.team_id.id,
																					   'member_id':record.sale_person.name,
																					   'source_document':record.name,
																					   'amount_total':percent_amount,
																					   'currency_id':record.currency_id.id or self.env.user.company_id.currency_id.id,
																					   'user_id':'Sales Person',
																					   })
						else:
							if apply_sale_commission == 'customer_payment':
								for lines in record.invoice_ids:
									if calculation_method == 'product':
										for line in lines.invoice_line_ids:
											for li in line.product_id.product_commission_ids:
												if line.product_id._is_commission:
													if not record.sale_team.user_id:
														raise ValidationError(_('Please Define Sale Team Manager as Team Leader in Sales Team'))
													if record.sale_team.user_id:
														if line.product_id.account_type == 'fixed_amount':
															amount = company.currency_id._convert(record.amount, record.currency_id, company, fields.Date.today())
															commission_amount = company.currency_id._convert(li.manager_commission_amount, record.currency_id, company, fields.Date.today())
															if amount >= li.initiate_total and amount <= li.end_total:
																product_commission.create({'product_id':line.product_id.id,
																	                       'state':'draft',
																						   'sale_team_id':lines.team_id.id,
																						   'member_id':record.sale_team.user_id.name,
																						   'source_document':record.name,
																						   'amount_total': commission_amount,
																						   'currency_id':record.currency_id.id or self.env.user.company_id.currency_id.id,
																						   'user_id':'Sales Manager',
																						   })
														if line.product_id.account_type == 'by_percentage':
															amount = company.currency_id._convert(record.amount, record.currency_id, company, fields.Date.today())
															percent_amount = (amount * li.sales_manager_commission) / 100
															if amount >= li.initiate_total and amount <= li.end_total:
																product_commission.create({'product_id':line.product_id.id,
																	                       'state':'draft',
																						   'sale_team_id':lines.team_id.id,
																						   'member_id':record.sale_team.user_id.name,
																						   'source_document':record.name,
																						   'amount_total':percent_amount,
																						   'currency_id':record.currency_id.id or self.env.user.company_id.currency_id.id,
																						   'user_id':'Sales Manager',
																						   })
													if record.sale_person:
														if line.product_id.account_type == 'fixed_amount':
															amount = company.currency_id._convert(record.amount, record.currency_id, company, fields.Date.today())
															commission_amount = company.currency_id._convert(li.sale_person_commission_amount, record.currency_id, company, fields.Date.today())
															if amount >= li.initiate_total and amount <= li.end_total:
																product_commission.create({'product_id':line.product_id.id,
																	                       'state':'draft',
																						   'sale_team_id':lines.team_id.id,
																						   'member_id':record.sale_person.name,
																						   'source_document':record.name,
																						   'amount_total': commission_amount,
																						   'currency_id':record.currency_id.id or self.env.user.company_id.currency_id.id,
																						   'user_id':'Sales Person',
																						   })

														if line.product_id.account_type == 'by_percentage':
															amount = company.currency_id._convert(record.amount, record.currency_id, company, fields.Date.today())
															percent_amount = (amount * li.sales_person_commission) / 100
															if amount >= li.initiate_total and amount <= li.end_total:
																product_commission.create({'product_id':line.product_id.id,
																	                       'state':'draft',
																						   'sale_team_id':lines.team_id.id,
																						   'member_id':record.sale_person.name,
																						   'source_document':record.name,
																						   'amount_total':percent_amount,
																						   'currency_id':record.currency_id.id or self.env.user.company_id.currency_id.id,
																						   'user_id':'Sales Person',
																						   })

									if calculation_method == 'sales_team':
										for line in lines.invoice_line_ids:
											for li in lines.team_id.sale_team_commission_ids:
												if lines.team_id._is_commission:
													if not record.sale_team.user_id:
														raise ValidationError(_('Please Define Sale Team Manager as Team Leader in Sales Team'))
													if record.sale_team.user_id:
														if lines.team_id.account_type == 'fixed_amount':
															amount = company.currency_id._convert(record.amount, record.currency_id, company, fields.Date.today())
															commission_amount = company.currency_id._convert(li.manager_commission_amount, record.currency_id, company, fields.Date.today())
															if amount >= li.initiate_total and amount <= li.end_total:
																product_commission.create({'product_id':line.product_id.id,
																                       'state':'draft',
																					   'sale_team_id':lines.team_id.id,
																					   'member_id':record.sale_team.user_id.name,
																					   'source_document':record.name,
																					   'amount_total': commission_amount,
																					   'currency_id':record.currency_id.id or self.env.user.company_id.currency_id.id,
																					   'user_id':'Sales Manager',
																					   })
														if lines.team_id.account_type == 'by_percentage':
															amount = company.currency_id._convert(record.amount, record.currency_id, company, fields.Date.today())
															percent_amount = (amount * li.sales_manager_commission) / 100
															if amount >= li.initiate_total and amount <= li.end_total:
																product_commission.create({'product_id':line.product_id.id,
																	                       'state':'draft',
																						   'sale_team_id':lines.team_id.id,
																						   'member_id':record.sale_team.user_id.name,
																						   'source_document':record.name,
																						   'amount_total':percent_amount,
																						   'currency_id':record.currency_id.id or self.env.user.company_id.currency_id.id,
																						   'user_id':'Sales Manager',
																						   })
													if record.sale_person:
														if lines.team_id.account_type == 'fixed_amount':
															amount = company.currency_id._convert(record.amount, record.currency_id, company, fields.Date.today())
															commission_amount = company.currency_id._convert(li.sale_person_commission_amount, record.currency_id, company, fields.Date.today())
															if amount >= li.initiate_total and amount <= li.end_total:
																product_commission.create({'product_id':line.product_id.id,
																                       'state':'draft',
																					   'sale_team_id':lines.team_id.id,
																					   'member_id':record.sale_person.name,
																					   'source_document':record.name,
																					   'amount_total': commission_amount,
																					   'currency_id':record.currency_id.id or self.env.user.company_id.currency_id.id,
																					   'user_id':'Sales Person',
																					   })
														if lines.team_id.account_type == 'by_percentage':
															amount = company.currency_id._convert(record.amount, record.currency_id, company, fields.Date.today())
															percent_amount = (amount * li.sales_person_commission) / 100
															if amount >= li.initiate_total and amount <= li.end_total:
																product_commission.create({'product_id':line.product_id.id,
																	                       'state':'draft',
																						   'sale_team_id':lines.team_id.id,
																						   'member_id':record.sale_person.name,
																						   'source_document':record.name,
																						   'amount_total':percent_amount,
																						   'currency_id':record.currency_id.id or self.env.user.company_id.currency_id.id,
																						   'user_id':'Sales Person',
																						   })

									if calculation_method == 'product_categ':
										for line in lines.invoice_line_ids:
											for li in line.product_id.categ_id.sale_commission_ids:
												if line.product_id.categ_id._is_commission:
													if not record.sale_team.user_id:
														raise ValidationError(_('Please Define Sale Team Manager as Team Leader in Sales Team'))
													if record.sale_team.user_id:
														if line.product_id.categ_id.account_type == 'fixed_amount':
															amount = company.currency_id._convert(record.amount, record.currency_id, company, fields.Date.today())
															commission_amount = company.currency_id._convert(li.manager_commission_amount, record.currency_id, company, fields.Date.today())
															if amount >= li.initiate_total and amount <= li.end_total:
																product_commission.create({'product_id':line.product_id.id,
																                       'state':'draft',
																					   'sale_team_id':lines.team_id.id,
																					   'member_id':record.sale_team.user_id.name,
																					   'source_document':record.name,
																					   'amount_total': commission_amount,
																					   'currency_id':record.currency_id.id or self.env.user.company_id.currency_id.id,
																					   'user_id':'Sales Manager',
																					   })
														if line.product_id.categ_id.account_type == 'by_percentage':
															amount = company.currency_id._convert(record.amount, record.currency_id, company, fields.Date.today())
															percent_amount = (amount * li.sales_manager_commission) / 100
															if amount >= li.initiate_total and amount <= li.end_total:
																product_commission.create({'product_id':line.product_id.id,
																	                       'state':'draft',
																						   'sale_team_id':lines.team_id.id,
																						   'member_id':record.sale_team.user_id.name,
																						   'source_document':record.name,
																						   'amount_total':percent_amount,
																						   'currency_id':record.currency_id.id or self.env.user.company_id.currency_id.id,
																						   'user_id':'Sales Manager',
																						   })
													if record.sale_person:
														if line.product_id.categ_id.account_type == 'fixed_amount':
															amount = company.currency_id._convert(record.amount, record.currency_id, company, fields.Date.today())
															commission_amount = company.currency_id._convert(li.sale_person_commission_amount, record.currency_id, company, fields.Date.today())
															if amount >= li.initiate_total and amount <= li.end_total:
																product_commission.create({'product_id':line.product_id.id,
																                       'state':'draft',
																					   'sale_team_id':lines.team_id.id,
																					   'member_id':record.sale_person.name,
																					   'source_document':record.name,
																					   'amount_total': commission_amount,
																					   'currency_id':record.currency_id.id or self.env.user.company_id.currency_id.id,
																					   'user_id':'Sales Person',
																					   })
														if line.product_id.categ_id.account_type == 'by_percentage':
															amount = company.currency_id._convert(record.amount, record.currency_id, company, fields.Date.today())
															percent_amount = (amount * li.sales_person_commission) / 100
															if amount >= li.initiate_total and amount <= li.end_total:
																product_commission.create({'product_id':line.product_id.id,
																	                       'state':'draft',
																						   'sale_team_id':lines.team_id.id,
																						   'member_id':record.sale_person.name,
																						   'source_document':record.name,
																						   'amount_total':percent_amount,
																						   'currency_id':record.currency_id.id or self.env.user.company_id.currency_id.id,
																						   'user_id':'Sales Person',
																						   })

		return res