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
    'name' : 'MRP KMS',
    'version' : '1.0',
    'author' : 'KM Sistemas de información, S.L.',
    'category' : '',
    'summary': '',
    'complexity': 'easy',
    'description' : """This module implements some changes on the base 'mrp' module of Odoo:
    
-   Invalidate default production wizard and, more specifically, 'action_produce'. We won't
    'consume' or 'consume and produce' anymore. Instead, consume and produce operations are
    independent: 
        -    For each 'to consume' move a button and a wizard is shown.
        -    For each 'to produce' move, a button and a wizard is shown.
        -    The 'Produce' button is replaced by a 'Close order' button that warns you if
             the order has any pending consumption/production moves (it lets you close the
             order, though).
    When you have consumed/produced all you needed to, you'll 'Close order'. If there are any
    pending moves, a warning is raised (though it lets you close the order).
             
-   'Consumed' and 'Produced' fields are not showing cancelled moves anymore.

-   Show the real produced quantity of order's product on the order form header.

             

""",
    'website': 'http://www.kmsistemas.com',
    'depends' : [
        'product',
        'mrp',
        'stock',
        'product_lot_sequence'
    ],
    'conflicts' : [
    ],
    'data': [
        # Workflows
        'workflow/mrp_workflow.xml',
        
        # Views
        'views/mrp_consume_view.xml',
        'views/mrp_view.xml',
    ],
    'qweb' : [
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
}
