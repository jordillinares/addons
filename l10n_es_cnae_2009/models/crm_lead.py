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

from openerp import models, fields, api


class crm_lead(models.Model):

    _inherit = 'crm.lead'

    cnae2009_ids = fields.Many2many('cnae2009',
                                    'crm_lead_cnae_2009_rel', 'lead_id',
                                    'cnae2009_id', string='CNAE codes')

    def _lead_create_contact(self, cr, uid, lead, name, is_company,
                             parent_id=False, context=None):
        if context is None:
            context = {}
        res = super(crm_lead, self)._lead_create_contact(
            cr, uid, lead, name, is_company, parent_id, context)
        partner_obj = self.pool.get('res.partner')
        if is_company:
            for cnae in lead.cnae2009_ids:
                partner_obj.write(
                    cr, uid, [res],
                    {'cnae2009_ids': [(4, cnae.id)]})
        return res
