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

        worksheet.write(1,0,'Proyecto de Instalación',header_style)
        worksheet.write(2,0,'Cuenta analítica (Folio):',header_style)
        worksheet.write(2,1, self.cuenta_analitica_id.name)
        worksheet.write(3,0,'Cliente:',header_style)
        worksheet.write(3,1, self.cuenta_analitica_id.partner_id.name)
        worksheet.write(4,4,'Salida Material Inicial',header_style)
        worksheet.write(4,7,'Devolución Material',header_style)
        worksheet.write(4,10,'Costo',header_style)

        worksheet.write(5,0,'Producto',header_style)
        worksheet.write(5,1,'Referencia interna',header_style)
        worksheet.write(5,2,'Cantidad salida',header_style)
        worksheet.write(5,3,'Almacén salida',header_style)
        worksheet.write(5,4,'Almacén entrada',header_style)
        worksheet.write(5,5,'Cantidad entrada',header_style)
        worksheet.write(5,6,'Almacén salida',header_style)
        worksheet.write(5,7,'Almacén entrada',header_style)
        worksheet.write(5,8,'Cantidad total',header_style)
        worksheet.write(5,9,'Costo unitario',header_style)
        worksheet.write(5,10,'Costo total',header_style)
        row = 6
        col = 0
        stock_picking = self.env['stock.picking'].search([('x_studio_cuenta_analitica','=', self.cuenta_analitica_id.id),
                                                     ('picking_type_id.code','in',['incoming','outgoing']), ('state', '=', 'done')
                                                     ])

        product_wise = {}
        for picking in stock_picking:
            for move in picking.move_ids_without_package:
               product= move.product_id
   #            _logger.info('picking type %s --- producto %s ----- cantidad %s', move.picking_type_id.code, move.product_id.name, move.quantity_done)
               if product not in product_wise:
                   if move.picking_type_id.code == 'incoming':
                       product_wise[product] = {
                         'product_id': move.product_id.id,
                         'outgoing': 0,
                         'incoming': move.quantity_done,
                         'in_from_loc': move.location_id.location_id.name + '/' + move.location_id.name,
                         'in_to_loc': move.location_dest_id.location_id.name + '/' + move.location_dest_id.name,
                       }
                   else:
                      product_wise[product] = {
                         'product_id': move.product_id.id,
                         'outgoing': move.quantity_done,
                         'incoming': 0,
                         'out_from_loc': move.location_id.location_id.name + '/' + move.location_id.name,
                         'out_to_loc': move.location_dest_id.location_id.name + '/' + move.location_dest_id.name,
                      }
               else:
                   if move.picking_type_id.code == 'incoming':
                      product_wise[product].update({
                         'incoming' : product_wise[product].get('incoming') + move.quantity_done,
                         'in_from_loc': move.location_id.location_id.name + '/' + move.location_id.name,
                         'in_to_loc': move.location_dest_id.location_id.name + '/' + move.location_dest_id.name,
                      })
                   else:
                      product_wise[product].update({
                         'outgoing' : product_wise[product].get('outgoing') + move.quantity_done,
                         'out_from_loc': move.location_id.location_id.name + '/' + move.location_id.name,
                         'out_to_loc': move.location_dest_id.location_id.name + '/' + move.location_dest_id.name,
                      })
        for product,data in product_wise.items():
            worksheet.write(row, col, product.name, text_center)
            col += 1
            worksheet.write(row, col, product.default_code, text_center)
            col += 1
            worksheet.write(row, col, data.get('outgoing'), text_center)
            col += 1 
            worksheet.write(row, col, data.get('out_from_loc'), text_center)
            col += 1
            worksheet.write(row, col, data.get('out_to_loc'), text_center)
            col += 1
            worksheet.write(row, col, data.get('incoming'), text_center)
            col += 1
            worksheet.write(row, col, data.get('in_from_loc'), text_center)
            col += 1
            worksheet.write(row, col, data.get('in_to_loc'), text_center)
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
    
    
        
        
        