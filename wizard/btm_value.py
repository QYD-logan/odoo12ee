# -*- coding: utf-8 -*-
# @Time    : 2020/5/27 18:26
# @Author  : logan
# @FileName: btm_value.py
from odoo import fields, models, api, _
from odoo.exceptions import UserError


class SetLabelValue(models.Model):
    _name = 'btm.label.value'

    @api.multi
    def _get_default_filed_value(self):
        context = dict(self._context or {})  # 获取
        models_id = self.env['ir.model'].search([('model', '=', context.get('active_model'))]).id
        label_env = self.env['add.label'].search([('apply_to_model.id', '=', models_id)])  # 这个是对应add
        res = []
        label_onde = []
        for label in label_env:
            for label_line in label.label_line:
                res.append(label_line.label_field_id.id)
                valu = (label_line.label_field_id.name, label_line.label_field_id.field_description)
                label_onde.append(valu)
        return label_onde

    label_field_name = fields.Char(string='字段名称')  # 字段名字 x_ 这样的
    label_field_description = fields.Char(string='字段标签')  # 字段的标签自己写的中文的标签
    label_field_ttpye = fields.Char(string='字段类型', )  # 字段类型 一般是char
    ttype = fields.Char(string=u'字段类型')
    label_select_field = fields.Selection(_get_default_filed_value, string=u'标签')
    label_select_field_value = fields.Char(string=u'标签值')
    old_value = fields.Char(string='当前的值')

    @api.onchange('label_select_field')
    def get_model_fidel_value(self):
        """
        获取标签的原始值
        :return:
        """
        if not self.label_select_field:
            return ''
        else:
            # 查找对应模型的对应字段的值
            context = dict(self._context or {})  # 获取
            # 给对应的属性赋值
            field_env = self.env['add.label.fields'].search([('name', '=', self.label_select_field)])
            self.label_field_name = field_env.name
            self.label_field_description = field_env.field_description
            self.ttype = field_env.ttype
            if len(context.get('active_ids')) == 1:
                pass

    @api.multi
    def to_value(self):
        """
        对选择的记录和对应的标签赋值
        :return:None
        """
        context = dict(self._context or {})
        active_ids = context.get('active_ids')
        if not self.label_select_field:
            raise UserError(_("请选择标签字段"))
        else:
            # 获取多对应的模型中的记录
            for id_one in active_ids:
                model_env = self.env[context.get('active_model')].search([('id', '=', id_one)])
                name_write = self.label_select_field
                if not self.label_select_field_value:
                    self.label_select_field_value = ''
                model_env.sudo().write({name_write: self.label_select_field_value})  # 将值赋给到对应的记录中去了
