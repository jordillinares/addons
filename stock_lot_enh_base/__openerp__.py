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
    # TODO: Rename module to 'Product lot enhancement'
    'name': 'Lot enhancements base',
    'version': '1.0',
    'author': 'Jordi Llinares López - bigandopen@bigandopen.com',
    'category': 'Stock/Traceability',
    'summary': 'Enhancements to lot management in Odoo',
    'complexity': 'easy',
    'description': """
Lot management enhancements
===========================
    
    Adds the possibility to specify a sequence for a product's lot, be it a received
    product or a manufactured product.

    Adds a button in the 'transfer details wizard' that allows to create a new lot number
    on the fly without needing to open a new popup. Please note it only works when product's lot
    creation mode is set to 'auto' and product tracking is enabled any of these three ways: incoming,
    outgoing or all. Furthermore, button visibility is determined by a calculated boolean technical
    field: 'allows_quick_lot_creating', which is only true when transfer action is linked to an
    incoming picking.
    If a sequence has not been specified for the product and it has creation mode set to 'auto', a
    new lot number is created based on the default 'stock.lot.serial' sequence.

    Adds two new char fields to production lot, aimed to give useful information on lots traceability:
        _origin:_ this field is automatically filled when a new lot is created, i.e. on product receival
        or manufacturing (the latter is implemented in 'stock_lot_enh_mrp' module). It shows a unique
        reference for the name of the incoming picking or manufacturing order.
        _destination:_ this field is automatically filled each time a given lot is moved on a picking
        of type internal or outgoing ('stock_lot_enh_mrp' writes also here the name of the manufacturing
        order when a raw material lot is consumed).
    Please note that 'origin' references an unique record, while 'destination' can contain references to
    multiple records of different models. #TODO: Develop a 'multi_many2many_list' field type and widget
    that allows to show links to different records from different models from inside a single labels-type
    field. That would greatly improve traceability UX!

    'quants_get_order' implements an extra check for FEFO quants: if a quant has already expired
    (removal_date < current date), it is taken out from quants calculation. Besides, if the method
    receives 'chatter_model' and 'chatter_id' in the context, it tries to notify the situation via the
    chatter_model message thread (provided the model inherits from mail.thread).
    NOTE: This module does not depend of 'product_expiry', which implements FEFO strategy, because only
    the variable 'orderby' used by the different removal strategies is checked. We assume 'orderby'
    clause for a given strategy will not change ever.

    Lots tree view now has an 'Available' filter that excludes not used lot numbers. Maybe in further
    versions this filter also excludes lots without at least one quant with qty > 0 (hide lots with
    exhausted stocks).

WARNING: Please note that stock.quant's '_quants_get_order' method is fully overwritten, not inherited.

""",
    'website': 'http://www.bigandopen.com',
    'depends': [
        'product',
        'stock',
        'multi_m2o_text_widget',
    ],
    'conflicts': [
    ],
    'data': [
        'views/product_view.xml',
        'views/stock_view.xml',
    ],
    'qweb': [
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
}
