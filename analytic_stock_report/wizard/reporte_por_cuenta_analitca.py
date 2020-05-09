# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import io
import base64
import itertools
from odoo.tools.misc import xlwt
from xlwt import easyxf
from collections import defaultdict
#import logging
#_logger = logging.getLogger(__name__)

class ReportePorCuentaAnalitca(models.TransientModel):
    _name = 'reporte.por.cuenta.analitca'
    
    cuenta_analitica_id = fields.Many2one('account.analytic.account', string='Cuenta Analitica', required=True)
    file_data = fields.Binary("File Data")
    
    def generate_cuenta_analitica_reporte(self):
        
        workbook = xlwt.Workbook()
        worksheet= workbook.add_sheet('Reporte Por Cuenta Analitica')
        col_width = 256 * 22
        try:
            for i in itertools.count():
                worksheet.col(i).width = col_width
        except ValueError:
            pass
        header_style = xlwt.easyxf('font:bold True;align: horiz center;')
        text_center = xlwt.easyxf('align: horiz center;')
        
        worksheet.write(0,0,'Producto',header_style)
        worksheet.write(0,1,'Referencia interna',header_style)
        worksheet.write(0,2,'Cantidad salida',header_style)
        worksheet.write(0,3,'Cantidad entrada',header_style)
        worksheet.write(0,4,'Cantidad total',header_style)
        worksheet.write(0,5,'Costo unitario',header_style)
        worksheet.write(0,6,'Costo total',header_style)
        row = 1
        col = 0
        stock_moves = self.env['stock.move'].search([('analytic_account_id','=', self.cuenta_analitica_id.id),
                                                     ('picking_type_id.code','in',['incoming','outgoing']), ('state', '=', 'done')
                                                     ])

        product_wise = {}
        for move in stock_moves:
            product= move.product_id
#            _logger.info('picking type %s --- producto %s ----- cantidad %s', move.picking_type_id.code, move.product_id.name, move.quantity_done)
            if product not in product_wise:
                if move.picking_type_id.code == 'incoming':
                   product_wise[product] = {
                      'product_id': move.product_id.id,
                      'outgoing': 0,
                      'incoming': move.quantity_done,
                   }
                else:
                   product_wise[product] = {
                      'product_id': move.product_id.id,
                      'outgoing': move.quantity_done,
                      'incoming': 0,
                   }
            else:
                if move.picking_type_id.code == 'incoming':
                   product_wise[product].update({
                      'incoming' : product_wise[product].get('incoming') + move.quantity_done,
                   })
                else:
                   product_wise[product].update({
                      'outgoing' : product_wise[product].get('outgoing') + move.quantity_done,
                   })
        for product,data in product_wise.items():
            worksheet.write(row, col, product.name, text_center)
            col += 1 
            worksheet.write(row, col, product.default_code, text_center)
            col += 1
            worksheet.write(row, col, data.get('outgoing'), text_center)
            col += 1 
            worksheet.write(row, col, data.get('incoming'), text_center)
            col += 1     
            worksheet.write(row, col,  data.get('outgoing') - data.get('incoming') , text_center)
            col += 1 
            worksheet.write(row, col, product.standard_price , text_center)
            col += 1 
            worksheet.write(row, col, (data.get('outgoing') - data.get('incoming')) * product.standard_price , text_center)
            col += 1 
            worksheet.write(row, col)
            col = 0
            row += 1       
        fp = io.BytesIO()
        workbook.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()
        self.write({'file_data': base64.b64encode(data)})
        action = {
                'name': 'Reporte Por Cuenta Analitica',
                'type': 'ir.actions.act_url',
                'url': "/web/content/?model=" + self._name + "&id=" + str(self.id) + "&field=file_data&download=true&filename=Reporte_Por_Cuenta_Analitica.xls",
                'target': 'self',
                }
        return action
    
    
        
        
        