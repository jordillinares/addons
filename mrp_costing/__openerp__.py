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

{
    'name': 'MRP Production costs (no analytics)',
    'version': '1.0',
    'author': 'Jordi Llinares López - bigandopen@bigandopen.com',
    'category': 'Manufacturing',
    'summary': 'Manufacturing costs calculation without using analytic accounting.',
    'complexity': 'easy',
    'description': """
MRP Production costs (no analytics)
===================================

This module allows to calculate production costs for your manufactured products without
need to use analytic accounting, which is more flexible, but sometimes is not what the
customer thinks his company needs to keep track of production costs at a glance.

Calculations are essentially based on the definition of a set of cost concepts in the
product and the workcenter. The workcenter allows to define costs per product. From each
workcenter in a route, unitary production costs are calculated for a given product. Cost
calculation for this product is completed adding the cost concepts defined on its form.
This way, you get the standard cost of a manufactured product.

Finally, in a given manufacturing order of that product you can specify each operation
duration with an accuracy of up to a second (thanks to my module 'float_time_hms'). From
the computation of real production times, and the real consumes and production, you'll
easily get the real cost of a product in an order.

# TODO:
A costing report is available for each done manufacturing order, and you can set the
standard cost for a product from a given manufacturing order. Odoo will keep track of
the origin MO, the assignation date and responsible person.
""",
    'website': 'http://www.bigandopen.com',
    'depends': [
        'product',
        'mrp',
        'stock',
        'stock_account',
    ],
    'data': [
        # Security

        # Data
        'data/mrp_costing_data.xml',

        # Views
        'views/product_view.xml',
        'views/mrp_view.xml',
    ],
    'conflicts': [
        'product_extended',
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
}
