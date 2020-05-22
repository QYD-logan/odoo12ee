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
    # complete_name = fields.Char(index=True)
    relation = fields.Char(string=u'对象关系',
                           help="对于关系字段，是目标模型的技术名称")
    field_description = fields.Char(string=u'字段标签', default='', required=True, translate=True)  # 字段的标签
    infos = fields.Char(string='字段备注')
    help = fields.Text(string=u'字段帮助', translate=True)
    ttype = fields.Selection(selection=FIELD_TYPES, string=u'字段类型', required=True)
    # selection = fields.Char(string='Selection Options', default="",
    #                         help="List of options for a selection field, "
    #                              "specified as a Python expression defining a list of (key, label) pairs. "
    #                              "For example: [('blue','Blue'),('yellow','Yellow')]")
    copied = fields.Boolean(string='复制', oldname='copy', default=True,
                            help="在复制记录时是否复制该值.")
    required = fields.Boolean(string=u'要求')
    readonly = fields.Boolean(string='是否只读')
    index = fields.Boolean(string='索引')
    # translate = fields.Boolean(string='翻译')
    size = fields.Integer(string='字段大小', default='64')
    domain = fields.Char(default="[]", string=u'域')
    groups = fields.Many2many('res.groups', 'ir_model_fields_group_rel', 'field_id', 'group_id')
    # depends = fields.Char(string='依赖关系', help="Dependencies of compute method; "
    #                                                   "a list of comma-separated field names, like\n\n"
    #                                                   "example: name, partner_id.name")
    store = fields.Boolean(string='是否存入数据库', default=True, help="是否存入数据库.默认是")
    state = fields.Boolean(string='字段状态', default=True)  # 默认为Fasle就是字段还没有被创建为,为True的时候就是字段以及被在某个模型中创建

    # label_line_ids = fields.One2many('add.label.line', 'id',string='标签行')

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

    # 当删除标签字段的时候对标签字段是不是使用进行一个校验

    @api.multi
    def unlink(self):
        print('删除标签字段操作')
        # 获取标签行模型,
        name = ''
        for one in self:
            label_line_env = self.env['add.label.line'].search([('label_field_id', '=', one.id)])
            for label_line in label_line_env:
                if label_line.label_id.active:
                    for line in label_line:
                        name += str(line.label_id.label_name)
                    if label_line:
                        raise ValidationError(_("此字段已被名字为:%s的标签使用请先删除标签再来处理!") % name)

    @api.multi
    def write(self, vals):
        print('修改标签字段操作')
        label_line = self.env['add.label.line'].search([('label_field_id', '=', self.id)])
        if label_line:
            raise ValidationError(_("此字段已被标签使用不允许修改!如有需要请新增"))
        return super(AddLabelFields, self).write(vals)
