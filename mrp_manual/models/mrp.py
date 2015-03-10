# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2012 Tiny SPRL (http://tiny.be). All Rights Reserved
#
#    This module,
#    Copyright (C) 2015 Jordi Llinares López - bigandopen@bigandopen.com
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

from openerp import models, fields, api
from openerp.addons.decimal_precision import decimal_precision as dp


class mrp_production(models.Model):

    _inherit = 'mrp.production'

    @api.one
    def _consume_or_produce_pending(self):
        self.consume_or_produce_pending = not self.test_production_done()

    @api.one
    def _produced_qty(self):
        self.produced_qty = self._get_produced_qty(self)

    consume_or_produce_pending = fields.Boolean('Has pending moves',
                                                compute=
                                                _consume_or_produce_pending,
                                                help='Technical field that '
                                                'calculates if production has'
                                                ' pending moves')
    # consumed and produced fields must not show cancelled moves
    move_lines2 = fields.One2many('stock.move',
                                  'raw_material_production_id',
                                  'Consumed products',
                                  domain=[('state', 'in', ('done',))])
    move_created_ids2 = fields.One2many('stock.move',
                                        'production_id',
                                        'Produced products',
                                        domain=[('state', 'in', ('done',))])
    produced_qty = fields.Float('Produced qty.',
                                digits_compute=
                                dp.get_precision('Product Unit of Measure'),
                                compute=_produced_qty)

    @api.one
    def action_produce(self, production_qty, production_mode, wiz=False,
                       context=None):
        # Invalidate action_produce method (see module description).
        return True

    @api.multi
    def action_production_end(self):
        for record in self:
            # Cancel pending consumes and productions
            moves = record.move_lines + record.move_created_ids
            moves.action_cancel()
        return super(mrp_production, self).action_production_end()
