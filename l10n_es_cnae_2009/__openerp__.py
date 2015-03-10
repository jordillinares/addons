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
    'name': 'Spanish CNAE 2009',
    'version': '1.0',
    'author': 'Jordi Llinares López - jorgellinareslopez@gmail.com',
    'category': 'Customer Relationship Management',
    'summary': 'Spanish CNAE list of economic activities',
    'complexity': 'easy',
    'description': """
Spanish CNAE 2009
=================
This module adds a new entity to manage the list of economic activities
defined in CNAE 2009, which is a version of european NACE.
Warning: Although module fields and views are defined both in english and
spanish, master data of the CNAE list are only in spanish.

Features:
-    Full spanish CNAE hyerarchical records list.
-    View of linked leads/partners to a given CNAE code from within its
     form view.
-    Added a new tags field in lead/opportunity/partner form view for CNAE
     codes (several codes may be linked).
-    CNAE codes are written when escalating a crm case to a partner.
""",
    'website': '',
    'depends': [
        'base',
        'crm',
    ],
    'data': [
        # Security
        'security/ir.model.access.csv',

        # Data
        'data/cnae2009_es.xml',

        # Views
        'views/cnae_2009_view.xml',
        'views/crm_lead_view.xml',
        'views/res_partner_view.xml',
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
