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

Essentially, this module adds several cost fields and a new costing method to the
product's form. Fields are 'Material cost', 'Production cost' and 'Other costs'.
Both three fields are calculated (the latter from a 'other costs' table).

The new costing method 'Computed M+P+A' makes the original 'standard_price' field
behave like a fake 'calculated field'. This way, you can manually define a standard
price for raw materials and other products (through selecting 'standard cost' costing
method), or you can make Odoo calculate product's costs on several concepts (materials,
production and other costs). Whenever you change a route, a BoM, or a raw material cost,
all depending costs will be recalculated.

Material cost is computed for a product from the components of the BoM with the lowest
sequence number for that product.

Concerning production costs, they can be defined for a workcenter on a per-product basis.
For each workcenter in a route, unitary production costs are calculated for a given product.

Cost calculation of a product is completed adding the 'other cost concepts' defined on its
form view.

The sum of these three costs gives you get the standard cost of a manufactured product.

This module keeps into account product variants and their respective costs definition.
At the variant level, material cost is calculated using the original _bom_find method.
This BoM is also used to compute the production cost of the variant.

At the template level, calculation is a bit more tricky: material cost is always done
from the BoM with the lowest sequence number (by now, it does not filter BoMs by validity
dates, unlike _find_bom. It's a # TODO). If the selected bom has also a variant linked,
production cost is taken from there. Otherwise, for each workcenter in the route linked
to the BoM, the cost is calculated from the cost definition with the lowest sequence
number among all the cost definitions for all variants of the product template.
That implies that sequences for mrp.workcenter.product.cost are only relevant when
a) you use product variants, and
b) a product's (template) BoM is not linked to a variant or a workcenter is used by
   several variants.

# TODO:
Finally, in a given manufacturing order of a product you can specify each operation
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
        'mrp_byproduct',
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
}
