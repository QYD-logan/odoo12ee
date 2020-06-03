# -*- coding: utf-8 -*-
# @Time    : 2020/5/16 13:11
# @Author  : logan
# @FileName: add_label_models.py
# 标签模型在技术设置获取
import logging
import os
import re
import xml.etree.ElementTree as ET

from lxml import etree

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError, AccessError
from odoo.tools import sql

_logger = logging.getLogger(__name__)


# 获取对应的文件路劲
def load_field_address():
    current_path = os.path.abspath(__file__)  # 获取当前文件夹
    config_file_path = os.path.join(os.path.abspath(os.path.dirname(current_path) + os.path.sep + ".."),
                                    'views/templates.xml')
    return config_file_path


PATH_add = load_field_address()


class AddLabel(models.Model):
    _name = 'add.label'
    _rec_name = 'label_name'
    _description = '标签'

    label_name = fields.Char(string=u'标签名称', help='标签名字不能重复', copy=False)
    apply_to_model = fields.Many2one('ir.model', 'Model', index=True, help='Specify a model for the label.')  # 标签关联的模型
    label_model_record = fields.Many2one('')
    label_line = fields.One2many('add.label.line', 'label_id', string='label Lines', copy=True, auto_join=True)
    label_summary = fields.Char(string=u'摘要')  # 注释
    label_note = fields.Char(string=u'备注')  # 注释
    field_ids = fields.Char(string=u'字段')
    access_ids = fields.Char(string=u'访问权限')
    infos = fields.Char(string=u'字段备注')
    sequence = fields.Integer(string=u'序号')
    label_field_id = fields.Char(string=u'标签字段')

    _sql_constraints = [('unique_label_name', 'unique (label_name)', u'标签名字重复请重新命名')]

    models_summary = fields.Char(string=u'使用标签的模型')

    @api.multi
    def get_labelfield_sum(self, self_m, self_one):
        """
        计算这个label模型字段中的
        :return:
        """
        result = self.search([('apply_to_model.id', '=', self_one.apply_to_model.id)])
        count = 0  # 本次删除的是几条
        for self1 in self_m:
            if self_one.apply_to_model == self1.apply_to_model:
                count += 1
        chsm = len(result) - count  # 最后结果的总数
        return chsm

    @api.model
    def create_new_field(self, values, models_name_env):
        """ Create a new field with given values.
            In some cases we have to convert "id" to "name" or "name" to "id"
            - "model" is the current model we are working on. In js, we only have his name.
              but we need his id to create the field of this model.
            - The relational widget doesn't provide any name, we only have the id of the record.
              This is why we need to search the name depending of the given id.
        """
        # Get current model
        model_name = models_name_env.model
        Model = self.env[models_name_env.model]
        # 获取字段定义模型中的数据
        label_field_env = self.env['add.label.fields'].search(
                [('id', '=', values[2]['label_field_id'])])
        # If the model is backed by a sql view
        # it doesn't make sense to add field, and won't work
        table_kind = sql.table_kind(self.env.cr, Model._table)
        if not table_kind or table_kind == 'v':
            raise UserError(_('The model %s doesnt support adding fields.') % Model._name)
        model = self.env['ir.model'].search([('model', '=', model_name)])
        value = {}
        value['model_id'] = model.id
        value['name'] = label_field_env.name
        value['ttype'] = label_field_env.ttype
        value['field_description'] = label_field_env.field_description
        # Create new field
        new_field = self.env['ir.model.fields'].create(value)
        return new_field

    @api.model
    def create(self, values):
        # 这里处理多行的情况-
        models_name_env = self.env['ir.model'].search([('id', '=', values['apply_to_model'])])
        try:
            values['label_line']
        except:
            raise AccessError(_("请添加标签行"))
        else:
            for result in values['label_line']:
                self.create_new_field(result, models_name_env)
            res = super(AddLabel, self).create(values)
            self.add_page_to_from(models_name_env)  # 添加页签
            self.create_action_to_tree(models_name_env)  # 添加动作
        return res

    # 字段管理啊视图界面
    @api.multi
    def action_view_label_fields(self):
        """
        跳转到字段管理from视图对字段进行管理
        :return:
        """
        action = self.env.ref('add_label.add_label_fields_action').read()[0]
        return action

    # 点击跳转到对应的tree视图
    @api.multi
    def action_view_model_tree(self):
        """
        跳转到对应模型的tree视图
        :return: 返回对应的字段值
        """
        model_env = self.env['ir.model'].search([('id', '=', self.apply_to_model.id)])
        return {
                'name':'模型记录',
                'type':'ir.actions.act_window',
                'view_type':'form',
                'res_model':model_env.model,
                "view_mode":'tree,form',
                }

    # onchange(改变模型的时候提醒)
    @api.multi
    @api.onchange("apply_to_model")
    def _check_apply_to_model(self):
        """
        点击改变不允许更改
        :return:
        """
        # 获取原始的模型信息
        label_env = self.search([('label_name', '=', self.label_name)])
        if not label_env.apply_to_model:
            pass
        else:
            if label_env.apply_to_model != self.apply_to_model:
                raise AccessError(_("模型不能修改"))

    # 写入操作
    @api.multi
    def write(self, vals):
        models_name_env = self.env['ir.model'].search([('id', '=', self.apply_to_model.id)])
        try:
            vals['label_line']
        except:
            return super(AddLabel, self).write(vals)
        else:
            for res in vals['label_line']:
                if res[0] == 0:  # 这个新增行
                    result = super(AddLabel, self).write(vals)
                    self.create_new_field(res, models_name_env)
                    self.create_action_to_tree(models_name_env)  # 创建动作
                    # 新增页签
                    self.add_page_to_from(models_name_env)  # 增加页签
                elif res[0] == 2:  # 这个是删除行

                    result = super(AddLabel, self).write(vals)
                    line_env = self.env['add.label.line'].search([('id', '=', res[1])])
                    self.delete_page_to_from()  # 删除页签
                    field_env = self.env['ir.model.fields'].search([('name', '=', line_env.label_field_id.name),
                                                                    ('model', '=', self.apply_to_model.model)])
                    field_env.unlink()  # 删除对应的模型字段
            return result

    # 删除标签的方法
    @api.multi
    def unlink(self):
        """
        删除的功能
        :return:
        """
        self_m = self
        for self_one in self:
            model_env = self.env['ir.model'].search([('id', '=', self_one.apply_to_model.id)])
            num = self.get_labelfield_sum(self_m, self_one)
            for line in self_one.label_line:
                if num == 0:
                    self_one.delete_action()  # 删除动作
                    self_one.delete_from_page()  # 删除页签
                    self._update_model()
                    field_env = self.env['ir.model.fields'].search([('name', '=', line.label_field_id.name),
                                                                    ('model', '=', model_env.model)])
                    field_env.unlink()  # 删除字段
                    self._update_model()
                else:
                    self_one.delete_page_to_from()
                    self._update_model()
                    field_env = self.env['ir.model.fields'].search([('name', '=', line.label_field_id.name),
                                                                    ('model', '=', model_env.model)])
                    field_env.unlink()  # 删除字段
                    self._update_model()
            return super(AddLabel, self).unlink()

    # 找到模型默认的from视图
    @api.multi
    def _find_model_default_from(self, model_env, view_type, ):
        """
        获取模型中的from视图并返回
        :return: 返回找到的form视图
        """
        view_id = None
        View = self.env['ir.ui.view']
        result = {
                'model':model_env.model,
                'field_parent':False,
                }
        # try to find a view_id if none provided
        if not view_id:
            # <view_type>_view_ref in context can be used to overrride the default view
            view_ref_key = view_type + '_view_ref'
            view_ref = self._context.get(view_ref_key)
            if view_ref:
                if '.' in view_ref:
                    module, view_ref = view_ref.split('.', 1)
                    query = "SELECT res_id FROM ir_model_data WHERE model='ir.ui.view' AND module=%s AND name=%s"
                    self._cr.execute(query, (module, view_ref))
                    view_ref_res = self._cr.fetchone()
                    if view_ref_res:
                        view_id = view_ref_res[0]
                else:
                    _logger.warning('%r requires a fully-qualified external id (got: %r for model %s). '
                                    'Please use the complete `module.view_id` form instead.', view_ref_key,
                                    view_ref,
                                    self._name)
            if not view_id:
                # otherwise try to find the lowest priority matching ir.ui.view
                view_id = View.default_view(model_env.model, view_type)
        if view_id:
            print(view_id, 'view_id')
            # read the view with inherited views applied
            root_view = View.browse(view_id).read_combined(['id', 'name', 'field_parent', 'type', 'model', 'arch'])
            result['arch'] = root_view['arch']
            result['name'] = root_view['name']
            result['type'] = root_view['type']
            result['view_id'] = root_view['id']
            result['field_parent'] = root_view['field_parent']
            result['base_model'] = root_view['model']
        else:
            # fallback on default views methods if no ir.ui.view could be found
            try:
                arch_etree = getattr(self, '_get_default_%s_view' % view_type)()
                result['arch'] = etree.tostring(arch_etree, encoding='unicode')
                result['type'] = view_type
                result['name'] = 'default'
            except AttributeError:
                raise UserError(_("No default view of type '%s' could be found !") % view_type)
        return result

    # 在from视图中减少对应字段的页签
    @api.multi
    def delete_page_to_from(self):
        """
        给对应模型后面增加页签
        :return: 返回修正后的结果
        """
        View = self.env['ir.ui.view']
        # Get the view arch and all other attributes describing the composition of the view
        model_env = self.env['ir.model'].search([('id', '=', self.apply_to_model.id)])
        result = self._find_model_default_from(model_env, view_type='form')
        # 获取视图id
        xarch, xfields = View.postprocess_and_fields(
                model_env.model,
                etree.fromstring(result['arch']),
                result['view_id'])
        result['arch'] = xarch
        result['fields'] = xfields
        view_id = result['view_id']
        arch = etree.fromstring(
                """<data>
                       <xpath expr="//form[1]/sheet[1]/notebook[1]" position="inside">
                           <page string="标签" id="add_label">
                               <group string="标签信息">
                                </group>
                           </page>
                       </xpath>
                   </data>
                """)
        view = self.env['ir.ui.view'].browse(view_id)
        self.delete_page_field(arch)  # 删除后的对应的field加到对应页面上xpath上去
        new_arch = etree.tostring(arch, encoding='unicode', pretty_print=True)
        self._set_label_view(view, new_arch)
        ViewModel = self.env[view.model]
        studio_view = self._get_studio_view(view)  # 获取页面的位置并给到数据信息
        fields_view = ViewModel.fields_view_get(view.id, view.type)
        return {
                'fields_views':fields_view,
                'fields':ViewModel.fields_get(),
                'studio_view_id':studio_view.id,
                }

    # 在视图中减少字段
    @api.multi
    def delete_page_field(self, arch):
        """
        在删除页签上面的字段
        :return:
        """
        xpath_node = self._get_xpath_node(arch)
        delete_label = self

        def add_columns(xml_node):  # 将field 到对应的模型中 xml_node这个就是对应的模型
            # 获取模型的全部属性
            label_env = self.env['add.label'].search(
                    [('apply_to_model.id', '=', self.apply_to_model.id)])  # 这个是对应add
            # 获取对应模型的自定义字段
            model_env = self.env['ir.model'].search([('id', '=', self.apply_to_model.id)])
            for label in label_env:
                print(delete_label, ',,', label)
                for label_line in label.label_line:
                    field_env = self.env['ir.model.fields'].search([('name', '=', label_line.label_field_id.name),
                                                                    ('model', '=', model_env.model)])
                    if label_line.label_field_id.name == field_env.name:  # 去报对模型中有这个字段
                        field_name = label_line.label_field_id.name  # 这个是标签字段的名字 如 x_sale 这样的字段(这里有多个)
                        field_description = label_line.label_field_id.field_description
                        xml_page_field = etree.SubElement(xml_node, 'field', {'name':field_name})
                        xml_page_field.attrib['string'] = _(field_description)

        # Create the actual node inside the xpath. It needs to be the first
        # child of the xpath to respect the order in which they were added.
        xml_node = etree.Element('group', {})  # 这里是增加后的属性
        add_columns(xml_node)
        xpath_node.insert(0, xml_node)

    # 删除页签
    @api.multi
    def delete_from_page(self):
        """
        删除页签
        :return:
        """
        model_env = self.env['ir.model'].search([('id', '=', self.apply_to_model.id)])
        result = self._find_model_default_from(model_env, view_type='form')
        view_id = result['view_id']  # 416
        view = self.env['ir.ui.view'].browse(view_id)
        view_page = self._get_studio_view(view)  # 获取view
        view_page.unlink()  # 删除页签页面

    # 在from视图后面中添加对应的页签
    @api.multi
    def add_page_to_from(self, models_name_env):
        """
        给对应模型后面增加页签
        :return: 返回修正后的结果
        """
        View = self.env['ir.ui.view']
        # model_env = self.env['ir.model'].search([('id', '=', self.apply_to_model.id)])
        # Get the view arch and all other attributes describing the composition of the view
        result = self._find_model_default_from(models_name_env, view_type='form')
        # 获取视图id
        xarch, xfields = View.postprocess_and_fields(models_name_env.model, etree.fromstring(result['arch']),
                                                     result['view_id'])
        result['arch'] = xarch
        result['fields'] = xfields
        view_id = result['view_id']
        # self.get_label_field()  # 编辑多个标签和name的属性值
        arch = etree.fromstring(
                """<data>
                       <xpath expr="//form[1]/sheet[1]/notebook[1]" position="inside">
                           <page string="标签" id="add_label">
                               <group string="标签信息">
                                </group>
                           </page>
                       </xpath>
                   </data>
                """)
        view = self.env['ir.ui.view'].browse(view_id)

        self._field_add(arch, models_name_env)  # 件对应的field加到对应页面上xpath上去
        new_arch = etree.tostring(arch, encoding='unicode', pretty_print=True)
        self._set_label_view(view, new_arch)
        ViewModel = self.env[view.model]
        studio_view = self._get_studio_view(view)  # 获取页面的位置并给到数据信息
        fields_view = ViewModel.fields_view_get(view.id, view.type)
        return {
                'fields_views':fields_view,
                'fields':ViewModel.fields_get(),
                'studio_view_id':studio_view.id,
                }

    # 获取新的xpth
    @api.multi
    def _get_xpath_node(self, arch):
        expr = '//' + 'form[1]/sheet[1]/notebook[1]/page[@id="add_label"]/group[1]'
        return etree.SubElement(arch, 'xpath', {
                'expr':expr,
                'position':'after'
                })

    # 将全部字段添加到对应的页签中
    @api.multi
    def _field_add(self, arch, models_name_env):
        xpath_node = self._get_xpath_node(arch)

        def add_columns(xml_node):
            # 获取模型的全部属性
            label_env = self.env['add.label'].search([('apply_to_model.id', '=', models_name_env.id)])
            for label in label_env:
                for label_line in label.label_line:
                    field_name = label_line.label_field_id.name  # 这个是标签字段的名字 如 x_sale 这样的字段(这里有多个)
                    field_description = label_line.label_field_id.field_description
                    xml_page_field = etree.SubElement(xml_node, 'field', {'name':field_name})
                    xml_page_field.attrib['string'] = _(field_description)

        xml_node = etree.Element('group', {})  # 这里是增加后的属性
        add_columns(xml_node)
        xpath_node.insert(0, xml_node)

    # 给对应的tree添加一个action
    @api.multi
    def create_action_to_tree(self, models_name_env):
        """
        给对应tree的动作加上一个action的标签管理的下拉菜单
        :return: none
        """
        tree = etree.parse(PATH_add)
        root = tree.getroot()
        count = 0
        size_node = root.findall('data')[0]
        mes = etree.tostring(size_node)
        mes = mes.decode(encoding='utf-8')
        res_mns = mes.split('/>')
        for i in res_mns[0:-1]:
            # 判断是不是中间有对应模块的一个action
            re_express = r'src_model=.+'
            try:
                res = re.search(re_express, i).group(0)
            except:
                mes = self.get_action_demo(models_name_env)
                size_node.append(mes)
                tree.write(PATH_add, encoding="utf-8", xml_declaration=True)
            else:
                if res.split(' ')[0].split('"')[1] == models_name_env.model:
                    count += 1
                    break
        if count == 0:
            mes = self.get_action_demo(models_name_env)  # 没有的话就增一个
            size_node.append(mes)
            tree.write(PATH_add, encoding="utf-8", xml_declaration=True)
        self._update_model()  # 跟新模块数据
        return True

    # 编辑动作的id
    @api.multi
    def get_action_id_name(self, models_name_env):
        name_before = str(models_name_env.model)
        name_res = name_before.replace('.', '_')
        return name_res + '_action_label_id'

    @api.multi
    def get_action_demo(self, models_name_env):
        """
        actin的样式
        :return:
        """
        action_id_name = self.get_action_id_name(models_name_env)  # 获取不同 的id
        if self:
            new_action = """
                            <act_window
                                id = "%(fields)s"
                                name = "标签管理"
                                src_model = "%(field)s"
                                res_model = "btm.label.value"
                                view_mode = "form,tree"
                                view_type = "form"
                                target = "new"
                                multi = "True"/>
                        """ % {'fields':action_id_name, 'field':self.apply_to_model.name}
        else:
            new_action = """
                             <act_window
                               id = "%(fields)s"
                               name = "标签管理"
                               src_model = "%(field)s"
                               res_model = "btm.label.value"
                               view_mode = "form,tree"
                               view_type = "form"
                               target = "new"
                               multi = "True"/>
                         """ % {'fields':action_id_name, 'field':models_name_env.model}
            # 获取文件的位置并写入到对应的xml里面用xpth定位文件位置
        mes = etree.XML(new_action)
        return mes

    # 跟新模块数据信息
    @api.multi
    def _update_model(self):
        """
        调用跟新模块信息
        :return:
        """
        update_model_env = self.env['base.module.update']
        update_model_env.update_module()  # 更新本地模块
        ir_model_env = self.env['ir.module.module'].search([('name', '=', 'add_label')])
        ir_model_env.button_immediate_upgrade()

    # 删除tree中的动作标签
    @api.multi
    def delete_action(self):
        """
        删除动作标签
        :return:
        """
        model_env = self.env['ir.model'].search([('id', '=', self.apply_to_model.id)])
        tree = ET.parse(PATH_add)
        root = tree.getroot()
        root = root.findall('data')
        for action in root:
            for rem in action.findall('act_window'):
                if rem.get('src_model') == model_env.model:
                    root[0].remove(rem)
                    tree.write(PATH_add,
                               encoding="utf-8", xml_declaration=True)
                    # 外面调用更新模块
                    self._update_model()

    # 创建一个新的继承的页面
    @api.multi
    def _create_studio_view(self, view, arch):
        return self.env['ir.ui.view'].create({
                'type':view.type,
                'model':view.model,
                'inherit_id':view.id,
                'mode':'extension',
                'priority':99,
                'arch':arch,
                'name':self._generate_studio_view_name(view),
                })

    # 设置页面
    @api.multi
    def _set_label_view(self, view, arch):
        studio_view = self._get_studio_view(view)  # 这里没有数据的时候 就正常了
        if studio_view and len(arch):
            studio_view.arch_db = arch  # 如果有这替换一下更新就行
        elif studio_view:
            studio_view.unlink()  # 删除了标签 这个可以的 哈哈哈
        elif len(arch):
            self._create_studio_view(view, arch)

    # 获取页面
    @api.multi
    def _get_studio_view(self, view):  # 获取新增继续的view的id
        domain = [('inherit_id', '=', view.id), ('name', '=', self._generate_studio_view_name(view))]
        return view.search(domain, order='priority desc, name desc, id desc', limit=1)

    # 编辑和获取对应的新的页面的名字
    @api.multi
    def _generate_studio_view_name(self, view):
        return "Odoo label: %s customization" % (view.name)


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
        """
        当改变增加标签行的时候如果字段已经在此模型值提示不能增加
        :return:
        """
        model_env = self.env['ir.model'].search([('id', '=', self.label_id.apply_to_model.id),
                                                 ])
        model_manual_env = model_env.field_id
        for manual_id in model_manual_env:
            if manual_id.state == 'manual' and manual_id.name == self.label_field_id.name:
                raise ValidationError(_('%s字段在,%s中存在') % (self.label_field_id.name, self.label_id.apply_to_model.name))
        self.name = self.label_field_id.name
        self.field_description = self.label_field_id.field_description
        self.infos = self.label_field_id.infos
        self.field_ttype = self.label_field_id.ttype
