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
    'name' : 'Product lot traceability MRP',
    'version' : '1.0',
    'author' : 'KM Sistemas de información, S.L.',
    'category' : '',
    'summary': '',
    'complexity': 'easy',
    'description' : """
Product lot traceability MRP
================
    
This module enhances Odoo traceability capabilities, by:

-    Writes manufacturing order number into origin/destination fields of production lots
     when they are consumed/produced.
     
-    When the 'Check availability' button inside a manufacturing order form view is clicked,
    it sends context values 'chatter_model' and 'chatter_id' to our custom _quants_get_order
    (see dependencies). That method skips FEFO lots that have already expired. Here, thanks
    to the button context, it can be documented in the manufacturing order message thread. 
    

""",
    'website': 'http://www.kmsistemas.com',
    'depends' : [
        'product',
        'stock',
        'mrp',
        'product_lot_sequence',
    ],
    'conflicts' : [
    ],
    'data': [
        'views/stock_view.xml',
        'views/mrp_view.xml',
    ],
    'qweb' : [
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': True,
}