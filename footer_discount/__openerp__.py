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
    'name': 'Footer discounts',
    'version': '1.0',
    'author': 'Jordi Llinares <bigandopen@bigandopen.com>',
    'category': 'Others',
    'summary': 'Two footer discounts on partner documents',
    'complexity': 'easy',
    'description': """
Footer discounts
================

This module:

- Adds two default discount fields to the partner form: sale and purchase discount.
- Adds two discount fields (partner discount and additional discount) to the footer
  of each sale/purchase document (i.e. order and invoice).
- For each new document, picks the default partner discount from the partner form.
- Propagates footer discounts from purchase/sales orders to invoice, be it generated
  from the order itself or from a picking.
- Propagates footer discounts from original invoice to refund.
- Keeps into account these discounts on financial moves and payment terms generation.

Discount fields added by this module can be hidden by disabling their corresponding
checkbox on both sale and purchase configuration settings. Changes on these two
checkboxes are linked to ir_config_param values, so when you uncheck the boxes
the discount fields on purchase/sale documents are not shown, and default value for
the partner discount field on each new document is set to 0 (without using these
parameters, you would hide the discount fields on new documents, but partner discount
field would still be defaulted to the partner's form 'default discount' value).

This module is based on previous work by E-nova tecnologies Pvt. Ltd. for OpenERP 6.1.
Greetings go there!
""",
    'website': 'http://www.bigandopen.com',
    'depends': [
        'base',
    	'purchase',
        'sale',
    	'stock',
        'account',
    ],
    'conflicts': [
    ],
    'data': [
        # Security
        'security/footer_discount_security.xml',

        # Data
        'data/data.xml',

        # Views
        'views/res_config_view.xml',
        'views/partner_view.xml',
        'views/purchase_view.xml',
        'views/sale_view.xml',
        'views/account_invoice_view.xml',
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
}


