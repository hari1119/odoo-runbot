# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from ast import literal_eval

YEARS = [('fiscal_year', "Fiscal Year"),
         ('calendar_year',"Calendar Year")]

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    server_side_validation = fields.Boolean("Enabled Server Side Global Validation",\
                     config_parameter='custom_properties.server_side_validation')
    skip_chars = fields.Char("Allowed Special Characters",\
                     config_parameter='custom_properties.skip_chars')
    rule_checker_master  = fields.Boolean("Apply Maker & Checker Rule for Master Forms",\
                     config_parameter='custom_properties.rule_checker_master')
    rule_checker_transaction = fields.Boolean("Apply Maker & Checker Rule for Transaction Forms",\
                     config_parameter='custom_properties.rule_checker_transaction')
    seq_num_reset = fields.Selection(selection=YEARS, string="Sequence Number Reset",\
                     config_parameter='custom_properties.seq_num_reset')
    del_draft_entry = fields.Boolean("Allow to delete draft entries by all",\
                     config_parameter='custom_properties.del_draft_entry')
                    
    master_search_installed_ids = fields.Many2many(
        'ir.module.module',
        string='Installed Modules',
        help="Select the installed modules you want to include in the master "
             "search.",
        domain="[('state', '=', 'installed'),('category_id.name', '=','custom_modules')]")

    def set_values(self):
       res = super(ResConfigSettings, self).set_values()
       self.env['ir.config_parameter'].sudo().set_param('custom_properties.server_side_validation', self.server_side_validation)
       self.env['ir.config_parameter'].sudo().set_param('custom_properties.del_draft_entry', self.del_draft_entry)
       self.env['ir.config_parameter'].sudo().set_param('custom_properties.skip_chars', self.skip_chars)
       self.env['ir.config_parameter'].sudo().set_param('custom_properties.rule_checker_master', self.rule_checker_master)
       self.env['ir.config_parameter'].sudo().set_param('custom_properties.rule_checker_transaction',\
                                                           self.rule_checker_transaction)
       self.env['ir.config_parameter'].sudo().set_param('custom_properties.seq_num_reset',\
                                                           self.seq_num_reset)
       self.env['ir.config_parameter'].sudo().set_param(
            'custom_properties.master_search_installed_ids',
            self.master_search_installed_ids.ids)
                                                        
       return res

    @api.model
    def get_values(self):
       res = super(ResConfigSettings, self).get_values()
       ICPSudo = self.env['ir.config_parameter'].sudo()
       res.update(
           server_side_validation=ICPSudo.get_param('custom_properties.server_side_validation'),
           del_draft_entry=ICPSudo.get_param('custom_properties.del_draft_entry'),
           skip_chars=ICPSudo.get_param('custom_properties.skip_chars'),
           rule_checker_master=ICPSudo.get_param('custom_properties.rule_checker_master'),
           rule_checker_transaction=ICPSudo.get_param('custom_properties.rule_checker_transaction'),
           seq_num_reset=ICPSudo.get_param('custom_properties.seq_num_reset'),
           
       )
       master_search_installed_ids = self.env[
            'ir.config_parameter'].sudo().get_param(
            'custom_properties.master_search_installed_ids')
       if master_search_installed_ids:
            res.update({
                'master_search_installed_ids': [
                    (6, 0, literal_eval(master_search_installed_ids))]
            })
       return res
       
       
