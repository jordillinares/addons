# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2012 Tiny SPRL (http://tiny.be). All Rights Reserved   
#
#    This module,
#    Copyright (C) 2015 KM Sistemas de Información, S.L. - http://www.kmsistemas.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp import models, fields, api, tools
from openerp.exceptions import except_orm
from openerp.tools.translate import _




class stock_move_consume(models.Model):
     
    _inherit = 'stock.move.consume'
    
    @api.multi
    def onchange_qty_or_lot_id(self, product_id, product_uom, restrict_lot_id=False, product_qty=0.0, location_id=False):
        quant_obj = self.env['stock.quant']
        product_obj = self.env['product.product']
        location_obj = self.env['stock.location']
        lot_obj = self.env['stock.production.lot']
        warning = {}
        max_qty = 0.0
        product = product_obj.browse(product_id)
        location = location_obj.browse(location_id)
        if restrict_lot_id:
            lot = lot_obj.browse(restrict_lot_id)
            if location_id:
                max_qty = product.with_context(location=location_id,lot_id=restrict_lot_id).qty_available
                if product_qty > max_qty:
                    warning = {
                        'title': _('Warning!'),
                        'message': _('You are trying to consume %s %s of lot %s, but there are only available '
                                     '%s %s on %s.\nQuantity automatically set to maximum available.')
                               % (product_qty, product.uom_id.name, lot.name, max_qty, product.uom_id.name, location.name),
                    }
                    product_qty = max_qty
        else:
            if location_id:
                max_qty = product.with_context(location=location_id).qty_available        
                if product_qty > max_qty:
                    warning = {
                        'title': _('Warning!'),
                        'message': _('You are trying to consume %s %s of this product, but there are only available '
                                     '%s %s on %s.\nQuantity automatically set to maximum available.')
                               % (product_qty, product.uom_id.name, max_qty, product.uom_id.name, location.name),
                    }
                    product_qty = max_qty
        return {
            'value': {
                'product_qty': product_qty,
                'restrict_lot_id': restrict_lot_id,
                'location_id': location_id
            },
            'warning': warning,
        }