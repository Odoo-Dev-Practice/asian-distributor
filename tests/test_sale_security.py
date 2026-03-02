from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from odoo import Command

class TestSaleSecurity(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.SaleOrder = cls.env['sale.order']
        cls.SaleOrderLine = cls.env['sale.order.line']

        # Get existing groups
        cls.group_sales = cls.env.ref('asian_distributor.group_asian_distributor_local_sales')
        cls.group_manager = cls.env.ref('asian_distributor.group_asian_distributor_manager')

        # Create Seller User
        cls.seller_user = cls.env['res.users'].create({
            'name': 'Test Seller',
            'login': 'seller_test_user',
            'groups_id': [Command.set([cls.group_sales.id, cls.env.ref('base.group_user').id])]
        })

        # Create Manager User
        cls.manager_user = cls.env['res.users'].create({
            'name': 'Test Manager',
            'login': 'manager_test_user',
            'groups_id': [Command.set([cls.group_manager.id, cls.env.ref('base.group_user').id])]
        })

        # Create Test Product
        cls.product = cls.env['product.product'].create({
            'name': 'Test Product Security',
            'list_price': 100.0,
        })

        # Create Test Customer
        cls.partner = cls.env['res.partner'].create({'name': 'Test Customer'})

    def test_01_seller_cannot_write_price(self):
        """A seller should be blocked from modifying the price unit manually."""
        order = self.SaleOrder.create({'partner_id': self.partner.id})
        
        line = self.SaleOrderLine.create({
            'order_id': order.id,
            'product_id': self.product.id,
            'price_unit': 100.0,
        })

        with self.assertRaises(ValidationError, msg="Seller should not be able to write price!"):
            # We enforce with_user simulation
            line.with_user(self.seller_user).write({'price_unit': 80.0})

    def test_02_manager_can_write_price(self):
        """A manager should be allowed to modify the price unit manually."""
        order = self.SaleOrder.create({'partner_id': self.partner.id})
        
        line = self.SaleOrderLine.create({
            'order_id': order.id,
            'product_id': self.product.id,
            'price_unit': 100.0,
        })

        # Manager modifies price shouldn't raise exception
        line.with_user(self.manager_user).write({'price_unit': 50.0})
        self.assertEqual(line.price_unit, 50.0)

    def test_03_seller_cannot_create_with_explicit_custom_price(self):
        """A seller who attempts to inject price_unit via RPC create should have it popped/ignored."""
        order = self.SaleOrder.create({'partner_id': self.partner.id})
        
        # When seller creates a line with explicit price
        line = self.SaleOrderLine.with_user(self.seller_user).create({
            'order_id': order.id,
            'product_id': self.product.id,
            'price_unit': 15.0, # Attempting to hack price during creation
        })
        
        # In our implementation, we silently pop the price_unit and standard Odoo compute takes over 
        # (which sets it back to product standard price, or 0.0 before onchange depending on context).
        # At the very least, we assert the hack attempt did NOT stick.
        self.assertNotEqual(line.price_unit, 15.0)

