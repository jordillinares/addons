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

from openerp.addons.decimal_precision import decimal_precision as dp
from openerp import models, fields, api
from openerp.exceptions import ValidationError
from openerp.tools.translate import _


class mrp_bom(models.Model):

    _inherit = 'mrp.bom'

    @api.multi
    def _get_cost(self):
        product_uom_obj = self.env['product.uom']
        for record in self:
            cost = 0.0
            default_uom = record.product_id.uom_id.id
            # cantidad en la UdM del producto (default_uom)
            qty = product_uom_obj._compute_qty(record.product_uom.id,
                                               record.product_qty,
                                               default_uom)
            for bom_line in record.bom_line_ids:
                # Coste
                default_uom = bom_line.product_id.uom_id.id
                # cantidad en la UdM del producto (default_uom)
                qty = product_uom_obj._compute_qty(bom_line.product_uom.id,
                                                   bom_line.product_qty,
                                                   default_uom)
                cost += qty * bom_line.product_id.standard_price
            record.cost = cost

            # Para las LdM que sean cabecera, ir al producto y escribir el coste estándar.
            # Otros costes
            other_costs = 0.0
            for other_cost in record.product_id.other_cost_ids:
                other_costs += other_cost.cost
            std_cost = record.product_id.material_cost + record.product_id.production_cost + other_costs
            # TODO: Añadir un botón de recalcular
            self.env.cr.execute("""
                UPDATE
                    product_product
                SET
                    standard_price = %s
                WHERE
                    id = %s;
                """ % (std_cost, record.product_id.id))

    cost = fields.Float(string="Cost", required=False,
            digits_compute = dp.get_precision('Product costing'),
            help=_("Components cost for this BoM."),
            compute=_get_cost)


class mrp_workcenter_cost_concept(models.Model):
    """
    Master data for workcenter cost concepts.
    """

    _name = 'mrp.workcenter.cost.concept'
    _description = 'Per-hour workcenter cost concept definition'
    #_description = 'Conceptos de coste/hora de máquina'

    name = fields.Char(string="Description", required=True)


class mrp_workcenter_product_cost(models.Model):

    _name = 'mrp.workcenter.product.cost'
    _description = 'Per-product workcenter cost'

    @api.model
    def _default_cost_concepts(self):
        mrp_wc_cost_concept_obj = self.env['mrp.workcenter.cost.concept']
        all_concept_names = mrp_wc_cost_concept_obj.search_read([], ['name'])
        lines = []
        for x in all_concept_names:
            lines.append((0, 0, {'name': x['name']}))
        return lines

    @api.multi
    def _get_cost_all(self):
        res = {}
        precision = self.env['decimal.precision'].precision_get(
            'Product costing')
        for record in self:
            res[record.id] = {
                'cost_hour': 0.0,
                'cost_cycle': 0.0,
                'cost_uom': 0.0,
                }
            for line in record.line_ids:
                record.cost_hour += line.cost
            record.cost_cycle = round(
                record.cost_hour * \
                record.time_cycle, precision)
            record.cost_uom = round(
                record.cost_cycle / \
                (record.capacity_per_cycle * \
                 record.product_efficiency), precision)

    workcenter_id = fields.Many2one(comodel_name="mrp.workcenter",
                                    string="Workcenter", required=True)
    # TODO: Filtro para que sólo se muestren productos que usen esta máquina.
    product_id = fields.Many2one(comodel_name="product.product",
                                 string="Product", required=True)
    capacity_per_cycle = fields.Float(string="Capacity/cycle", required=True,
                                      help = "Quantity of production product (in product's UoM) "
                                             "that the workcenter contributes to produce in a cycle.",
                                      # Definimos como precisión decimal la mínima necesaria para
                                      # almacenar un segundo, que equivale a 0.000277778 horas.
                                      # Por tanto, (4,9)
                                      digits = (4, 9), default=1.0)
    time_cycle = fields.Float(string="Cycle time",
                              help = "Time needed for this machine to complete"
                                     " one cycle.")
    product_efficiency = fields.Float(string="Efficiency factor",
                                      help="A factor of 0.9 means a loss of 10% during the production "
                                           "process.",
                                      required=True, default=1.0)
    # TODO: 'cost_hour' habrá de ser calculado en función de los items y las cantidades
    cost_hour = fields.Float(string="Cost per hour",
                             digits_compute = dp.get_precision('Product costing'),
                             help = "Calculated cost per hour.",
                             compute=_get_cost_all)
    cost_cycle = fields.Float(string="Cost per cycle",
                              digits_compute = dp.get_precision('Product costing'),
                              help = "Calculated cost per cycle.",
                              compute=_get_cost_all)
    cost_uom = fields.Float(string="Cost per UoM",
                            digits_compute = dp.get_precision('Product costing'),
                            help = "Calculated cost per product's UoM.",
                            compute=_get_cost_all)
    line_ids = fields.One2many(comodel_name="mrp.workcenter.product.cost.item",
                               inverse_name="workcenter_product_cost_id",
                               string="Cost details",
                               default=_default_cost_concepts
                               )


    @api.one
    @api.constrains('capacity_per_cycle')
    def _check_qty(self):
        if self.capacity_per_cycle <= 0:
            raise ValidationError("Capacity per cycle cannot "
                                  "be negative or zero!")
        return True

    # Do not allow to declare several cost lines for the same product on a
    # given workcenter
    _sql_constraints = [
        ('product_uniq', 'unique(workcenter_id, product_id)',
         _("A product's cost definition must be unique per work center!")),
        ]


class mrp_workcenter_product_cost_item(models.Model):

    _name = 'mrp.workcenter.product.cost.item'
    _description = 'Hourly workcenter cost detail'

    workcenter_product_cost_id = fields.Many2one(string="Product",
            comodel_name="mrp.workcenter.product.cost",
            required=True,
            default=lambda self, cr, uid, ctx: ctx and ctx.get(
                'workcenter_product_cost_id', False) or False)
    name = fields.Char(string="Description", required=True)
    cost = fields.Float(string="Hourly cost", default=0.0,
            digits_compute = dp.get_precision('Product costing'),
            help="Cost per hour")


class mrp_workcenter(models.Model):

    _inherit = 'mrp.workcenter'

    product_cost_ids = fields.One2many(inverse_name="workcenter_id",
            comodel_name="mrp.workcenter.product.cost",
            string="Efficiency and cost")
