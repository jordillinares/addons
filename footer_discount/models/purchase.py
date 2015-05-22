# -*- encoding: utf-8 -*-
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

from openerp import models, fields, api, exceptions
from openerp.tools.translate import _
from openerp.addons.decimal_precision import decimal_precision as dp


class purchase_order(models.Model):

    _inherit = 'purchase.order'

    base_amount = fields.Float(string="Base amount",
        compute='_amount_all',
        help="Sum of all lines subtotals",
        digits=dp.get_precision('Account'),
    )
    partner_disc = fields.Float(string="Partner discount(%)",
        digits=(4,2),
        readonly=True,
        states={'draft': [('readonly', False)]},
        default=0.0,
    )
    partner_disc_amt = fields.Float(string="Partner discount",
        compute='_amount_all',
        help="Partner discount amount.",
        digits=dp.get_precision('Account'),
    )
    add_disc = fields.Float(string="Additional discount(%)",
        digits=(4,2),
        readonly=True,
        states={'draft': [('readonly', False)]},
        default=0.0,
    )
    add_disc_amt = fields.Float(string="Additional discount",
        compute='_amount_all',
        help="Additional discount amount.",
        digits=dp.get_precision('Account'),
    )
    amount_untaxed = fields.Float(string="Untaxed amount",
        compute='_amount_all',
        help="Amount after discounts and before applying taxes.",
        digits=dp.get_precision('Account'),
    )
    amount_tax = fields.Float(string="Taxes",
        compute='_amount_all',
        help="Sum of taxes.",
        digits=dp.get_precision('Account'),
    )
    amount_total = fields.Float(string="Total",
        compute='_amount_all',
        help="The total amount.",
        digits=dp.get_precision('Account'),
    )

    @api.depends('order_line', 'partner_disc', 'add_disc',
                 'order_line.price_unit', 'order_line.taxes_id',
                 'order_line.product_qty',
                 'order_line.price_subtotal')
    def _amount_all(self):
        cr, uid, context = self.env.args
        cur_obj = self.env['res.currency']
        res = super(purchase_order, self._model)._amount_all(cr,
                                                         uid,
                                                         self._ids,
                                                         False,
                                                         False,
                                                         context=context)
        for record in self:
            # Taxes are applied line by line, we cannot apply a
            # discount on taxes that are not proportional
            if not all(t.type == 'percent' for line in record.order_line \
                       for t in line.taxes_id):
                raise exceptions.Warning(_('Unable to compute a global '
                                           'discount with non percent-type '
                                           'taxes'))
            cur = record.pricelist_id.currency_id
            record.base_amount = sum(line.price_subtotal \
                                     for line in record.order_line)
            # 1. partner discount
            record.partner_disc_amt = cur.round(record.base_amount *\
                                            (-1 *record.partner_disc / 100))
            base_amt_part_disc = record.base_amount + record.partner_disc_amt
            # 2. additional discount (over amount_untaxed_with_partner_discount)
            record.add_disc_amt = cur.round(base_amt_part_disc *\
                                            (-1 * record.add_disc / 100))
            record.amount_untaxed = base_amt_part_disc + record.add_disc_amt
            amt_tax_part_disc = cur.round(res[record.id]['amount_tax'] *\
                              (100.0 - (record.partner_disc or 0.0)) / 100.0)
            record.amount_tax = cur.round(amt_tax_part_disc *\
                              (100.0 - (record.add_disc or 0.0)) / 100.0)
            record.amount_total = record.amount_untaxed + record.amount_tax

    @api.onchange('partner_id')
    def onchange_partner_id(self, partner_id):
        res = super(purchase_order, self).onchange_partner_id(partner_id)
        if partner_id:
            partner = self.env['res.partner'].browse(partner_id)
            ir_config_param = self.env['ir.config_parameter']
            use_purchase_footer_discount = ir_config_param.get_param(
                'use_purchase_footer_discount')
            res['value']['partner_disc'] = use_purchase_footer_discount and \
                                partner.purchase_partner_discount or 0.0
        return res

    @api.multi
    def action_invoice_create(self):
        """
        Add both discounts to the invoice **AFTER** creation (that's why
        we don't make use of _prepare_invoice),
        and recompute the total.
        """
        # CAUTION: Due to the structure of the original method, which
        # works on a recordset but returns an unique invoice id instead of
        # a mapping of saleorder-invoice, we cannot inherit method and
        # modify + recompute every already-created invoice, as we would
        # have done.
        # Instead, we must fully overwrite this method, so please keep notice
        # of possible incompatibilities of this module with others that
        # possibly inerit or rewrite this method.
        inv_obj = self.env['account.invoice']
        inv_line_obj = self.env['account.invoice.line']
        res = False
        for order in self:
            self.env.context.pop('force_company', None)
            if order.company_id.id != self.env.user.company_id.id:
                #if the company of the document is different than the current
                # user company, force the company in the context then re-do a
                # browse to read the property fields for the good company.
                order = order.with_context(force_company=order.company_id.id)
                # For other models browses that share the same context
                self.env.context.update({'force_company': order.company_id.id})

            # generate invoice line correspond to PO line and link that to
            # created invoice (inv_id) and PO line
            inv_lines = []
            for po_line in order.order_line:
                acc_id = self._choose_account_from_po_line(po_line)
                inv_line_data = self._prepare_inv_line(acc_id, po_line)
                inv_line = inv_line_obj.create(inv_line_data)
                inv_lines.append(inv_line.id)
                po_line.write({'invoice_lines': [(4, inv_line.id)]})

            # get invoice data and create invoice
            inv_data = self._prepare_invoice(order, inv_lines)
            inv = inv_obj.create(inv_data)

            inv.partner_disc = order.partner_disc or 0.0
            inv.add_disc = order.add_disc or 0.0
            # compute the invoice
            inv_obj.button_compute([inv.id], set_total=True)
            # Link this new invoice to related purchase order
            order.write({'invoice_ids': [(4, inv.id)]})
            res = inv.id
        return res
