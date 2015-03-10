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
    'name': 'Multiple many2one text field widget',
    'version': '1.0',
    'author': 'KM Sistemas de información, S.L.',
    'category': '',
    'summary': '',
    'complexity': 'easy',
    'description': """
Multiple reference fields widget
================================

This module is a prototype of a new field type + widget that links a field in a
model with several records of other different models. It is useful, for example
when you want to track a raw material lot usage. A given lot may have been
partially served to a customer (if you sell the product) and partially consumed
in a manufacturing order.

By now, you must manually take care of writing the field value: it basically
consists of a text field, which content  must be a semicolon-separated list of
pairs (model_name,res_id). So field value would be something like
"model_name1,res_id1;model_name2,res_id2;".

A custom widget 'multi_reference' (bad name, in fact it extends FieldMany2One
widget) formats foretold data structure, presenting it as a set of links to
records of different models.

You can see a working example in my 'stock_lot_enh_base' module.

#TODO: Format/widget in tree view.

Please keep on mind that my Qweb/JQuert/JS skills are limited, so widget is NOT
displayed as I'd like in tree views.
 
""",
    'website': 'http://www.kmsistemas.com',
    'depends': [
        'web',
    ],
    'data': [
        'views/multi_reference_widget_view.xml',
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
}