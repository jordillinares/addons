# -*- encoding: utf-8 -*-
####################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004- 2015 Tiny SPRL (http://tiny.be). All Rights Reserved
#
#    This module,
#    Copyright (C) 2015 Jordi Llinares <bigandopen@bigandopen.com>
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
#####################################################################

import time
from openerp import models, fields, api, tools
from openerp.addons.decimal_precision import decimal_precision as dp
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools.translate import _
from openerp.addons.product import _common
import math


class mrp_bom(models.Model):

    _inherit = 'mrp.bom'

    @api.model
    def _bom_explode(self, bom, product, factor, properties=None,
                     level=0, routing_id=False, previous_products=None,
                     master_bom=None):
        """
        CAUTION: This method is fully overwritten, so any module that inherits
        it will NOT be compatible with this one.
        """
        uom_obj = self.env['product.uom']
        routing_obj = self.env['mrp.routing']
        master_bom = master_bom or bom

        def _factor(factor, product_efficiency, product_rounding):
            factor = factor / (product_efficiency or 1.0)
            factor = _common.ceiling(factor, product_rounding)
            if factor < product_rounding:
                factor = product_rounding
            return factor

        factor = _factor(factor, bom.product_efficiency, bom.product_rounding)
        result = []
        result2 = []

        routing = (routing_id and routing_obj.browse(routing_id)) or \
                  bom.routing_id or False
        if routing:
            for wc_use in routing.workcenter_lines:
                wc = wc_use.workcenter_id
                for wc_product_cost in wc.product_cost_ids:
                    if wc_product_cost.product_id.id == bom.product_id.id:
                        # Esto afectará al consumo de materiales
                        factor = _factor(factor, wc_product_cost\
                            .product_efficiency or 1.0, bom.product_rounding)
                        d, m = divmod(factor, wc_product_cost\
                            .capacity_per_cycle)
                        cycle = math.ceil(
                            (bom.product_qty * factor) / \
                            wc_product_cost.capacity_per_cycle)
                        result2.append({
                            'name': tools.ustr(wc_use.name) + ' - '  + \
                                    tools.ustr(bom.product_id.name),
                            'workcenter_id': wc.id,
                            'sequence': level+(wc_use.sequence or 0),
                            'cycle': cycle,
                            'hour': round(float(wc_product_cost.time_cycle * \
                                                cycle / wc_product_cost\
                                                .product_efficiency or 1.0),9),
                            # 'est_hour' used only for cost reporting, to know
                            # the difference between estimated and real
                            # operation time.
                            'est_hour': round(
                                float(wc_product_cost.time_cycle * cycle / \
                                      wc_product_cost.product_efficiency \
                                      or 1.0),9),
                        })
        for bom_line_id in bom.bom_line_ids:
            if bom_line_id.date_start \
                and bom_line_id.date_start > \
                            time.strftime(DEFAULT_SERVER_DATE_FORMAT) \
                or bom_line_id.date_stop and bom_line_id.date_stop < \
                            time.strftime(DEFAULT_SERVER_DATE_FORMAT):
                continue
            # all bom_line_id variant values must be in the product
            if bom_line_id.attribute_value_ids:
                if not product or (
                    set(map(int,bom_line_id.attribute_value_ids or [])) -
                    set(map(int,product.attribute_value_ids))):
                    continue

            if previous_products and bom_line_id.product_id.product_tmpl_id\
                .id in previous_products:
                raise Warning(_('BoM "%s" contains a BoM line with a product '
                    'recursion: "%s".') % (master_bom.name,bom_line_id\
                                           .product_id.name_get()[0][1]))

            quantity = _factor(bom_line_id.product_qty * factor,
                               bom_line_id.product_efficiency,
                               bom_line_id.product_rounding)
            bom_id = self._bom_find(product_id=bom_line_id.product_id.id,
                                    properties=properties)

            # If BoM should not behave like PhantoM, just add the product,
            # otherwise explode further
            if bom_line_id.type != "phantom" and (not bom_id or \
                self.browse(bom_id).type != "phantom"):
                result.append({
                    'name': bom_line_id.product_id.name,
                    'product_id': bom_line_id.product_id.id,
                    'product_qty': quantity,
                    'product_uom': bom_line_id.product_uom.id,
                    'product_uos_qty': bom_line_id.product_uos and \
                        _factor(bom_line_id.product_uos_qty * factor,
                                bom_line_id.product_efficiency,
                                bom_line_id.product_rounding) or False,
                    'product_uos': bom_line_id.product_uos and \
                        bom_line_id.product_uos.id or False,
                })
            elif bom_id:
                all_prod = [bom.product_tmpl_id.id] + (previous_products or [])
                bom2 = self.browse(bom_id)
                # We need to convert to units/UoM of chosen BoM
                factor2 = uom_obj._compute_qty(bom_line_id.product_uom.id,
                                               quantity,
                                               bom2.product_uom.id)
                quantity2 = factor2 / bom2.product_qty
                res = self._bom_explode(bom2, bom_line_id.product_id,
                                        quantity2, properties=properties,
                                        level=level + 10,
                                        previous_products=all_prod,
                                        master_bom=master_bom)
                result = result + res[0]
                result2 = result2 + res[1]
            else:
                raise Warning(_('BoM "%s" contains a phantom BoM line but '
                                'the product "%s" does not have any BoM '
                                'defined.') % (master_bom.name,bom_line_id\
                                               .product_id.name_get()[0][1]))
        return result, result2


class mrp_production(models.Model):

    _inherit = 'mrp.production'

    #=========================================================================
    # MO standard cost fields
    #=========================================================================
    std_material_cost = fields.Float(string="Material cost",
            digits = dp.get_precision('Product costing'),
            help="Standard material cost of this MO. It is calculated from "
                 "the standard cost of the actually consumed materials.",
            compute='_cost_all', store=True)
    std_production_cost = fields.Float(string="Production cost",
            digits = dp.get_precision('Product costing'),
            help="Standard production cost of this MO. It is calculated from "
                 "the production costs defined on each workcenter in this "
                 "MO's routing.",
            compute='_cost_all', store=True)
    std_others_cost = fields.Float(string="Other costs",
            digits = dp.get_precision('Product costing'),
            help="Sum of standard additional costs.",
            compute='_cost_all', store=True)
    std_cost = fields.Float(string="Standard cost",
            digits = dp.get_precision('Product costing'),
            help="Standard cost of this MO.",
            compute='_cost_all', store=True)
    std_material_cost_estimated = fields.Float(string="Est. material cost",
            digits = dp.get_precision('Product costing'),
            help="Initially estimated standard material cost of this MO. "
                 "It is calculated from the standard cost of the planned "
                 "materials.",
            compute='_cost_all', store=True)
    std_production_cost_estimated = fields.Float(
            string="Est. production cost",
            digits = dp.get_precision('Product costing'),
            help="Estimated standard production cost of this MO. It is "
                 "calculated from the production costs defined on each "
                 "workcenter in this MO's routing, according to estimated "
                 "to-produce quantity.",
            compute='_cost_all', store=True)
    std_others_cost_estimated = fields.Float(string="Est. add. cost",
            digits = dp.get_precision('Product costing'),
            help="Sum of the estimated standard additional costs of the "
                 "produced product, according to estimated to-produce "
                 "quantity.",
            compute='_cost_all', store=True)
    std_cost_estimated = fields.Float(string="Est. standard cost",
            digits = dp.get_precision('Product costing'),
            help="Estimated standard cost of this MO.",
            compute='_cost_all', store=True)
    #=========================================================================
    # Unitary standard cost fields
    #=========================================================================
    std_material_cost_unit = fields.Float(string="Unit material cost",
            digits = dp.get_precision('Product costing'),
            help="Unitary (per product UoM) standard material cost of "
                 "this MO.",
            compute='_cost_all', store=True)
    std_production_cost_unit = fields.Float(string="Unit production cost",
            digits = dp.get_precision('Product costing'),
            help="Unitary (per product UoM) standard production cost of "
                 "this MO.",
            compute='_cost_all', store=True)
    std_others_cost_unit = fields.Float(string="Unit additional cost",
            digits = dp.get_precision('Product costing'),
            help="Unitary (per product UoM) additional cost of this MO.",
            compute='_cost_all', store=True)
    std_cost_unit = fields.Float(string="Unit standard cost",
            digits = dp.get_precision('Product costing'),
            help="Unitary (per product UoM) standard cost of this MO.",
            compute='_cost_all', store=True)
    std_material_cost_unit_estimated = fields.Float(
            string="Est. unit mat. cost",
            digits = dp.get_precision('Product costing'),
            help="Estimated unitary (per product UoM) standard material "
                 "cost of this MO.",
            compute='_cost_all', store=True)
    std_production_cost_unit_estimated = fields.Float(
            string="Est. unit prod. cost",
            digits = dp.get_precision('Product costing'),
            help="Estimated unitary (per product UoM) standard production "
                 "cost of this MO.",
            compute='_cost_all', store=True)
    std_others_cost_unit_estimated = fields.Float(
            string="Est. unit add. cost",
            digits = dp.get_precision('Product costing'),
            help="Estimated unitary (per product UoM) additional cost "
                 "of this MO.",
            compute='_cost_all', store=True)
    std_cost_unit_estimated = fields.Float(string="Est. unit std. cost",
            digits = dp.get_precision('Product costing'),
            help="Estimated unitary (per product UoM) standard cost "
                 "of this MO.",
            compute='_cost_all', store=True)
    #=========================================================================
    # Cost difference fields
    #=========================================================================
    std_material_cost_balance = fields.Float(
            string="Material cost",
            digits = dp.get_precision('Product costing'),
            help="Difference between estimated and real standard material cost of this MO.",
            compute='_cost_all', store=True)
    std_production_cost_balance = fields.Float(
            string="Production cost",
            digits = dp.get_precision('Product costing'),
            help="Difference between estimated and real production cost of this MO.",
            compute='_cost_all', store=True)
    std_others_cost_balance = fields.Float(
            string="Other costs",
            digits = dp.get_precision('Product costing'),
            help="Difference between estimated and real additional cost of this MO.",
            compute='_cost_all', store=True)
    std_cost_balance = fields.Float(string="Standard cost",
            digits = dp.get_precision('Product costing'),
            help="Difference between estimated and real standard cost of this MO.",
            compute='_cost_all', store=True)
    std_material_cost_unit_balance = fields.Float(
            string="Unit mat. cost",
            digits = dp.get_precision('Product costing'),
            help="Difference between estimated and real unitary standard material cost of this MO.",
            compute='_cost_all', store=True)
    std_production_cost_unit_balance = fields.Float(
            string="Unit prod. cost",
            digits = dp.get_precision('Product costing'),
            help="Difference between estimated and real unitary production material cost of this MO.",
            compute='_cost_all', store=True)
    std_others_cost_unit_balance = fields.Float(
            string="Unit add. cost",
            digits = dp.get_precision('Product costing'),
            help="Difference between estimated and real unitary additional cost of this MO.",
            compute='_cost_all', store=True)
    std_cost_unit_balance = fields.Float(
            string="Unit std. cost",
            digits = dp.get_precision('Product costing'),
            help="Difference between estimated and real unitary standard cost of this MO.",
            compute='_cost_all', store=True)

    @api.depends('state')
    def _cost_all(self):
        bom_obj = self.env['mrp.bom']
        product_uom_obj = self.env['product.uom']
        precision = self.env['decimal.precision'].precision_get(
            'Product costing')
        for record in self:
            vals = {}

            # ESTIMATED standard costs. Computed when MO is confirmed.
            if record.state in ('confirmed', 'ready'):
                record.std_material_cost_estimated = 0.0
                record.std_production_cost_estimated = 0.0
                record.std_others_cost_estimated = 0.0
                record.std_cost_estimated = 0.0
                record.std_material_cost_unit_estimated = 0.0
                record.std_production_cost_unit_estimated = 0.0
                record.std_others_cost_unit_estimated = 0.0
                record.std_cost_unit_estimated = 0.0

                for planned in record.product_lines:
                    default_uom = planned.product_id.uom_id.id
                    planned_qty = product_uom_obj._compute_qty(
                        planned.product_uom.id,
                        planned.product_qty,
                        default_uom)
                    planned.std_cost = planned_qty * \
                                       planned.product_id.standard_price
                    record.std_material_cost_estimated += planned.std_cost

                default_uom = record.product_id.uom_id.id
                to_produce_qty = product_uom_obj._compute_qty(
                    record.product_uom.id,
                    record.product_qty,
                    default_uom)
                for workcenter_line in record.workcenter_lines:
                    wc_cost = 0.0
                    for workcenter_product_cost in workcenter_line\
                            .workcenter_id.product_cost_ids:
                        if workcenter_product_cost.product_id\
                                .id == record.product_id.id:
                            wc_cost += workcenter_product_cost.cost_uom *\
                                       to_produce_qty
                    workcenter_line.est_prod_cost = wc_cost
                    record.std_production_cost_estimated += wc_cost

                record.std_others_cost_estimated = record.product_id.\
                    other_concepts_cost * to_produce_qty
                record.std_cost_estimated =\
                    record.std_material_cost_estimated + \
                    record.std_production_cost_estimated + \
                    record.std_others_cost_estimated

                record.std_material_cost_unit_estimated = round(
                    record.std_material_cost_estimated / to_produce_qty,
                    precision)
                record.std_production_cost_unit_estimated = round(
                    record.std_production_cost_estimated / to_produce_qty,
                    precision)
                record.std_others_cost_unit_estimated = round(
                    record.std_others_cost_estimated / to_produce_qty,
                    precision)
                record.std_cost_unit_estimated = round(
                    record.std_cost_estimated / to_produce_qty,
                    precision)

            # COMPUTED standard costs. Computed when MO is closed.
            elif record.state == 'done':
                record.std_material_cost = 0.0
                record.std_production_cost = 0.0
                record.std_others_cost = 0.0
                record.std_cost = 0.0
                record.std_material_cost_unit = 0.0
                record.std_production_cost_unit = 0.0
                record.std_others_cost_unit = 0.0
                record.std_cost_unit = 0.0
                record.std_material_cost_balance = 0.0
                record.std_production_cost_balance = 0.0
                record.std_others_cost_balance = 0.0
                record.std_cost_balance = 0.0
                record.std_material_cost_unit_balance = 0.0
                record.std_production_cost_unit_balance = 0.0
                record.std_others_cost_unit_balance = 0.0
                record.std_cost_unit_balance = 0.0

                for consumed in record.move_lines2:
                    if consumed.state == 'done':
                        default_uom = consumed.product_id.uom_id.id
                        consumed_qty = product_uom_obj._compute_qty(
                            consumed.product_uom.id,
                            consumed.product_qty,
                            default_uom)
                        consumed.std_cost = consumed_qty * \
                            consumed.product_id.standard_price
                        record.std_material_cost += consumed.std_cost

                default_uom = record.product_id.uom_id.id
                produced_qty = product_uom_obj._compute_qty(
                    record.product_uom.id,
                    record.produced_qty,
                    default_uom)
                for workcenter_line in record.workcenter_lines:
                    wc_cost = 0.0
                    for workcenter_product_cost in workcenter_line\
                            .workcenter_id.product_cost_ids:
                        if workcenter_product_cost.product_id\
                                .id == record.product_id.id:
                            wc_cost = round(
                                (workcenter_product_cost.cost_hour * \
                                 workcenter_line.hour) / \
                                workcenter_product_cost.product_efficiency,
                                precision)
                    workcenter_line.prod_cost = wc_cost
                    record.std_production_cost += wc_cost

                record.std_others_cost = record.product_id\
                    .other_concepts_cost * produced_qty
                record.std_cost = record.std_material_cost + \
                                  record.std_production_cost + \
                                  record.std_others_cost

                if produced_qty:
                    record.std_material_cost_unit = round(
                        record.std_material_cost / produced_qty,
                        precision)
                    record.std_production_cost_unit = round(
                        record.std_production_cost / produced_qty,
                        precision)
                    record.std_others_cost_unit = round(
                        record.std_others_cost / produced_qty,
                        precision)
                    record.std_cost_unit = round(
                        record.std_cost / produced_qty,
                        precision)

                record.std_material_cost_balance = record\
                    .std_material_cost - record.std_material_cost_estimated
                record.std_production_cost_balance = record\
                    .std_production_cost - \
                    record.std_production_cost_estimated
                record.std_others_cost_balance = record\
                    .std_others_cost - record.std_others_cost_estimated
                record.std_cost_balance = record.std_cost - \
                    record.std_cost_estimated
                record.std_material_cost_unit_balance = record\
                    .std_material_cost_unit - \
                    record.std_material_cost_unit_estimated
                record.std_production_cost_unit_balance = record\
                    .std_production_cost_unit - \
                    record.std_production_cost_unit_estimated
                record.std_others_cost_unit_balance = record\
                    .std_others_cost_unit - \
                    record.std_others_cost_unit_estimated
                record.std_cost_unit_balance = record\
                    .std_cost_unit - \
                    record.std_cost_unit_estimated


class mrp_production_product_line(models.Model):

    _inherit = 'mrp.production.product.line'

    std_cost = fields.Float(string="Cost",
            digits = dp.get_precision('Product costing'))


class mrp_production_workcenter_line(models.Model):

    _inherit = 'mrp.production.workcenter.line'

    est_prod_cost = fields.Float(string="Est. prod. cost",
            digits = dp.get_precision('Product costing'))
    prod_cost = fields.Float(string="Production cost",
            digits = dp.get_precision('Product costing'))
    est_hour = fields.Float(string="Est. time",
            digits = dp.get_precision('Product costing'),
            help = "Estimated operation duration.")