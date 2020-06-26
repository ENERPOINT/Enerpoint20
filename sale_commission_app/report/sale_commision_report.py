# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class generate_report_details(models.TransientModel):

	_name = "sale.commission.report"
	_description = "Report for Commission"
	
	def generate_report(self):

		active_ids = self._context.get('active_ids')

		data={
				'ids': self.ids,
				'model':self._name,
				'active_ids' : active_ids
		}
		return self.env.ref('sale_commission_app.report_template_ids').report_action(self, data=data)

class sale_commission_report(models.AbstractModel):

	_name= 'report.sale_commission_app.worksheet_template_ids'
	_description = "Report Template"

	@api.model
	def _get_report_values(self, docids, data=None):
		sale_commission_line = self.env['sale.commission.worksheet'].search([('id','in',data.get('active_ids'))])
		return {
			'doc_ids': sale_commission_line.ids,
			'doc_model': 'sale.commission.report',
			'docs': sale_commission_line,
		}

