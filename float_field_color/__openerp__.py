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
    'name': 'Float field color widget',
    'version': '1.0',
    'author': 'Jordi Llinares López - bigandopen@bigandopen.com',
    'category': 'Others',
    'description': """
    This module extends the float field widget creating two new widgets:
    'float_color' and 'float_color_inverted', which automatically set the font
    color accoding to the float value sign.

    USAGE: declare a float field with widget='float_color' to display positive
    values in green color and negative ones in red, or with 'float_color_inverted'
    to invert the color rule.

    NOTE: This widget currently works only on form view.
    """,
    'website': 'http://www.bigandopen.com',
    'images': [
    ],
    'depends': [
        'web',
    ],
    'conflicts': [
    ],
    'data': [
        'static/src/views/float_field_color.xml',
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
}
