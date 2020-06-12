# -*- coding: utf-8 -*-
{
    'name': "数据库分组展示",
    'application': True,
    'sequence': 1,
    
    'summary': """
        数据库在前端页面上分组显示
        """,
    
    'description': """
        数据库在前端页面上分组显示
    """,
    
    'author': "logan.Qian",
    'website': "http://www.yourcompany.com",
    
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'group_database', 'Uncategorized'
                                  'version': '0.1',
    
    # any module necessary for this one to work correctly
    'depends': ['base'],
    
    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/views.xml',
        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
