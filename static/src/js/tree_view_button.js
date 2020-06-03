// odoo.define('hr_employee.tree_view_button', function (require) {
//     "use strict";
//     var core = require('web.core');
//     var ListView = require('web.ListView');
//     var ListController = require('web.ListController');
//     var FormView = require('web.FormView');
//     var FormController = require('web.FormController');
//
//     var ImportViewMixin = {
//         init: function (viewInfo, params) {
//             var importEnabled = 'import_enabled' in params ? params.import_enabled : true;
//             this.controllerParams.importEnabled = importEnabled;
//         },
//     };
//
//     var ImportControllerMixin = {
//         init: function (parent, model, renderer, params) {
//             this.importEnabled = params.importEnabled;
//         },
//         _bindImport: function () {
//             if (!this.$buttons) {
//                 return;
//             }
//             var self = this;
//             this.$buttons.on('click', '.o_list_tender_button_say_hello', function () {
//                 var view_type = self.viewType;
//                 var actived_id;
//                 var actived_ids = [];
//
//                 if (view_type === "form") {
//                     actived_id = self.model.get(self.handle).data.id;
//                     console.log(actived_id);
//                     // 至此你获取到了 当前form 的ID，你可以在JS里拿这着这个ID搞点事
//                     // 当然，你也可以去调用后台的方法,或者打开一个新的页面，一个新的wizard
//                 }
//                 else {
//                     var state = self.model.get(self.handle, {raw: true});
//                     for (var i = 0; i < $('tbody .o_list_record_selector input').length; i++) {
//                         if ($('tbody .o_list_record_selector input')[i].checked === true) {
//                             actived_ids.push(state.res_ids[i]);
//                         }
//                     }
//                     var ctx = state.context;
//                     ctx['active_ids'] = actived_ids;
//                     console.log(actived_ids);
//                     // 至此你获取到了你勾选的项的ID，你可以在JS里拿这着这些ID搞点事
//                     // 当然，你也可以去调用后台的方法，或者打开一个新的页面，一个新的wizard
//                 }
//                 var resmodel = "btm.label.value";
//                 var resname = "标签管理";
//                 if ((view_type === "list" && actived_ids.length >= 1 ) || (view_type === "form")) {
//                     // 这里的例子是弹出一个wizard提示，根据用户选择操作后台
//                     self.do_action
//                     ({
//                             type: 'ir.actions.act_window',
//                             name: resname,
//                             res_model: resmodel,
//                             views: [[false, 'form']],
//                             target: 'new',
//                             context: {
//                                 view_type: view_type,
//                                 active_ids: actived_ids,
//                                 actived_id: actived_id,
//                             },
//                         },
//                         {
//                             on_reverse_breadcrumb: function () {
//                                 self.reload();
//                             },
//                             on_close: function () {
//                                 self.reload();
//                             }
//                         });
//                 }
//                 else {
//                     $(function () {
//                         alert('温馨提示',"请选择你需要处理的标签记录")
//                     });
//                 }
//             });
//         }
//     };
//     拓展LIST
//     ListView.include({
//         init: function () {
//             this._super.apply(this, arguments);
//             ImportViewMixin.init.apply(this, arguments);
//         },
//     });
//
//     ListController.include({
//         init: function () {
//             this._super.apply(this, arguments);
//             ImportControllerMixin.init.apply(this, arguments);
//         },
//         renderButtons: function () {
//             this._super.apply(this, arguments);
//             ImportControllerMixin._bindImport.call(this);
//         }
//     });
// 拓展FORM
// FormView.include({
//     init: function (viewInfo) {
//         this._super.apply(this, arguments);
//         this.controllerParams.viewID = viewInfo.view_id;
//         ImportViewMixin.init.apply(this, arguments);
//     },
// });
//
// FormController.include({
//     init: function (parent, model, renderer, params) {
//         this._super.apply(this, arguments);
//         this.viewID = params.viewID;
//         ImportControllerMixin.init.apply(this, arguments);
//     },
//     renderButtons: function () {
//         this._super.apply(this, arguments); // Sets this.$buttons
//         ImportControllerMixin._bindImport.call(this);
//     }
// });
// });