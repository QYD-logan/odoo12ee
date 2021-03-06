# -*- coding: utf-8 -*-
# @Time    : 2020/5/18 15:45
# @Author  : logan
# @FileName: model_field_l.py
# 定义自定义字段模型,一个模型有很多的字段属性,规定标签字段'l_'开头的为自定义标签字段
from odoo import fields, api, models, _
from odoo.exceptions import ValidationError

FIELD_TYPES = [(key, key) for key in sorted(fields.Field.by_type)]


class AddLabelFields(models.Model):
    _name = 'add.label.fields'
    _order = 'name'
    _rec_name = 'name'
    _description = '标签字段'

    name = fields.Char(string='字段名字', default='x_', required=True, index=True)
    field_description = fields.Char(string=u'字段标签', default='', required=True, translate=True)  # 字段的标签
    infos = fields.Char(string='字段备注')
    help = fields.Text(string=u'字段帮助', translate=True)
    ttype = fields.Selection(selection=FIELD_TYPES, string=u'字段类型', required=True, default='char')
    copied = fields.Boolean(string='复制', oldname='copy', default=True,
                            help="在复制记录时是否复制该值.")
    readonly = fields.Boolean(string='是否只读')
    index = fields.Boolean(string='索引')
    size = fields.Integer(string='字段大小', default='64')
    domain = fields.Char(default="[]", string=u'域')
    groups = fields.Many2many('res.groups', 'ir_model_fields_group_rel', 'field_id', 'group_id')
    store = fields.Boolean(string='是否存入数据库', default=True, help="是否存入数据库默认是")
    state = fields.Boolean(string='字段状态', default=True)
    track_visibility = fields.Selection(
        [('onchange', "On Change"), ('always', "Always")], string="跟踪",
        help="设置后，对该字段的每次修改都会在聊天记录中跟踪.", default='onchange'
    )

    _sql_constraints = [('unique_label_fields_name', 'unique (name)', u'字段名称不能重复')]

    @api.multi
    @api.onchange('name')
    def _check_name(self):
        for field in self:
            if field.state == 'manual' and not field.name.startswith('x_'):
                raise ValidationError(_("Custom fields must have a name that starts with 'x_' !"))
            try:
                models.check_pg_name(field.name)
            except ValidationError:
                msg = _("Field names can only contain characters, digits and underscores (up to 63).")
                raise ValidationError(msg)

    # 校验选择其他类型字段
    @api.multi
    @api.onchange('ttype')
    def _check_ttype(self):
        value = ['many2many', 'many2one', 'one2many', 'html', 'selection', 'reference']
        if self.ttype in value:
            msg = (_("%s字段类型暂时不能使用") % self.ttype)
            raise ValidationError(msg)

    @api.multi
    def unlink(self):
        # 获取标签行模型,
        name = ''
        for one in self:
            label_line_env = self.env['add.label.line'].search([('label_field_id', '=', one.id)])
            for label_line in label_line_env:
                for line in label_line:
                    name += str(line.label_id.label_name)
                if label_line:
                    raise ValidationError(_("此字段已被名字为:%s的标签使用请先删除标签再来处理!") % name)
        return super(AddLabelFields, self).unlink()

    @api.multi
    def write(self, vals):
        label_line = self.env['add.label.line'].search([('label_field_id', '=', self.id)])
        if label_line:
            raise ValidationError(_("此字段已被标签使用不允许修改!如有需要请新增"))
        return super(AddLabelFields, self).write(vals)
