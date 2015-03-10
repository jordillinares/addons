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

from openerp import models, fields, api, tools
import openerp.addons.decimal_precision as dp


class product_template(models.Model):

    _inherit = 'product.template'

    lot_creation_mode = fields.Selection([('manual', 'Manual'),
                                          ('auto', 'Auto')],
                                         'Lot numbering mode', default='auto',
                                         help="Manual: You can freely type "
                                         "any text to code a new lot, assuming"
                                         " lot with that code doesn't exist "
                                         "yet."
                                         "\nAuto: a specific sequence is used "
                                         "to automatically create every new "
                                         "lot number.")
    lot_sequence = fields.Many2one('ir.sequence', 'Lot generation sequence',
                                   help="Create a new sequence pattern and "
                                   "link it to this product to have new lot "
                                   "numbers automatically created when "
                                   "receiving or manufacturing this product.")
