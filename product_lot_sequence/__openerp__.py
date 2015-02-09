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

{
    'name' : 'Product lot sequence',
    'version' : '1.0',
    'author' : 'KM Sistemas de información, S.L.',
    'category' : 'Stock/Traceability',
    'summary': '',
    'complexity': 'easy',
    'description' : """
Product lot sequence
====================
    
This module adds the possibility to specify a sequence for a product's lot, be it a received
product or a manufactured product.

It also adds a button in the 'transfer details wizard' that allows to create a new lot number
on the fly without needing to open a new popup. Please note it only works when product's lot
creation mode is set to 'auto' and product tracking is enabled any of these three ways: incoming,
outgoing or all.

If a sequence has not been specified for the product and it has creation mode set to 'auto', a
new lot number is created based on the default 'stock.lot.serial' sequence.
""",
    'website': 'http://www.kmsistemas.com',
    'depends' : [
        'product',
        'stock',
    ],
    'conflicts' : [
    ],
    'data': [
        'views/product_view.xml',
        'views/stock_view.xml',
    ],
    'qweb' : [
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
}