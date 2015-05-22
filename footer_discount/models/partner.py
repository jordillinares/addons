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


class res_partner(models.Model):

    _inherit = 'res.partner'

    purchase_partner_discount = fields.Float(string="Purchase discount(%)",
        digits=(4,2),
        help="Default suggested discount for this partner on purchase "
             "orders and incoming invoices. Can be overwritten on every "
             "document.",
        default=0.0,
    )
    sale_partner_discount = fields.Float(string="Sale discount(%)",
        digits=(4,2),
        help="Default suggested discount for this partner on sales "
             "orders and outgoing invoices. Can be overwritten on every "
             "document.",
        default=0.0,
    )
