# -*- coding: utf-8 -*-
# @Time    : 2020/5/19 10:52
# @Author  : logan
# @FileName: mian.py


# class WebStudioController(http.Controller):
#
#     @http.route('/web/dataset/call_kw/add.label/create', type='json', auth='user')
#     def create_fields(self, view_id, studio_view_arch, args=None):
#         IrModelFields = request.env['ir.model.fields']
#         view = request.env['ir.ui.view'].browse(view_id)
#
#         parser = etree.XMLParser(remove_blank_text=True)
#         arch = etree.fromstring(studio_view_arch, parser=parser)
#         model = view.model
#
#         # Determine whether an operation is associated with
#         # the creation of a binary field
#         def create_binary_field(op):
#             node = op.get('node')
#             if node and node.get('tag') == 'field' and node.get('field_description'):
#                 ttype = node['field_description'].get('type')
#                 is_related = node['field_description'].get("related")
#                 is_image = node['attrs'].get('widget') == 'image'
#                 return ttype == 'binary' and not is_image and not is_related
#             return False
#
#         # Every time the creation of a binary field is requested,
#         # we also create an invisible char field meant to contain the filename.
#         # The char field is then associated with the binary field
#         # via the 'filename' attribute of the latter.
#         for op in [op for op in args if create_binary_field(op)]:
#             filename = op['node']['field_description']['name'] + '_filename'
#
#             # Create an operation adding an additional char field
#             char_op = deepcopy(op)
#             char_op['node']['field_description'].update({
#                 'name': filename,
#                 'type': 'char',
#                 'field_description': _('Filename for %s') % op['node']['field_description']['name'],
#             })
#             char_op['node']['attrs']['invisible'] = '1'
#             args.append(char_op)
#
#             op['node']['attrs']['filename'] = filename
#
#         for op in args:
#             print(op, 'op')
#             # create a new field if it does not exist
#             if 'node' in op:
#                 if op['node'].get('tag') == 'field' and op['node'].get('field_description'):
#                     model = op['node']['field_description']['model_name']
#                     # Check if field exists before creation
#                     field = IrModelFields.search([
#                         ('name', '=', op['node']['field_description']['name']),
#                         ('model', '=', model),
#                     ], limit=1)
#
#                     if not field:
#                         field = self.create_new_field(op['node']['field_description'])
#                     op['node']['attrs']['name'] = field.name
#                 if op['node'].get('tag') == 'filter' and op['target']['tag'] == 'group' and op['node']['attrs'].get('create_group'):
#                     op['node']['attrs'].pop('create_group')
#                     create_group_op = {
#                         'node': {
#                             'tag': 'group',
#                             'attrs': {
#                                 'name': 'studio_group_by',
#                             }
#                         },
#                         'empty': True,
#                         'target': {
#                             'tag': 'search',
#                         },
#                         'position': 'inside',
#                     }
#                     self._operation_add(arch, create_group_op, model)
#             # set a more specific xpath (with templates//) for the kanban view
#             if view.type == 'kanban':
#                 if op.get('target') and op['target'].get('tag') == 'field':
#                     op['target']['tag'] = 'templates//field'
#
#             # call the right operation handler
#             getattr(self, '_operation_%s' % (op['type']))(arch, op, model)
#
#         # Save or create changes into studio view, identifiable by xmlid
#         # Example for view id 42 of model crm.lead: web-studio_crm.lead-42
#         new_arch = etree.tostring(arch, encoding='unicode', pretty_print=True)
#         self._set_studio_view(view, new_arch)
#
#         # Normalize the view
#         studio_view = self._get_studio_view(view)
#         try:
#             normalized_view = studio_view.normalize()
#             self._set_studio_view(view, normalized_view)
#         except ValidationError:  # Element '<...>' cannot be located in parent view
#             # If the studio view is not applicable after normalization, let's
#             # just ignore the normalization step, it's better to have a studio
#             # view that is not optimized than to prevent the user from making
#             # the change he would like to make.
#             self._set_studio_view(view, new_arch)
#
#         ViewModel = request.env[view.model]
#         fields_view = ViewModel.with_context({'studio': True}).fields_view_get(view.id, view.type)
#         view_type = 'list' if view.type == 'tree' else view.type
#
#         return {
#             'fields_views': {view_type: fields_view},
#             'fields': ViewModel.fields_get(),
#             'studio_view_id': studio_view.id,
#         }
