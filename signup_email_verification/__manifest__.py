# -*- coding: utf-8 -*-
{
    'name': "Signup mail confirmation",
    'summary': """ """,
    'description': """ """,
    'price': '30',
    'currency': 'EUR',
    'license': 'OPL-1',
    'support': 'odooeos@gmail.com',
    'author': "Eos odoo",
    'category': 'Uncategorized',
    'version': '12.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'auth_signup', 'website'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/confirmation_view.xml',
    ],
    'images': [
        'static/description/icon.png',
    ],
        'assets': {
            'web.assets_frontend': [
                'signup_email_verification/static/src/css/style.css',
            ],
        },
}
