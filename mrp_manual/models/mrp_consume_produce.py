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
     
    removal_strategy = fields.Char(string='Removal strategy')
    
    @api.onchange('product_id')
    def onchange_product_id(self):
        domain = {}
        context = self._context
        move = self.env['stock.move'].browse(context['active_id'])
        self.removal_strategy = self.location_id.get_removal_strategy(self.location_id, self.product_id).upper()
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



class stock_move_produce(models.TransientModel):

    _name = 'stock.move.produce'
    _description = 'Produce product'
    
    product_id = fields.Many2one('product.product', 'Product', required=True, select=True)
    product_qty = fields.Float('Quantity', digits_compute=dp.get_precision('Product Unit of Measure'), required=True)
    product_uom = fields.Many2one('product.uom', 'Product Unit of Measure', required=True)
    location_id = fields.Many2one('stock.location', 'Location', required=True)
    location_dest_id = fields.Many2one('stock.location', 'Destination loc.', required=True)
    lot_id = fields.Many2one('stock.production.lot', 'Lot')

    #TOFIX: product_uom should not be different from product's default uom. Qty should be converted to UOM of original move line before being produced
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(stock_move_produce, self).default_get(cr, uid, fields, context=context)
        move = self.pool.get('stock.move').browse(cr, uid, context['active_id'], context=context)
        if 'product_id' in fields:
            res.update({'product_id': move.product_id.id})
        if 'product_uom' in fields:
            res.update({'product_uom': move.product_uom.id})
        if 'product_qty' in fields:
            res.update({'product_qty': move.product_uom_qty})
        if 'location_id' in fields:
            res.update({'location_id': move.location_id.id})
        if 'location_dest_id' in fields:
            res.update({'location_dest_id': move.location_dest_id.id})
        return res    
    
    @api.multi
    def quick_lot_create(self):
        for detail in self:
            if detail.product_id and detail.product_id.lot_creation_mode == 'auto' and \
                                    (detail.product_id.track_production or \
                                    detail.product_id.track_all):
                detail.lot_id = self.env['stock.production.lot'].with_context(product_id=detail.product_id.id).create({})
            else:
                raise except_orm(_('Warning!'),
                                 _('Product lot tracking is not enabled, or lot creation mode is '
                                   '\'manual\'\n. A new lot number won\'t be automatically created.'))
        if self and self[0]:
            return self[0].wizard_view()

    @api.multi
    def wizard_view(self):
        view = self.env.ref('mrp_kms.view_stock_move_produce_wizard')
        return {
            'name': _('Consume Move'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'stock.move.produce',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': self.ids[0],
            'context': self.env.context,
        }
    
    @api.multi
    def do_move_produce(self):
        context = self._context
        move_ids = context['active_ids']
        move_obj = self.env['stock.move']
        for record in self:
            if move_ids and move_ids[0]:
                move = move_obj.browse(move_ids[0])
                # Yes, we create a wizard for production very similar to consume wizard, but at the end of both wizards
                # we use the same 'action_consume' method.
                move.action_consume(record.product_qty, record.location_id.id, restrict_lot_id=record.lot_id.id)
        return {'type': 'ir.actions.act_window_close'}
