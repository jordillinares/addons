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

{
    'name': 'MRP Production - real cost',
    'version': '1.0',
    'author': 'Jordi Llinares López - bigandopen@bigandopen.com',
    'category': 'Manufacturing',
    'summary': 'Manufacturing order real cost costs calculation without using analytic accounting.',
    'complexity': 'easy',
    'description': """
MRP Production real cost (no analytics)
=======================================

This module is based on (and needs) my other module 'mrp_costing'. It  allows
to calculate cost of each production order for your manufactured products without
need to use analytic accounting.

Please read comment on 'mrp_costing' module to get familiar with how different
cost fields are computed.
""",
    'website': 'http://www.bigandopen.com',
    'depends': [
        'product',
        'mrp',
        'stock',
        'stock_account',
        'mrp_costing',
        'float_field_color',
    ],
    'data': [
        # Security

        # Data

        # Views
        'static/src/views/mrp_costing_real.xml',
        'views/mrp_view.xml',
    ],
    'conflicts': [
        'product_extended',
        'mrp_byproduct',
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
}