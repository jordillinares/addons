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
    'name': 'Time fields as \'hh:mm:ss\'',
    'version': '1.0',
    'author': 'Jordi Llinares López - bigandopen@bigandopen.com',
    'category': 'Others',
    'description': """
    This module replaces the format of the 'float_time' widget, which is hh:mm,
    by hh:mm:ss, as there are some industries on which some processes are as
    short as a few seconds. This fact is specially relevant when measuring
    cycle times in manufacturing.
    **for use this function in kanban view must call the "kanban_float_time" function
    Example: t-esc="kanban_float_time(field.raw_value)"**
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
        'views/float_time_hms_views.xml',
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
