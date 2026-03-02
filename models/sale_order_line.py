from odoo import models, fields, api, _, exceptions
import logging

_logger = logging.getLogger(__name__)

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    is_price_editable = fields.Boolean(
        compute='_compute_is_price_editable',
        store=False
    )

    @api.depends_context('uid')
    def _compute_is_price_editable(self):
        for line in self:
            line.is_price_editable = self.env.user.has_group('asian_distributor.group_asian_distributor_manager')

    def write(self, vals):
        if 'price_unit' in vals and not self.env.user.has_group('asian_distributor.group_asian_distributor_manager'):
            for line in self:
                # Allow standard processes to pass if the value is essentially the same
                new_price = float(vals['price_unit']) if vals['price_unit'] else 0.0
                if new_price != line.price_unit:
                    raise exceptions.ValidationError(_("No tiene derechos para modificar el precio de catálogo."))
        
        return super(SaleOrderLine, self).write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.user.has_group('asian_distributor.group_asian_distributor_manager'):
            for vals in vals_list:
                if 'price_unit' in vals:
                    _logger.debug("Non-manager user is creating a sale.order.line with explicit price_unit. Relying on UI restriction and standard priceless recomputation.")
                    # Normally we'd raise an exception here, but during creation Odoo often explicitly sends price_unit computed in the frontend.
                    # Since the UI field is locked as readonly/force_save, they physically can't edit it.
                    # For backend API protection, we pop the price_unit and let Odoo compute it properly from pricelists.
                    vals.pop('price_unit', None)
                    
        return super(SaleOrderLine, self).create(vals_list)
