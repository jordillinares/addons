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
    'name': 'Stock Barcode Sound',
    'version': '1.0',
    'author': 'Jordi Llinares <bigandopen@bigandopen.com>',
    'category': 'Others',
    'summary': 'Scrolls window and plays sound on barcode scanning',
    'complexity': 'easy',
    'description': """
Stock Barcode Sound
===================

This module adds two little improvements to the processing of picking lines
through the JS barcode interface:

- When a barcode is scanned, the interface window is scrolled to show the
  scanned element as the first one. That's specially useful if your picking
  has a lot of lines.

- When a barcode is scanned and processed a different sound is played
  depending on if the barcode has been found or not.

""",
    'website': 'http://www.bigandopen.com',
    'depends': [
    	'stock',
    ],
    'conflicts': [
    ],
    'data': [
        # Security

        # Data

        # Views
        'static/src/xml/stock_barcode_sound.xml',
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
}
