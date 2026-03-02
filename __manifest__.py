# -*- coding: utf-8 -*-
{
    'name': "Asian Distributor",
    'summary': """
        Base module for Asian import and distribution companies.
    """,
    'description': """
        Adds key fields and processes for imports, inventory, and sales 
        tailored for wholesale distribution environments.
    """,
    'author': "Fairw",
    'category': 'Sales/Custom',
    'version': '18.0.1.0.0',
    'depends': ['base', 'stock', 'sale_management', 'purchase'],
    'data': [
        'security/security_groups.xml',
        'security/ir_rule.xml',
        'security/ir.model.access.csv',
        'views/product_template_views.xml',
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}