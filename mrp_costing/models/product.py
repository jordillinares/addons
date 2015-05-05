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
from openerp.addons.decimal_precision import decimal_precision as dp
from operator import itemgetter


class product_template_cost_concept(models.Model):
    """
    Class for a set of predefined product cost concepts.
    """

    _name = 'product.template.cost.concept'
    _description = 'Product cost concept'

    name = fields.Char('Description', required=True)
    category_ids = fields.Many2many('product.category',
                                    'product_cost_conc_cat_rel',
                                    'concept_id', 'category_id',
                                    string='Product categories')


class product_category_cost_concept(models.Model):
    """
    Class that links a set of cost concepts to a product category.
    """

    _name = 'product.category.cost.concept'
    _description = 'Product cost concepts per product category'

    category_id = fields.Many2one('product.category', string='Category',
                                  required=True, ondelete='cascade')
    name = fields.Char('Description', required=True)


class product_template_cost_item(models.Model):
    """
    Implementation of concept + cost value for a product.
    """

    _name = 'product.template.cost.item'
    _description = 'Product cost item'

    product_tmpl_id = fields.Many2one('product.template', string='Product',
                                      required=True, ondelete='cascade')
    name = fields.Char('Description', required=True)
    cost = fields.Float('Cost', digits=dp.get_precision('Product costing'),
                        help="Cost per product UoM")


class product_category(models.Model):

    _inherit = 'product.category'

    @api.model
    def _default_cost_concepts(self):
        cost_concept_obj = self.env['product.template.cost.concept']
        all_concept_names = cost_concept_obj.search_read([], ['name'])
        for x in all_concept_names:
            self.cost_concept_ids.append((0, 0, {'name': x['name'],
                                                 'category_id': self.id,
                                                 }))

    cost_concept_ids = fields.One2many('product.category.cost.concept',
                                       'category_id', 'Cost concepts',
                                       default=_default_cost_concepts)


class product_template(models.Model):

    _inherit = 'product.template'

    concept_cost_ids = fields.One2many('product.template.cost.item',
                                       'product_tmpl_id',
                                       'Other concepts detailed cost')
    other_concepts_cost = fields.Float('Additional cost',
                                       digits=dp.get_precision('Product '
                                                               'costing'),
                                       compute='_compute_cost',
                                       help="Sum of all 'Other concepts"
                                       "detailed costs'")
    material_cost = fields.Float('Material cost',
                                 digits=dp.get_precision('Product costing'),
                                 compute='_compute_cost',
                                 help="Components cost for this product. It "
                                 "is calculated from the product's BoM with "
                                 "the lowest sequence number.")
    production_cost = fields.Float('Production cost',
                                   digits=dp.get_precision('Product costing'),
                                   compute='_compute_cost',
                                   help="Production cost. It is calculated "
                                   "from the routing of the product's BoM "
                                   "with  the lowest sequence number. Each "
                                   "routing  workcenter must have a defined "
                                   "cost forthis product. See workcenter's "
                                   "'Per-product costs' tab.")
    # TODO: What if a product DOES have a BoM, but it can be not only
    # manufactured but also purchased? How are we going to control this
    # field "readonliness"?
    computed_cost = fields.Float('Computed cost',
                                 digits=dp.get_precision('Product costing'),
                                 compute='_compute_cost',
                                 help="Computed cost. It can be manually set"
                                 " here if this product has not any BoM "
                                 "linked. Otherwise, it is calculated from "
                                 " the sum of material, production and other"
                                 " concepts cost.")
    standard_price = fields.Float('Cost Price',
                                 digits=dp.get_precision('Product costing'),
                                 help="Cost price of the product "
                                 "used for standard stock valuation in "
                                 "accounting and used as a base price on "
                                 "purchase orders. Expressed in the default "
                                 "unit of measure of the product.",
                                 company_dependent=True)
    cost_method = fields.Selection([('standard', 'Standard Price'),
                                    ('average', 'Average Price'),
                                    ('real', 'Real Price'),
                                    ('auto_mpa', 'Computed (M+P+A)'),
                                    ],
                                   string='Costing method',
                                   required=True,
                                   copy=True,
                                   help="Standard Price: The cost price is "
                                   "manually updated at the end of a specific "
                                   "period (usually every year).\n"
                                   "Average Price: The cost price is "
                                   "recomputed at each incoming shipment and "
                                   "used for the product valuation.\n"
                                   "Real Price: The cost price displayed is "
                                   "the price of the last outgoing product "
                                   "(will be use in case of inventory loss "
                                   "for example).\n"
                                   "Computed (M+P+A): The cost price is "
                                   "automatically calculated as the sum of "
                                   "Material + Production + Additional costs."
                                   " If the product has not any defined BoM, "
                                   " its cost is only calculated from the "
                                   "additional costs details table.")

    @api.one
    def default_cost_concepts(self):
        category_cost_concept_obj = self.env['product.category.cost.concept']
        product_cost_concept_obj = self.env['product.template.cost.item']
        all_concept_names = category_cost_concept_obj.search_read([], ['name'])
        self.concept_cost_ids = []
        concept_costs = []
        for x in all_concept_names:
            product_cost_concept_obj.create({'name': x['name'],
                                             'product_tmpl_id': self.id,
                                             })

    # Verificado: aquí no ponemos depends. Si ponemos depends + stored, la única forma
    # de que se actualice al actualizar standard_price de un componente es
    # editando éste desde el PF, a través de su LdM.
    @api.multi
    def _compute_cost(self):
        # BEWARE: Material and production cost are both calculated ONLY from
        # the product's BoM with the lowest sequence number. It does NOT take
        # into account BoM validity dates nor routes.
        bom_obj = self.env['mrp.bom']
        uom_obj = self.env['product.uom']
        dp_obj = self.env['decimal.precision']
        wc_product_cost_obj = self.env['mrp.workcenter.product.cost']
        material_cost = 0.0
        production_cost = 0.0
        oth_conc_cost = 0.0
        for record in self:
            if record.bom_count:

                bom_ids = [x.id for x in record.sudo().bom_ids if x.active]
                bom_ids_read = bom_obj.search_read(
                    [('id', 'in', bom_ids)
                     ], ['sequence'])
                if bom_ids_read:
                    by_seq_bom_ids = sorted(bom_ids_read,
                                            key=itemgetter('sequence', 'id'))
                    # This is the BoM with the lowest sequence number
                    bom_id = by_seq_bom_ids[0]['id']
                    bom = bom_obj.browse(bom_id)

                    # Material cost
                    # bom_qty = BoM's product qty in the default UoM of the product
                    bom_qty = uom_obj._compute_qty(bom.product_uom.id,
                                                   bom.product_qty,
                                                   record.uom_id.id)
                    for bom_line in bom.bom_line_ids:
                        # bom_line_qty = bom line qty in the default UoM
                        # of the product
                        bomline_qty = uom_obj._compute_qty(
                            bom_line.product_uom.id,
                            bom_line.product_qty,
                            bom_line.product_id.uom_id.id)
                        material_cost += round(bomline_qty * \
                            bom_line.product_id.standard_price,
                            dp_obj.precision_get('Product costing'))
                    material_cost = round(material_cost / bom_qty,
                        dp_obj.precision_get('Product costing'))

                    # Production cost (para ese mismo bom ya seleccionado para el coste material)
                    if bom.routing_id:
                        for workcenter_line in bom.routing_id.workcenter_lines:
                            # We will have only a record for each product due
                            # to sql_constrains, but we can certainly have
                            # a record for each product variant of a product,
                            # so how do we get the template's production cost?
                            # Keeping in mind that our goal is that the BoM
                            # with the lowest sequence determines material
                            # and production cost, we check if this bom
                            # (already selected here) has a variant. If not,
                            # it is decided according to the 'sequence'
                            # field of the per-product cost definition for
                            # each workcenter.
                            wc_product_costs = []
                            if bom.product_id:
                                wc_product_costs = wc_product_cost_obj.search([('workcenter_id','=', workcenter_line.workcenter_id.id),('product_id','=',bom.product_id.id)], order='sequence')
                            else:
                                wc_product_costs = wc_product_cost_obj.search([('workcenter_id','=', workcenter_line.workcenter_id.id),('product_tmpl_id','=',record.id)], order='product_id,sequence')
                            production_cost += wc_product_costs and wc_product_costs[0].cost_uom or 0.0

                # Other concepts cost
                for concept_cost in record.concept_cost_ids:
                    oth_conc_cost += concept_cost.cost or 0.0

                record.material_cost = material_cost
                record.production_cost = production_cost
                record.other_concepts_cost = oth_conc_cost
                record.computed_cost = record.material_cost + \
                    record.production_cost +  record.other_concepts_cost

                if record.cost_method == 'auto_mpa' and \
                    record.standard_price != record.computed_cost:
                        res_id = 'product.template,' + str(record.id)
                        self.env.cr.execute("""
                            UPDATE
                                ir_property
                            SET
                                value_float = %s
                            WHERE
                                res_id = '%s'
                            AND
                                name = 'standard_price';
                        """ % (record.computed_cost, res_id))

    @api.onchange('cost_method','computed_cost','concept_cost_ids.cost')
    def _onchange_cost_method(self):
        if self.cost_method == 'auto_mpa' and \
            self.standard_price != self.computed_cost:
                self.standard_price = self.computed_cost

    @api.one
    def write(self, vals):
        res = super(product_template, self).write(vals)
        if 'cost_method' in vals:
            if vals['cost_method'] == 'auto_mpa':
                super(product_template,
                      self).write({'standard_price': self.computed_cost})
        elif 'concept_cost_ids' in vals:
            if self.cost_method == 'auto_mpa':
                super(product_template,
                      self).write({'standard_price': self.computed_cost})
        return res


class product_product(models.Model):

    _inherit = 'product.product'

    material_cost = fields.Float('Material cost',
                                 digits=dp.get_precision('Product costing'),
                                 compute='_compute_cost',
                                 help="Components cost for this product. It "
                                 "is calculated from the product's BoM with "
                                 "the lowest sequence number.")
    production_cost = fields.Float('Production cost',
                                   digits=dp.get_precision('Product costing'),
                                   compute='_compute_cost',
                                   help="Production cost. It is calculated "
                                   "from the routing of the product's BoM "
                                   "with  the lowest sequence number. Each "
                                   "routing  workcenter must have a defined "
                                   "cost forthis product. See workcenter's "
                                   "'Per-product costs' tab.")
    computed_cost = fields.Float('Computed cost',
                                 digits=dp.get_precision('Product costing'),
                                 compute='_compute_cost',
                                 help="Computed cost. It can be manually set"
                                 " here if this product has not any BoM "
                                 "linked. Otherwise, it is calculated from "
                                 " the sum of material, production and other"
                                 " concepts cost.")
    standard_price = fields.Float('Cost Price',
                                 digits=dp.get_precision('Product costing'),
                                 help="Cost price of the product "
                                 "used for standard stock valuation in "
                                 "accounting and used as a base price on "
                                 "purchase orders. Expressed in the default "
                                 "unit of measure of the product.",
                                 company_dependent=True)
    cost_method = fields.Selection([('standard', 'Standard Price'),
                                    ('average', 'Average Price'),
                                    ('real', 'Real Price'),
                                    ('auto_mpa', 'Auto M+P+A'),
                                    ],
                                   string='Costing method',
                                   required=True,
                                   copy=True,
                                   help="Standard Price: The cost price is "
                                   "manually updated at the end of a specific "
                                   "period (usually every year).\n"
                                   "Average Price: The cost price is "
                                   "recomputed at each incoming shipment and "
                                   "used for the product valuation.\n"
                                   "Real Price: The cost price displayed is "
                                   "the price of the last outgoing product "
                                   "(will be use in case of inventory loss "
                                   "for example).\n"
                                   "Auto M+P+A: The cost price is "
                                   "automatically calculated as the sum of "
                                   "Material + Production + Additional costs."
                                   " If the product has not any defined BoM, "
                                   " its cost method is only defined by the "
                                   "additional costs details table.")

    @api.multi
    def _compute_cost(self):
        # BEWARE: Material and production cost are both calculated ONLY from
        # the product's BoM with the lowest sequence number. It does NOT take
        # into account BoM validity dates nor routes.
        bom_obj = self.env['mrp.bom']
        uom_obj = self.env['product.uom']
        dp_obj = self.env['decimal.precision']
        material_cost = 0.0
        production_cost = 0.0
        oth_conc_cost = 0.0
        for record in self:

            bom_obj = self.env['mrp.bom']
            bom_id = bom_obj._bom_find(product_id=record.id)
            if bom_id:
                bom = bom_obj.browse(bom_id)
                # Material cost
                # bom_qty = BoM's product qty in the default UoM of the product
                bom_qty = uom_obj._compute_qty(bom.product_uom.id,
                                               bom.product_qty,
                                               record.uom_id.id)
                for bom_line in bom.bom_line_ids:
                    # bom_line_qty = bom line qty in the default UoM
                    # of the product
                    bomline_qty = uom_obj._compute_qty(
                        bom_line.product_uom.id,
                        bom_line.product_qty,
                        bom_line.product_id.uom_id.id)
                    material_cost += round(bomline_qty * \
                        bom_line.product_id.standard_price,
                        dp_obj.precision_get('Product costing'))
                material_cost = round(material_cost / bom_qty,
                    dp_obj.precision_get('Product costing'))

                # Production cost (para el mismo bom ya seleccionado para el
                # coste material)
                if bom.routing_id:
                    for workcenter_line in bom.routing_id.workcenter_lines:
                        wc_cost = 0.0
                        for workcenter_product_cost in workcenter_line.workcenter_id.product_cost_ids:
                            if workcenter_product_cost.product_id.id == record.id:
                                wc_cost += workcenter_product_cost.cost_uom
                        production_cost += wc_cost

            # Other concepts cost
            for concept_cost in record.product_tmpl_id.concept_cost_ids:
                oth_conc_cost += concept_cost.cost or 0.0

            record.material_cost = material_cost
            record.production_cost = production_cost
            record.other_concepts_cost = oth_conc_cost
            record.computed_cost = record.material_cost + \
                record.production_cost +  record.other_concepts_cost

            if record.cost_method == 'auto_mpa' and \
                record.standard_price != record.computed_cost:
                    record.standard_price = record.computed_cost

    @api.onchange('cost_method','computed_cost')
    def _onchange_cost_method(self):
        if self.cost_method == 'auto_mpa' and \
            self.standard_price != self.computed_cost:
                self.standard_price = self.computed_cost

    # TODO: Interesa que, con el create, se copien los costes desde la plantilla.
    # Ahora, al crear un producto, como se crea automáticamente su variante única,
    # ésta no trae costes.

    @api.one
    def write(self, vals):
        res = super(product_product, self).write(vals)
        if 'cost_method' in vals:
            if vals['cost_method'] == 'auto_mpa':
                super(product_product, self).write({'standard_price': self.computed_cost})
        elif 'concept_cost_ids' in vals:
            if self.cost_method == 'auto_mpa':
                super(product_product, self).write({'standard_price': self.computed_cost})
        return res
