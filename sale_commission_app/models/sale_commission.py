# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError

class ResConfigSettings(models.TransientModel):
	_inherit = "res.config.settings"

	apply_sale_commission = fields.Selection([('sales_confirmation', 'Confirm Sale'),
											  ('invoice_validate', 'Validate Invoice'),
											  ('customer_payment', 'Register Payment')],string="Apply Commission On",default='sales_confirmation')
	
	calculation_method = fields.Selection([('sales_team','On Sales Team'),
										   ('product_categ','On Product Category'),
										   ('product','On Product')],string="Based on Calculation",default='sales_team')

	def set_values(self):

		res = super(ResConfigSettings,self).set_values()
		apply_sale_commission = self.env['ir.config_parameter'].sudo().set_param('sale_commission_app.apply_sale_commission',self.apply_sale_commission)
		calculation_method = self.env['ir.config_parameter'].sudo().set_param('sale_commission_app.calculation_method',self.calculation_method)

		return res

	@api.model
	def get_values(self):

		res = super(ResConfigSettings,self).get_values()
		apply_sale_commission = self.env['ir.config_parameter'].sudo().get_param('sale_commission_app.apply_sale_commission')
		calculation_method = self.env['ir.config_parameter'].sudo().get_param('sale_commission_app.calculation_method')
		res.update({'apply_sale_commission':apply_sale_commission,'calculation_method':calculation_method})

		return res


class ProductCategory(models.Model):
	_inherit = "product.category"

	_is_commission = fields.Boolean(string="Is Commission Product")
	account_type = fields.Selection([('fixed_amount','Fixed Amount'),('by_percentage','By Percentage')],string="Amount Type For Commission")
	sale_commission_ids = fields.One2many('commission.record','product_category_id')

	@api.constrains('sale_commission_ids')
	def _check_commission(self):
		if self._is_commission:
			if not self.sale_commission_ids:
				raise ValidationError(_('Please enter Commission Values'))

class CommissionRecord(models.Model):
	_name = "commission.record"
	_description = "Commission for Product Category"

	initiate_total = fields.Float(string="Initiate Total", required=True)
	end_total = fields.Float(string="End Total", required=True)
	sales_manager_commission = fields.Float(string="Sales Manager Commission(%)")
	sales_person_commission = fields.Float(string="Sales Person Commmission(%)")
	manager_commission_amount = fields.Float(string="Sales Manager Commission Amount")
	sale_person_commission_amount = fields.Float(string="Sales Person Commission Amount")
	product_category_id = fields.Many2one('product.category')
	account_type = fields.Selection([('fixed_amount','Fixed Amount'),('by_percentage','By Percentage')],related='product_category_id.account_type',string="Amount Type For Commission")

class ProductTemplate(models.Model):
	_inherit = "product.template"

	_is_commission = fields.Boolean(string="Is Commission Product")
	account_type = fields.Selection([('fixed_amount','Fixed Amount'),('by_percentage','By Percentage')],string="Amount Type For Commission")
	product_commission_ids = fields.One2many('product.commission.record','product_category_id')

	@api.constrains('product_commission_ids')
	def _check_commission(self):
		if self._is_commission:
			if not self.product_commission_ids:
				raise ValidationError(_('Please enter Commission Values'))

class ProductCommissionRecord(models.Model):
	_name = "product.commission.record"
	_description = "Commission for Product"

	initiate_total = fields.Float(string="Initiate Total", required=True)
	end_total = fields.Float(string="End Total", required=True)
	sales_manager_commission = fields.Float(string="Sales Manager Commission(%)")
	sales_person_commission = fields.Float(string="Sales Person Commmission(%)")
	manager_commission_amount = fields.Float(string="Sales Manager Commission Amount")
	sale_person_commission_amount = fields.Float(string="Sales Person Commission Amount")
	product_category_id = fields.Many2one('product.template')
	account_type = fields.Selection([('fixed_amount','Fixed Amount'),('by_percentage','By Percentage')],related="product_category_id.account_type", string="Amount Type For Commission")

class CrmTeam(models.Model):
	_inherit = "crm.team"

	_is_commission = fields.Boolean(string="Is Commission Product")
	account_type = fields.Selection([('fixed_amount','Fixed Amount'),('by_percentage','By Percentage')],string="Amount Type For Commission")
	sale_team_commission_ids = fields.One2many('sale.team.commission.record','crm_team_id')

	@api.constrains('sale_team_commission_ids')
	def _check_commission(self):
		if self._is_commission:
			if not self.sale_team_commission_ids:
				raise ValidationError(_('Please enter Commission Values'))

class SaleTeamCommissionRecord(models.Model):
	_name = "sale.team.commission.record"
	_description = "Commission for Sales Team"

	initiate_total = fields.Float(string="Initiate Total", required=True)
	end_total = fields.Float(string="End Total", required=True)
	sales_manager_commission = fields.Float(string="Sales Manager Commission(%)")
	sales_person_commission = fields.Float(string="Sales Person Commmission(%)")
	manager_commission_amount = fields.Float(string="Sales Manager Commission Amount")
	sale_person_commission_amount = fields.Float(string="Sales Person Commission Amount")
	crm_team_id = fields.Many2one('crm.team')
	account_type = fields.Selection([('fixed_amount','Fixed Amount'),('by_percentage','By Percentage')],related='crm_team_id.account_type',string="Amount Type For Commission")


class CrmTeam(models.Model):
	_inherit = "crm.team"

	_is_commission = fields.Boolean(string="Is Commission Product")
	account_type = fields.Selection([('fixed_amount','Fixed Amount'),('by_percentage','By Percentage')],string="Amount Type For Commission")
	sale_team_commission_ids = fields.One2many('sale.team.commission.record','crm_team_id')

	@api.constrains('sale_team_commission_ids')
	def _check_commission(self):
		if self._is_commission:
			if not self.sale_team_commission_ids:
				raise ValidationError(_('Please enter Commission Values'))

class SaleTeamCommissionRecord(models.Model):
	_name = "sale.team.commission.record"
	_description = "Commission for Sales Team"

	initiate_total = fields.Float(string="Initiate Total", required=True)
	end_total = fields.Float(string="End Total", required=True)
	sales_manager_commission = fields.Float(string="Sales Manager Commission(%)")
	sales_person_commission = fields.Float(string="Sales Person Commmission(%)")
	manager_commission_amount = fields.Float(string="Sales Manager Commission Amount")
	sale_person_commission_amount = fields.Float(string="Sales Person Commission Amount")
	crm_team_id = fields.Many2one('crm.team')
	account_type = fields.Selection([('fixed_amount','Fixed Amount'),('by_percentage','By Percentage')],related='crm_team_id.account_type',string="Amount Type For Commission")

class ProductSupplierInfo(models.Model):
	_inherit = "product.supplierinfo"

	_is_commission = fields.Boolean(string="Is Commission Product")
	account_type = fields.Selection([('fixed_amount','Fixed Amount'),('by_percentage','By Percentage')],string="Amount Type For Commission")
	supplierinfo_commission_ids = fields.One2many('product.supplierinfo.commission.record','supplier_id')

	@api.constrains('supplierinfo_commission_ids')
	def _check_commission(self):
		if self._is_commission:
			if not self.sale_team_commission_ids:
				raise ValidationError(_('Please enter Commission Values'))

class ProductSupplierInfoCommissionRecord(models.Model):
	_name = "product.supplierinfo.commission.record"
	_description = "Commission for Sales Team"

	initiate_total = fields.Float(string="Initiate Total", required=True)
	end_total = fields.Float(string="End Total", required=True)
	supplier_commission = fields.Float(string="Seller(Vendor) Commmission(%)")
	supplier_commission_amount = fields.Float(string="Seller(Vendor) Commission Amount")
	supplier_id = fields.Many2one('product.supplierinfo')
	account_type = fields.Selection([('fixed_amount','Fixed Amount'),('by_percentage','By Percentage')],related='supplier_id.account_type',string="Amount Type For Commission")
