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
    'name': 'Lot management enhancement in manufacturing',
    'version': '1.0',
    'author': 'Jordi Llinares López - bigandopen@bigandopen.com',
    'category': '',
    'summary': 'Additional enhancements to lot mananagement in manufacturing.',
    'complexity': 'easy',
    'description': """
MRP lot management enhancements:
================================

    Writes manufacturing order number into origin/destination fields of production lots
    when they are consumed/produced. Both fields are defined in 'stock_lot_enh_base' module.

    When the 'Check availability' button of a manufacturing order form view is clicked,
    it sends context values 'chatter_model' and 'chatter_id' to custom _quants_get_order
    That method of 'stock_lot_enh_base' module skips FEFO lots that have already expired.
    Here, thanks to the button context, it can be documented in the manufacturing order message
    thread.

""",
    'website': 'http://www.bigandopen.com',
    'depends': [
        'product',
        'stock',
        'mrp',
        'stock_lot_enh_base',
        'multi_m2o_text_widget',
    ],
    'conflicts': [
    ],
    'data': [
        'views/mrp_view.xml',
        'views/stock_view.xml',
    ],
    'qweb': [
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': True,
}
