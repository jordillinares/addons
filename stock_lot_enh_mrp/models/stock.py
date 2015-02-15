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
    
    # We need 'production_id' to be copy=True for split moves to inherit production_id from original move,
    # because in our version of MRP we can manually produce a smaller qty than the original move's, and without
    # copy=True, split move would be created, but not be shown as production pending.
    production_id = fields.Many2one('mrp.production', 'Production Order for Produced Products', select=True, copy=True)
    
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
                if 'consume' in context and context.get('consume', False):
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
                                                                         _('Raw material consume'), context=context)
                elif 'produce' in context and context.get('produce', False):
                    production_ids = production_obj.search(cr, uid, [('move_created_ids', 'in', [move.id])])
                    production_id = production_ids and production_ids[0] or False
                    if production_id:
                        production = production_obj.browse(cr, uid, production_id, context=context)
                        add_origin = ""
                        if production:
                            add_origin = production.name
                        for lot in move.lot_ids:
                            message = _("%s %s of lot %s of %s have been produced.") % (move.product_qty,
                                                                                              move.product_uom.name,
                                                                                              lot.name, name)
                            if add_origin:
                                origin_list = []
                                if lot.origin: origin_list += lot.origin.split(", ")
                                if add_origin not in origin_list:  origin_list.append(add_origin)
                                origin = ", ".join(origin_list)
                                lot_obj.write(cr, uid, [lot.id], {'origin': origin, })
                            else:
                                message = _("%s %s of %s have been produced.") % (move.product_qty,
                                                                                  move.product_uom.name,
                                                                                  name)
                            self.pool.get('mrp.production').message_post(cr, uid, [production_id], message,
                                                                         _('Manufactured product'), context=context)
                            # In our manual consume/produce version, we didn't use 'consumed_for' until here. But here
                            # we'll assign all already consumed materials that do not have a value in 'consumed_for'
                            # to this production move.
                            consume_parent_move_ids = [x.id for x in production.move_lines2 if not x.consumed_for]
                            self.write(cr, uid, consume_parent_move_ids, {'consumed_for': move.id}, context=context)
        return res
    

class stock_production_lot(models.Model):
    
    _inherit = 'stock.production.lot'
    
    def init(self, cr):
        """
        Create pl/pgqsl functions for upstream and downstream lot traceability on module installation"
        """
        # Check if pl/pgsql language is present in the DB. If not, install it.
        cr.execute("select * from pg_language where lanname = 'plpgsql'")
        if not cr.rowcount:
            cr.execute("create language 'plpgsql'")
            
        # Check if custom SQL type 'prodlot_hierarchy' is present in the DB. If not, create it.
        # If it exists, delete functions, delete type and recreate all (it's unnecessary on a 
        # production environment, but very useful while adjusting SQL functions).
        cr.execute("SELECT 1 FROM pg_type WHERE typname = 'lot_hierarchy';")
        if cr.rowcount:
            cr.execute("""SELECT 1 FROM pg_proc WHERE proname = 'trace_lot_up' AND pronargs=1;""")
            if cr.rowcount:
                cr.execute("""DROP FUNCTION trace_lot_up(integer);""")
            cr.execute("""SELECT 1 FROM pg_proc WHERE proname = 'trace_lot_down' AND pronargs=1;""")
            if cr.rowcount:
                cr.execute("""DROP FUNCTION trace_lot_down(integer);""")
            cr.execute("""DROP TYPE lot_hierarchy;""")
        
        cr.execute("""
            CREATE TYPE lot_hierarchy AS (
                parent_id integer,
                id integer
        );""")  
        
        cr.execute("""
            CREATE OR REPLACE FUNCTION trace_lot_up(integer)
            RETURNS SETOF lot_hierarchy
            AS
            $BODY$
                DECLARE
                    parent_lot record;
                    eachlot record;
                BEGIN
                    FOR parent_lot IN
                        SELECT
                            parent_sm.restrict_lot_id AS this_lot_id,
                            sm.restrict_lot_id AS related_lot_id
                        FROM
                            stock_move sm,
                            stock_move parent_sm,
                            stock_production_lot spl
                        WHERE
                            parent_sm.consumed_for = sm.id
                        AND
                            parent_sm.restrict_lot_id = $1
                        AND
                            sm.restrict_lot_id = spl.id
                        AND
                            sm.state = 'done'
                        AND
                            parent_sm.state = 'done'
                    LOOP                
                        FOR eachlot IN
                            SELECT
                                *
                            FROM
                                trace_lot_up(parent_lot.related_lot_id)
                        LOOP
                            return next eachlot;
                        END LOOP;
                        return next parent_lot;
                    END LOOP;    
                END;
            $BODY$
            LANGUAGE 'plpgsql';
        """)  
        
        cr.execute("""
            CREATE OR REPLACE FUNCTION trace_lot_down(integer)
            RETURNS SETOF lot_hierarchy
            AS
            $BODY$
                DECLARE
                    parent_lot record;
                    eachlot record;
                BEGIN
                    FOR parent_lot IN
                        SELECT
                            parent_sm.restrict_lot_id AS related_lot_id,
                            sm.restrict_lot_id AS this_lot_id
                        FROM
                            stock_move sm,
                            stock_move parent_sm,
                            stock_production_lot spl
                        WHERE
                            parent_sm.consumed_for = sm.id
                        AND
                            sm.restrict_lot_id = $1
                        AND
                            parent_sm.restrict_lot_id = spl.id
                        AND
                            sm.state = 'done'
                        AND
                            parent_sm.state = 'done'
                    LOOP                
                        FOR eachlot IN
                            SELECT
                                *
                            FROM
                                trace_lot_down(parent_lot.related_lot_id)
                        LOOP
                            return next eachlot;
                        END LOOP;
                        return next parent_lot;
                    END LOOP;    
                END;
            $BODY$
            LANGUAGE 'plpgsql';
        """)
    
    def _child_compute(self):
        for record in self:
            self.env.cr.execute('SELECT id FROM trace_lot_up(%s) WHERE parent_id = %s' % (record.id, record.id))
            data = self.env.cr.fetchall()
            child_ids = [x[0] for x in data if not x[0] in [y.id for y in self]]
            record.child_complete_ids = self.browse(child_ids)
    
    def _parent_compute(self):
        for record in self:
            self.env.cr.execute('SELECT parent_id FROM trace_lot_down(%s) WHERE id = %s' % (record.id, record.id))
            data = self.env.cr.fetchall()
            parent_ids = [x[0] for x in data if not x[0] in [y.id for y in self]]
            record.parent_complete_ids = self.browse(parent_ids)
    
    
    child_complete_ids = fields.Many2many(comodel_name='stock.production.lot', string="Lot hierarchy upstream", compute=_child_compute)
    parent_complete_ids = fields.Many2many(comodel_name='stock.production.lot', string="Lot hierarchy upstream", compute=_parent_compute)