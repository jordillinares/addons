# -*- encoding: utf-8 -*-
####################################################################
#
# OpenERP, Open Source Management Solution
#    Copyright (C) 2004- 2015 Tiny SPRL (http://tiny.be). All Rights Reserved
#
#    This module,
#    Copyright (C) 2015 Jordi Llinares <bigandopen@bigandopen.com>
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
#####################################################################

from openerp import models, fields, api


class stock_picking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def _get_invoice_vals(self, key, inv_type, journal_id, move):
        cr, uid, context = self.env.args
        vals = super(stock_picking, self._model)._get_invoice_vals(cr,
                                                            uid,
                                                            key,
                                                            inv_type,
                                                            journal_id,
                                                            move,
                                                            context=context)
        if inv_type in ('out_invoice', 'out_refund'):
            if move.picking_id and 'sale_id' in move.picking_id._columns and \
                    move.picking_id.sale_id:
                vals.update({'partner_disc': move.picking_id.sale_id \
                                                 .partner_disc or 0.0,
                             'add_disc': move.picking_id.sale_id \
                                                 .add_disc or 0.0,
                             })
        elif inv_type in ('in_invoice', 'in_refund'):
            if move.purchase_line_id and move.purchase_line_id.order_id:
                vals.update({'partner_disc': move.purchase_line_id.order_id \
                                                 .partner_disc or 0.0,
                             'add_disc': move.purchase_line_id.order_id \
                                                 .add_disc or 0.0
                             })
        return vals