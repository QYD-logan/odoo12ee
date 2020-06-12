# -*- coding: utf-8 -*-

# class GroupDatabase(http.Controller):
#     @http.route('/group_database/group_database/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/group_database/group_database/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('group_database.listing', {
#             'root': '/group_database/group_database',
#             'objects': http.request.env['group_database.group_database'].search([]),
#         })

#     @http.route('/group_database/group_database/objects/<model("group_database.group_database"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('group_database.object', {
#             'object': obj
#         })
