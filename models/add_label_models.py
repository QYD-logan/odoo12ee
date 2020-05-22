# -*- coding: utf-8 -*-
# @Time    : 2020/5/16 13:11
# @Author  : logan
# @FileName: add_label_models.py
# 标签模型在技术设置获取
from ast import literal_eval

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.loglevels import ustr
from odoo.tools import sql


class AddLabel(models.Model):
    _name = 'add.label'
    _rec_name = 'label_name'
    _description = '标签'

    label_name = fields.Char(string=u'标签名称', help='标签名字建议是唯一的且不能重复')
    apply_to_model = fields.Many2one('ir.model', 'Model', index=True, help='Specify a model for the label.')  # 标签关联的模型
    technology_model = fields.Char(string=u'涉及到的技术模块')
    label_line = fields.One2many('add.label.line', 'label_id', string='label Lines', copy=True, auto_join=True)
    label_summary = fields.Char(string=u'摘要')  # 注释
    label_note = fields.Char(string=u'备注')  # 注释
    active = fields.Boolean(default=True)  # 是不是归档是删除整个标签.
    field_ids = fields.Char(string=u'字段')
    access_ids = fields.Char(string=u'访问权限')
    infos = fields.Char(string=u'字段备注')
    sequence = fields.Integer(string=u'Sequence')
    label_field_id = fields.Char(string=u'标签字段')

    _sql_constraints = [('unique_label_name', 'unique (label_name)', u'标签名字重复请重新命名')]

    # 暂时能处理在对应的模型中增加字段,后期再优化和处理
    @api.model
    def create_new_field(self, values):
        """ Create a new field with given values.
            In some cases we have to convert "id" to "name" or "name" to "id"
            - "model" is the current model we are working on. In js, we only have his name.
              but we need his id to create the field of this model.
            - The relational widget doesn't provide any name, we only have the id of the record.
              This is why we need to search the name depending of the given id.
        """
        # Get current model
        # # model_name = values.pop('model_name')
        # Model = self.env[model_name]

        models_name_env = self.env['ir.model'].search([('id', '=', values['apply_to_model'])])
        model_name = models_name_env.model
        Model = self.env[model_name]

        # 获取字段定义模型中的数据
        label_field_env = self.env['add.label.fields'].search(
                [('id', '=', values['label_line'][0][2]['label_field_id'])])
        # If the model is backed by a sql view
        # it doesn't make sense to add field, and won't work
        table_kind = sql.table_kind(self.env.cr, Model._table)
        if not table_kind or table_kind == 'v':
            raise UserError(_('The model %s doesn\'t support adding fields.') % Model._name)
        # models_name_env 下面这个就是这个
        model = self.env['ir.model'].search([('model', '=', model_name)])
        value = {}
        value['model_id'] = model.id
        # 获取字段的名字
        value['name'] = label_field_env.name
        # 获取字段类型信息
        ttype = label_field_env.ttype
        print(ttype, 'ttype')
        # Field type is called ttype in the database
        if ttype:
            value['ttype'] = ttype
        else:
            pass  # 需要警告字段没有类型
        # # For many2one and many2many fields
        # if values.get('relation_id'):
        #     values['relation'] = self.env['ir.model'].browse(values.pop('relation_id')).model
        # # For related one2many fields
        # if values.get('related') and values.get('ttype') == 'one2many':
        #     field_name = values.get('related').split('.')[-1]
        #     field = self.env['ir.model.fields'].search([
        #         ('name', '=', field_name),
        #         ('model', '=', values.pop('relational_model')),
        #     ])
        #     field.ensure_one()
        #     values.update(
        #         relation=field.relation,
        #         relation_field=field.relation_field,
        #     )
        # # For one2many fields
        # if values.get('relation_field_id'):
        #     field = self.env['ir.model.fields'].browse(values.pop('relation_field_id'))
        #     values.update(
        #         relation=field.model_id.model,
        #         relation_field=field.name,
        #     )
        # For selection fields
        if values.get('selection'):
            values['selection'] = ustr(values['selection'])
        # Optional default value at creation
        default_value = values.pop('default_value', False)
        # 获取字段的标签
        value['field_description'] = label_field_env.field_description
        # 对values的值进行修饰,

        print(value, 'value最后的值')
        # Create new field

        new_field = self.env['ir.model.fields'].create(value)

        if default_value:
            if new_field.ttype == 'selection':
                if default_value is True:
                    selection_values = literal_eval(new_field.selection)
                    # take the first selection value as default one in this case
                    default_value = len(selection_values) and selection_values[0][0]
            self.set_default_value(new_field.model, new_field.name, default_value)

        return new_field

    @api.multi
    def add_page_to_model_form(self, values):
        """
        向对应的模型中的form后面添加一个标签页签
        :return:
        """
        pass

    @api.model
    def create(self, values):
        print(values, '多行标签的情况')
        # 在对应的模型中添加字段
        # 这里处理多行的情况(for一下)
        self.create_new_field(values)
        # 给对应模型中的from视图添加对应的页签页面
        self.add_page_to_model_form(values)

        return super(AddLabel, self).create(values)

    # (原本数据中的信息系) write函数写入到这个模型中去write 删除还是增加都是在这个模型中

    @api.multi
    def action_view_label_fields(self):
        """
        跳转到字段管理from视图对字段进行管理(如果字段有对应的标签(标签要是active为true)将不能删除)
        :return:
        """
        action = self.env.ref('add_label.add_label_fields_action').read()[0]
        return action

    @api.multi
    def write(self, vals):
        print('修改标签(头部和行的操作')
        print(self.read(), 'self.read()')
        print(vals, 'vals.readsss')
        # 检查不对应的模型是不是不一样
        try:
            if self.active and vals['apply_to_model']:
                pass
        except Exception:
            values = {}
            values['apply_to_model'] = self.apply_to_model.id
            for new_line in vals['label_line']:
                if new_line[-1]:
                    values['label_line'] = [new_line]
                    print(values, '最后传入的值')
                    # 这在调用函数曾加字段
                    self.create_new_field(values)
        else:
            raise ValidationError(_("已经使用标签关联的模型不允许更改"))

        return super(AddLabel, self).write(vals)


class AddLabelLine(models.Model):
    _name = 'add.label.line'
    _rec_name = 'name'
    _description = '标签行'

    label_id = fields.Many2one('add.label', string='label Reference', required=True, ondelete='cascade', index=True,
                               copy=False)
    name = fields.Char(string='字段名称')
    field_description = fields.Char(string='字段标签')
    field_id = fields.Char(string=u'字段')
    field_ttype = fields.Char(string=u'字段类型')
    access_id = fields.Char(string='访问权限')
    infos = fields.Char(string='字段备注')
    size = fields.Integer()
    required = fields.Boolean()
    readonly = fields.Boolean()
    help = fields.Text(string='Field Help', translate=True)
    copied = fields.Boolean(string='Copied', oldname='copy',
                            help="Whether the value is copied when duplicating a record.")
    store = fields.Boolean(string='Stored', default=True, help="Whether the value is stored in the database.")
    sequence = fields.Integer(string='Sequence')
    label_field_id = fields.Many2one('add.label.fields', string='标签字段')

    @api.multi
    @api.onchange('label_field_id')
    def _get_name_value(self):
        self.name = self.label_field_id.name
        self.field_description = self.label_field_id.field_description
        self.infos = self.label_field_id.infos
        self.field_ttype = self.label_field_id.ttype

    # @api.multi
    # @api.onchange('label_id.active')
    # def change_fields_sate(self):
    #     """
    #     这里需要处理的问题是当标签中的active 变成归档也就是取消标签的时候我们对标签中的字段进行处理
    #     :return:
    #     """
    #     pass
