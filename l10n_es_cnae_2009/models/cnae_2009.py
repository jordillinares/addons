# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2012 Tiny SPRL (http://tiny.be). All Rights Reserved
#
#    This module,
#    Copyright (C) 2015 Jordi Llinares López - jorgellinareslopez@gmail.com
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
from openerp.tools.translate import _


class cnae2009(models.Model):

    _name = 'cnae2009'
    _description = 'Spanish Economic Activity CNAE 2009'
    _rec_name = 'description'

    @api.multi
    def name_get(self):
        def _name_get(d):
            description = d.get('description', '')
            code = 'code' in d and d.get('code', False) or False
            if code:
                description = '%s %s' % (code, description)
            return (d['id'], description)
        result = []
        for record in self:
            mydict = {'id': record.id,
                      'description': record.description,
                      'code': record.code,
                      }
            result.append(_name_get(mydict))
        return result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if not args:
            args = []
        if name:
            ids = self.search(
                ['|', ('code', operator, name),
                 ('description', operator, name)] + args, limit=limit)
        else:
            ids = self.search(args, limit=limit)
        if ids:
            return ids.name_get()
        return False

    code = fields.Char('Code')
    description = fields.Char('Description')
    parent_id = fields.Many2one('cnae2009', string='Parent code')
    child_ids = fields.One2many('cnae2009', 'parent_id',
                                string='Child codes')
    lead_ids = fields.Many2many('crm.lead',
                                'crm_lead_cnae_2009_rel', 'cnae2009_id',
                                'lead_id', string='Leads under this CNAE code')
    partner_ids = fields.Many2many(
        'res.partner', 'res_partner_cnae_2009_rel', 'cnae2009_id', 'partner_id',
        string='Partners under this CNAE code')

    @api.multi
    def from_hierarchy_open_form(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('CNAE code'),
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'cnae2009',
            'res_id': self and self[0].id or False,
            'views': [(False, 'form')],
        }
