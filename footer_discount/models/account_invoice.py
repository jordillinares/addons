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
#

from openerp import models, fields, api, exceptions
from openerp.addons.decimal_precision import decimal_precision as dp
from openerp.tools.translate import _
import logging


_logger = logging.getLogger(__name__)


class account_invoice(models.Model):

    _inherit = "account.invoice"

    def _get_invoice_line(self, cr, uid, ids, context=None):
        """copy pasted from account_invoice"""
        result = {}
        for line in self.pool.get('account.invoice.line').browse(cr, uid, ids, context=context):
            result[line.invoice_id.id] = True
        return result.keys()

    def _get_invoice_tax(self, cr, uid, ids, context=None):
        """copy pasted from account_invoice"""
        result = {}
        for tax in self.pool.get('account.invoice.tax').browse(cr, uid, ids, context=context):
            result[tax.invoice_id.id] = True
        return result.keys()


    base_amount = fields.Float(string="Base amount",
        compute='_compute_amount',
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
        compute='_compute_amount',
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
        compute='_compute_amount',
        help="Additional discount amount.",
        digits=dp.get_precision('Account'),
    )
    amount_untaxed = fields.Float(string="Untaxed amount",
        compute='_compute_amount',
        help="Amount after discounts and before applying taxes.",
        digits=dp.get_precision('Account'),
    )
    amount_tax = fields.Float(string="Taxes",
        compute='_compute_amount',
        help="Sum of taxes.",
        digits=dp.get_precision('Account'),
    )
    amount_total = fields.Float(string="Total",
        compute='_compute_amount',
        help="The total amount.",
        digits=dp.get_precision('Account'),
    )

    @api.one
    @api.depends('invoice_line.price_subtotal', 'tax_line.amount',
                 'partner_disc', 'add_disc')
    def _compute_amount(self):
        # self.amount_tax = sum(line.amount for line in self.tax_line)
        # self.amount_total = self.amount_untaxed + self.amount_tax
        super(account_invoice, self)._compute_amount()
        # Taxes are applied line by line, we cannot apply a
        # discount on taxes that are not proportional
        if not all(t.type == 'percent' for line in self.invoice_line \
                   for t in line.invoice_line_tax_id):
            raise exceptions.Warning(_('Unable to compute a global '
                                       'discount with non percent-type '
                                       'taxes'))
        cur = self.currency_id
        self.base_amount = sum(line.price_subtotal \
                               for line in self.invoice_line)
        # 1. partner discount
        self.partner_disc_amt = cur.round(self.base_amount *\
                                         (-1 * self.partner_disc / 100))
        base_amt_part_disc = self.base_amount + self.partner_disc_amt
        # 2. additional discount
        self.add_disc_amt = cur.round(base_amt_part_disc *\
                                     (-1 * self.add_disc / 100))
        self.amount_untaxed = base_amt_part_disc + self.add_disc_amt
        self.amount_total = self.amount_untaxed + self.amount_tax

    @api.onchange('partner_id')
    def onchange_partner_id(self, type, partner_id, date_invoice=False,
            payment_term=False, partner_bank_id=False, company_id=False):
        res = super(account_invoice, self).onchange_partner_id(type,
            partner_id, date_invoice=date_invoice, payment_term=payment_term,
            partner_bank_id=partner_bank_id, company_id=company_id)
        if partner_id:
            partner = self.env['res.partner'].browse(partner_id)
            ir_config_param = self.env['ir.config_parameter']
            if type in ('out_invoice', 'out_refund'):
                use_sale_footer_discount = ir_config_param.get_param(
                    'use_sale_footer_discount')
                res['value']['partner_disc'] = use_sale_footer_discount and \
                                    partner.sale_partner_discount or 0.0
            elif type in ('in_invoice', 'in_refund'):
                use_purchase_footer_discount = ir_config_param.get_param(
                    'use_purchase_footer_discount')
            res['value']['partner_disc'] = use_purchase_footer_discount and \
                                partner.purchase_partner_discount or 0.0
        return res

    @api.multi
    def finalize_invoice_move_lines(self, move_lines):
        # Sacado de lp: ~therp-nl/additional-discount/fix_lp1102075_move_lines
        #  debido al bug #41 de indsl.
        # Ha habido que añadirle los dos descuentos, eliminar la referencia
        # a que vals['credit'] o vals['debit'] pudieran ser igual a
        # invoice_browse.amount_total, lo cual no tenía en cuenta el caso de
        # que hubiese distintos plazos de pago y, precisamente por la misma
        # razón, sobrecargar el método move_line_get_item de
        # account.invoice.line, para que a este método
        # finalize_invoice_move_lines llegasen los movs de los pagos
        # calculados desde las líneas de factura, que es lo que hace el
        # mencionado método sobreescrito, pero con la 'trampa' de aplicarle a
        # cada línea los dos descuentos de la fra. (sólo para el cálculo de
        # los apuntes contables, insisto. El subtotal de las líneas
        # y sus impuestos permanecen inalterados por esta sobrecarga).
        """finalize_invoice_move_lines(cr, uid, invoice, move_lines)
        -> move_lines
        Hook method to be overridden in additional modules to verify and
        possibly alter the move lines to be created by an invoice, for
        special cases.
        :param move_lines: list of dictionaries with the account.move.lines
         (as for create())
        :return: the (possibly updated) final move_lines to create for this
         invoice

        Actually move_lines is a list of tuples with each tuple having three
        elements. The third element is the value dictionary used to create one
        line. So move_lines will look like this:
        [(0, 0, {'debit': ......}), (0, 0, {<values for second line>}), ..]

        Taxes are a special problem, because when this function is called,
        the tax move lines have the discount already applied. There is no
        easy way to recogize these lines, therefore we retrieve all tax
        account_id's used and exclude them from being discounted (again).
        """
        precision_obj = self.env['decimal.precision']
        precision = precision_obj.precision_get('Account')
        ait_obj = self.env['account.invoice.tax']
        for record in self:
            partner_disc = record.partner_disc
            add_disc = record.add_disc
            if not partner_disc and not add_disc:
                return move_lines
            # Only if there is any of both additional discounts we will loop
            # over all lines to adjust the amounts. We assume a line will
            # only contain either credit or debit, never both.
            partner_disc_factor = 1.0 - (partner_disc / 100.0)
            add_disc_factor = 1.0 - (add_disc / 100.0)
            balance_credit = True
            total_credit = 0.0
            total_debit = 0.0
            # Get tax account id's
            tax_account_ids = []
            ait_lines = ait_obj.move_line_get(record.id)
            for ait_line in ait_lines:
                tax_account_ids.append(ait_line['account_id'])

            for move_line in move_lines:
                # Check format
                assert len(move_line) > 2, (
                    _('Invalid move line %s') % str(move_line))
                vals = move_line[2]
                # Do not change tax lines (but include them in totals):
                if vals['account_id'] in tax_account_ids:
                    if  vals['debit']:
                        total_debit += vals['debit']
                    if  vals['credit']:
                        total_credit += vals['credit']
                    continue
                # Handle debtor/creditor
                # We don't want to recompute to make sure open amount will
                # be exactly the same as on invoice.
                if record.account_id.id == vals['account_id']:
                    if vals['debit']:
                        assert not vals['credit'], (
                            _('Can not have credit and debit '
                              'in the same move line'))
                        # what if there are several payment terms???
                        # vals['debit'] = invoice_browse.amount_total
                        total_debit += vals['debit']
                    else:
                        assert not vals['debit'], (
                            _('Can not have debit and credit '
                              'in the same move line'))
                        # what if there are several payment terms???
                        # vals['credit'] = invoice_browse.amount_total
                        total_credit += vals['credit']
                        balance_credit = False
                else:
                    if vals['credit']:
                        total_credit += vals['credit']
                    if vals['debit']:
                        total_debit += vals['debit']
                if vals['amount_currency']:
                    # Partner discount
                    vals['amount_currency'] = round(
                        vals['amount_currency'] * partner_disc_factor,
                        precision)
                    # Additional discount
                    vals['amount_currency'] = round(
                        vals['amount_currency'] * add_disc_factor,
                        precision)
                if vals['tax_amount']:
                    # Partner discount
                    vals['tax_amount'] = round(
                        vals['tax_amount'] * partner_disc_factor,
                        precision)
                    # Additional discount
                    vals['tax_amount'] = round(
                        vals['tax_amount'] * add_disc_factor,
                        precision)
            # Check balance
            difference = total_debit - total_credit
            if  abs(difference) > 10 ** -4:
                # Find largest credit or debit amount and adjust for rounding:
                largest_vals = None
                largest_amount = 0.0
                for move_line in move_lines:
                    vals = move_line[2]
                    if balance_credit:
                        if vals['credit'] and vals['credit'] > largest_amount:
                            largest_vals = vals
                    else:
                        if vals['debit'] and vals['debit'] > largest_amount:
                            largest_vals = vals
                assert largest_vals, _('No largest debit or credit found')
                if  balance_credit:
                    largest_vals['credit'] = (
                        largest_vals['credit'] + difference)
                    if largest_vals['tax_amount']:
                        largest_vals['tax_amount'] = (
                            largest_vals['tax_amount'] + difference)
                else:
                    largest_vals['debit'] = (
                        largest_vals['debit'] - difference)
                    if largest_vals['tax_amount']:
                        largest_vals['tax_amount'] = (
                            largest_vals['tax_amount'] - difference)
                _logger.info(_('Modified move line %s to prevent unbalanced '
                    'move with difference %d') % (str(largest_vals),
                                                  difference))
        return move_lines

    @api.model
    def _prepare_refund(self, invoice, date=None, period_id=None,
                        description=None, journal_id=None):
        res = super(account_invoice, self)._prepare_refund(invoice, date=date,
                period_id=period_id, description=description,
                journal_id=journal_id)
        res.update({'partner_disc': invoice.partner_disc,
                    'add_disc': invoice.add_disc,
                    })
        return res


class account_invoice_line(models.Model):

    _inherit = 'account.invoice.line'

    def move_line_get_item(self, line):
        # Este módulo original de 'additional_discount' junto con la rama
        # ~therp-nl/additional-discount/fix_lp1102075_move_lines
        # que arregla algunas cosas de los apuntes cuando hay descuentos,
        # está muy bien, pero faltaba probar CON VARIOS PAGOS (30,60,90 días,
        # por ejemplo), y en esos casos no funcionaba porque los apuntes
        # correspondientes a los pagos se basaban siempre en la B.I. antes de
        # los descuentos. Como lo hacía por línea de factura, ha habido que
        # aplicar, para el cálculo de cada uno de los pagos solamente, es
        # decir, sin efecto sobre el subtotal de cada línea de factura, el
        # mismo descuento para cada línea de factura que los aplicados en la
        # cabecera. Así ya funciona y es capaz de calcular bien los pagos y
        # estimar bien el importe pendiente.
        res = super(account_invoice_line, self).move_line_get_item(line)
        partner_disc = line.invoice_id.partner_disc
        add_disc = line.invoice_id.add_disc
        precision_obj = self.env['decimal.precision']
        precision = precision_obj.precision_get('Account')
        partner_disc_factor = 1.0 - (partner_disc / 100.0)
        add_disc_factor = 1.0 - (add_disc / 100.0)
        res['price'] = round(line.price_subtotal * partner_disc_factor,
                             precision)
        res['price'] = round(res['price'] * add_disc_factor,
                             precision)
        return res


class account_invoice_tax(models.Model):

    _inherit = 'account.invoice.tax'

    def compute(self, invoice):
        tax_grouped = super(account_invoice_tax, self).compute(invoice)
        tax_obj = self.env['account.tax']
        currency = invoice.currency_id.with_context(
            date=invoice.date_invoice or fields.Date.context_today(invoice))
        # Recalculation of taxes (with discounts)
        tax_ids = set([key[0] for key in tax_grouped])
        taxes = tax_obj.browse(tax_ids)
        if taxes and not all(t.type == 'percent' for t in taxes):
            raise exceptions.Warning(_('Unable to compute a global discount '
                                       'with non percent-type taxes'))
        partner_disc = invoice.partner_disc
        add_disc = invoice.add_disc
        for line in tax_grouped:
            for key in ('tax_amount', 'base_amount', 'amount', 'base'):
                val = tax_grouped[line][key]
                tax_grouped[line][key] = currency.round(
                    val * (1.0 - partner_disc / 100.0))
                tax_grouped[line][key] = currency.round(
                    tax_grouped[line][key] * (1.0 - add_disc / 100.0))
        return tax_grouped