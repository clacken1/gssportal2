

{
    'name': 'Approval App',
    'depends': ['base','contacts'],
    'data': [
            'security/ir.model.access.csv',
        'security/access_group.xml',
            'view/approval_app.xml',
            ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
