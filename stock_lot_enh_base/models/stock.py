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


from openerp import models, fields, api
from openerp.exceptions import except_orm
from openerp.tools.translate import _
import time
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools.float_utils import float_compare, float_round


class stock_quant(models.Model):
    
    _inherit = 'stock.quant'
    
    @api.model
    def _quants_get_order(self, location, product, quantity, domain=[], orderby='in_date'):
        ''' Implementation of removal strategies
            If it can not reserve, it will return a tuple (None, qty)
        '''
        context = self._context
        domain += location and [('location_id', 'child_of', location.id)] or []
        domain += [('product_id', '=', product.id)]
        if context.get('force_company'):
            domain += [('company_id', '=', context.get('force_company'))]
        else:
            domain += [('company_id', '=', self.env.user.company_id.id)]
        res = []
        offset = 0
        while float_compare(quantity, 0, precision_rounding=product.uom_id.rounding) > 0:
            quants = self.search(domain, order=orderby, limit=10, offset=offset)
            if not quants:
                res.append((None, quantity))
                break
            for quant in quants:
                # Here we implement a change that affects FEFO removal strategy (orderby = 'removal_date, in_date, id'):
                # If a quant is already expired (removal_date < current date), skip it and send a warning message.
                if orderby == 'removal_date, in_date, id':
                    if quant.removal_date and quant.removal_date < time.strftime(DEFAULT_SERVER_DATETIME_FORMAT):
                        if 'chatter_model' in context and context.get('chatter_model', False) and 'chatter_id' in context and context.get('chatter_id', False):
                            model = self.env[context['chatter_model']]
                            try: # maybe our active model class does not inherit from 'mail.thread'
                                record = model.browse(context['chatter_id'])
                                message = _("A quant of lot %s has been ignored because it seems to have expired.\nPlease check it and, if needed, remove the whole lot from stock.") % (quant.lot_id.name,)
                                record.message_post(message, _('An expired lot must be retired!'), context=context)
                            finally:
                                # these pops throw an error: raise NotImplementedError("'pop' not supported on frozendict")
                                #self._context.pop('chatter_model')
                                #self._context.pop('chatter_id')
                                pass
                        continue
                rounding = product.uom_id.rounding
                if float_compare(quantity, abs(quant.qty), precision_rounding=rounding) >= 0:
                    res += [(quant, abs(quant.qty))]
                    quantity -= abs(quant.qty)
                elif float_compare(quantity, 0.0, precision_rounding=rounding) != 0:
                    res += [(quant, quantity)]
                    quantity = 0
                    break
            offset += 10
        return res


class stock_production_lot(models.Model):
    
    _inherit = 'stock.production.lot'
    
    @api.model
    def _get_lotname(self):
        context = self._context
        if context.get('product_id', False):
            product = self.env['product.product'].browse(context['product_id'])
            if product.lot_creation_mode == 'manual':
                return False
            elif product.lot_creation_mode == 'auto' and product.lot_sequence:
                return self.env['ir.sequence'].get_id(product.lot_sequence.id)
        return self.env['ir.sequence'].get_id('stock.lot.serial', code_or_id='code')
    
    name = fields.Char('Lot number', required=True, help="Unique lot/serial alphanumeric code.",
                       index=True, copy=False, default=_get_lotname)
    origin = fields.Char('Origin', help="Reference of the document in which that lot was created.", index=True)
    destination = fields.Char('Destination', size=200, help="Reference of the the documents in which that lot was used.", index=True)
    
    
class stock_transfer_details_items(models.TransientModel):

    _inherit = 'stock.transfer_details_items'
    
    @api.multi
    def quick_lot_create(self):
        for detail in self:
            if detail.product_id and detail.product_id.lot_creation_mode == 'auto' and \
                                    (detail.product_id.track_incoming or \
                                    detail.product_id.track_outgoing or \
                                    detail.product_id.track_all):
                self.lot_id = self.env['stock.production.lot'].with_context(product_id=detail.product_id.id).create({})
            else:
                raise except_orm(_('Warning!'),
                                 _('Product has not lot tracking enabled, or has lot creation mode set '
                                   'to \'manual\'. A new lot number won\'t be automatically created.'))
        if self and self[0]:
            return self[0].transfer_id.wizard_view()    
    