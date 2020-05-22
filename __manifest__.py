# -*- coding: utf-8 -*-
{
        'name':"添加标签",
        'application':True,
        'sequence':1,

        'summary':"""
        添加标签ha de """,

        'description':"""
        添加标签
    """,

        'author':"logan.Qian,",
        'website':"http://www.yourcompany.com",

        # Categories can be used to filter modules in modules listing
        # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
        # for the full list
        'category':'add_label',
        'version':'0.1',

        # any module necessary for this one to work correctly
        'depends':['base', 'base_setup', 'sale', 'bus', 'web_tour'],

        # always loaded
        'data':[
                # 'security/add_label_group.xml',
                'security/ir.model.access.csv',
                'views/views.xml',
                # # 'views/templates.xml',
                'views/add_label.xml',
                'views/add_hear_label.xml',
                'views/add_fields_l.xml',
                ],
        # only loaded in demonstration mode
        'demo':[
                'demo/demo.xml',
                ],
        }
