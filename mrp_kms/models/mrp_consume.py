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
from openerp.addons.decimal_precision import decimal_precision as dp

    
    

class stock_move_consume(models.TransientModel):
      
    _inherit = 'stock.move.consume'
    
    @api.onchange('product_id')
    def onchange_product_id(self):
        domain = {}
        context = self._context
        move = self.env['stock.move'].browse(context['active_id'])   
        if move.reserved_quant_ids:
            suggested_quant = move.reserved_quant_ids[0]
            self.product_qty = suggested_quant.qty
            self.restrict_lot_id = suggested_quant.lot_id.id
            # domain for lot_id: Do not show lots with no stock on location_id!
            # Please note 'ordered_quants_info' variable includes not only reserved quants for the movement, but also
            # all quants of the product that are not reserved and have a lot_id, thus being able to be selected here.
            ordered_quants_info = self.env['stock.quant'].quants_get(move.location_id, move.product_id, suggested_quant.qty, domain=['&','|',('reservation_id','=',move.id),('reservation_id','=',False),('qty','>',0)])
            lot_ids = []
            for quant, qty in ordered_quants_info:
                if quant.lot_id and quant.lot_id.id not in lot_ids:
                    lot_ids.append(quant.lot_id.id)
            if lot_ids:
                domain['restrict_lot_id'] = [('id', 'in', lot_ids)]
        return {
            'domain': domain,
        }      
        
    @api.onchange('restrict_lot_id')
    def onchange_lot_id(self):
        context = self._context
        warning = {}
        move = self.env['stock.move'].browse(context['active_id'])
        if self.restrict_lot_id:
            max_qty = move.product_id.with_context(location=move.location_id.id, lot_id=self.restrict_lot_id.id).qty_available        
            if self.product_qty > max_qty:
                self.product_qty = max_qty
                
    @api.onchange('product_qty')
    def onchange_product_qty(self):
        context = self._context
        warning = {}
        move = self.env['stock.move'].browse(context['active_id'])
        if self.restrict_lot_id:
            max_qty = move.product_id.with_context(location=move.location_id.id, lot_id=self.restrict_lot_id.id).qty_available        
            if self.product_qty > max_qty:
                warning = {
                    'title': _('Warning!'),
                    'message': _('You are trying to consume %s %s of lot %s, but there are only available '
                                 '%s %s on %s.\nQuantity automatically set to maximum available.')
                           % (self.product_qty, move.product_id.uom_id.name, self.restrict_lot_id.name, max_qty, move.product_id.uom_id.name, move.location_id.name),
                }
                self.product_qty = max_qty
        return {
            'warning': warning,
        }

