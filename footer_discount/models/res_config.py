# -*- encoding: utf-8 -*-
####################################################################
#
#    OpenERP, Open Source Management Solution
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


class sale_configuration(models.TransientModel):

    _inherit = 'sale.config.settings'

    group_discount_sale_footer = fields.Boolean(
        string="Use sale footer discount",
        implied_group='footer_discount.group_discount_sale_footer',
        help="Allows you to set a footer discount on your sale documents "
             "(orders and invoices).",
        default=False,
    )

    @api.onchange('group_discount_sale_footer')
    def onchange_group_discount_sale_footer(self):
        ir_config_param = self.env['ir.config_parameter']
        ir_config_param.set_param('use_sale_footer_discount',
                                  self.group_discount_sale_footer and \
                                  "1" or "0",
                                  groups=['base.group_system'])


class purchase_config_settings(models.TransientModel):

    _inherit = 'purchase.config.settings'

    group_discount_purchase_footer = fields.Boolean(
        string="Use purchase footer discount",
        implied_group='footer_discount.group_discount_purchase_footer',
        help="Allows you to set a footer discount on your sale documents "
             "(orders and invoices).",
        default=False,
    )

    @api.onchange('group_discount_purchase_footer')
    def onchange_group_discount_purchase_footer(self):
        ir_config_param = self.env['ir.config_parameter']
        ir_config_param.set_param('use_purchase_footer_discount',
                                  self.group_discount_purchase_footer and \
                                  "1" or "0",
                                  groups=['base.group_system'])
