# 弹窗模型给到强制删除的功能去处理这个问题
from odoo import fields, models, api


class MandatoryDelete(models.TransientModel):
    _name = 'mandatory.delete'
    _description = 'mandatory.delete'
    
    note = fields.Char()
    
    @api.multi
    def to_datele(self):
        """
        这里处理强制删除这个东西
        :return: None
        """
        pass
