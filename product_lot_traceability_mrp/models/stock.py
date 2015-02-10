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




class stock_move(models.Model):
    
    _inherit = 'stock.move'
    
    def action_consume(self, cr, uid, ids, product_qty, location_id=False, restrict_lot_id=False,
                       restrict_partner_id=False, consumed_for=False, context=None):
        product_obj = self.pool.get('product.product')
        production_obj = self.pool.get('mrp.production')
        lot_obj = self.pool.get('stock.production.lot')
        res = super(stock_move, self).action_consume(cr, uid, ids, product_qty, location_id=location_id,
                                                     restrict_lot_id=restrict_lot_id, restrict_partner_id=restrict_partner_id,
                                                     consumed_for=consumed_for, context=context)              
        for move in self.browse(cr, uid, ids, context=context):
            for (id, name) in product_obj.name_get(cr, uid, [move.product_id.id]):
                production_ids = production_obj.search(cr, uid, [('move_lines', 'in', [move.id])])
                production_id = production_ids and production_ids[0] or False
                if production_id:
                    production = production_obj.browse(cr, uid, production_id, context=context)
                    add_destination = ""
                    if production:
                        add_destination = production.name
                for lot in move.lot_ids:
                    message = _("%s %s of lot %s of %s have been consumed.") % (move.product_qty,
                                                                                      move.product_uom.name,
                                                                                      lot.name, name)
                    if add_destination:
                        destination_list = []
                        if lot.destination: destination_list += lot.destination.split(", ")
                        if add_destination not in destination_list:  destination_list.append(add_destination)
                        destination = ", ".join(destination_list)
                        lot_obj.write(cr, uid, [lot.id], {'destination': destination, })
                    else:
                        message = _("%s %s of %s have been consumed.") % (move.product_qty,
                                                                          move.product_uom.name,
                                                                          name)
                    self.pool.get('mrp.production').message_post(cr, uid, [production_id], message,
                                                                 _('Raw material consumption'), context=context)
        return res
    
    