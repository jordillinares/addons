# -*- encoding: utf-8 -*-
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

{
    'name': 'CRM leads unique email',
    'version': '1.0',
    'author': 'Jordi Llinares <bigandopen@bigandopen.com>',
    'category': 'Others',
    'summary': 'Unique email field for CRM leads',
    'complexity': 'easy',
    'description': """
CRM leads unique email
======================

This module warns you if the email of the lead you are about to create already
exists.
""",
    'website': 'http://www.bigandopen.com',
    'depends': [
    	'base',
    	'crm',
    ],
    'data': [
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
}
