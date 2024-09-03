from odoo import models, fields, api
from odoo.addons.custom_properties.decorators import validation,check_delete_access
from odoo.exceptions import UserError, ValidationError
import time
import logging
from collections import defaultdict    
_logger = logging.getLogger(__name__)


CUSTOM_STATUS = [
    ('draft', "Draft"),
    ('wfa', "WFA"),
    ('approved', "Approved"),
    ('closed', "Closed"),
    ('rejected', "Rejected"),
    ('cancelled', "Cancelled")]

PAY_MODE = [('bank', "Bank"),
            ('cash', "Cash"),
            ('cheque', "Cheque"),
            ('neft_rtgs', "NEFT/RTGS"),
            ('others', "Others")]

TRANS_STATUS = [('direct', "Direct"),
                ('from_po', "From PO")]

ENTRY_MODE =  [('manual', "Manual"),
               ('auto', "Auto")]

WARRANTY_STATUS = [('applicable', "Applicable"),
                   ('not_applicable', "Not Applicable")]

MAIL_SMS_STATUS = [('pending', "Pending"),
                   ('sent', "Sent"),
                   ('re_sent', "Re-Send"),('not_applicable', "Not Applicable"),
                   ('sms_not_applicable', "SMS Not Applicable"),('mail_not_applicable', "Mail Not Applicable")]
JS_STATUS = [('applicable', "Applicable"),
             ('not_applicable', "Not Applicable"),
             ('jc_open', "JC Open"),
             ('jc_closed', "JC Closed")]

YEARS = [('fiscal_year', "Fiscal Year"),
         ('calendar_year',"Calendar Year")]

class FieldsDatabank(models.Model):
    _name = 'fields.databank'
    _description = 'Fields Databank'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'avatar.mixin']

    #Char
    name = fields.Char(string="Order No", readonly=True, index=True, copy=False, size=15, modified=True)
    short_name = fields.Char(string="Short Name", copy=False, size=4, modified=True,
                 help="Maximum 4 char is allowed and will accept upper case only")
    remark = fields.Char(string="Remark", copy=False) 
    quote_ref = fields.Char(string="Quotation Ref", copy=False, tracking=True, size=15)
    address = fields.Char(string="Address", size=252)
    del_address = fields.Char(string="Delivery Address", size=252,default="")## want to add company delivery address as default.
    entry_spec = fields.Char(string="Specification")
    mobile_no = fields.Char(string="Mobile No", size=15)
    mobile_no1 = fields.Char(string="Mobile No 1", size=15)
    phone_no = fields.Char(string="Phone No", size=15)
    pincode = fields.Char(string="Zip", copy=False, size=6)
    vendor_inv_no = fields.Char(string="Supplier / Vendor Invoice No", copy=False, tracking=True, size=15)
    ref_no = fields.Char(string="Customer Reference", copy=False, tracking=True, size=15)
    name_draft = fields.Char(string="Draft No", readonly=True, index=True, copy=False, size=15)
    ack_no = fields.Char(string="Acknowledgement No", copy=False, tracking=True, size=15)	
    cheque_favor = fields.Char(string="Cheque In Favor Of", copy=False, tracking=True, size=252)	
    tin_no = fields.Char(string="TIN No", copy=False, size=20)	
    pan_no = fields.Char(string="PAN No", copy=False, size=15)	
    cst_no = fields.Char(string="CST No", copy=False, size=20)	
    vat_no = fields.Char(string="VAT No", copy=False, size=20)
    ap_rej_remarks = fields.Char(string="Approved/ Reject Remark", copy=False)
    purpose = fields.Char(string="Purpose", copy=False, side=252)
    desc = fields.Char(string="Description", side=252)
    attach_desc = fields.Char(string="Description", size=150)
    gst_no = fields.Char(string="GST No", copy=False, size=15)
    invoice_status = fields.Char(string="Invoice Status", readonly=True, copy=False, default="Pending", size=15)
    payment_status = fields.Char(string="Payment Status", readonly=True, copy=False, default="Pending", size=15)
    contact_person = fields.Char(string="Contact Person", size=20)
    email = fields.Char(string="Email", copy=False, size=252)
    fax = fields.Char(string="Fax", copy=False, size=20)
    website = fields.Char(string="Website", copy=False, size=100)
    street = fields.Char(string="Street", size=252)
    street1 = fields.Char(string="Street1", size=252)
    tan_no = fields.Char(string="TAN", size=20)
    aadhar_no = fields.Char(string="Aadhar No", copy=False, tracking=True, size=12)
    account_no = fields.Char(string="Account No", copy=False, tracking=True)
    landmark = fields.Char(string="Landmark", size=252)
    state_code = fields.Char(string="State Code", help="The state code.",
		    readonly=True, copy=False, size=252)
    acc_holder_name = fields.Char(string='Account Holder Name', size=252, copy=False,\
		    help="Account holder name, in case it is different than the name of the Account Holder")
    bank_name = fields.Char(string="Bank Name", copy=False, size=252)
    ifsc_code = fields.Char(string="IFSC Code", size=11, copy=False)
    branch_name = fields.Char(string="Branch Name",size=252, copy=False)
    cin_no = fields.Char(string="CIN NO", size=21, copy=False)
    job_position = fields.Char(string="Job Position", copy=False, size=252)
    tax_name = fields.Char(string="Tax Name", copy=False, size=252)
    serial_no = fields.Char(string="Serial No", copy=False, size=252)
    mail_from = fields.Char(string="From", copy=False, size=252)
    mail_to = fields.Char(string="To", copy=False, size=252)
    mail_cc = fields.Char(string="CC", copy=False, size=252)
    mail_bcc = fields.Char(string="BCC", copy=False, size=252)
    interval = fields.Char(string="Interval", copy=False, size=252)
    from_mail_id = fields.Char(string="From Email-ID", copy=False, size=252)
    subject = fields.Char(string="Subject", copy=False, size=252)

	
    #Selection
    status = fields.Selection(selection=CUSTOM_STATUS, string="Status", readonly=True, store=True, copy=False, default='draft')
    pay_mode = fields.Selection(selection=PAY_MODE, string="Mode of Payment", copy=False, tracking=True)
    grn_type = fields.Selection(selection=TRANS_STATUS, string="GRN Type",copy=False)
    entry_from = fields.Selection(selection=TRANS_STATUS, string="Entry From", copy=False, tracking=True)
    invoice_control = fields.Selection(selection=TRANS_STATUS, string="Invoice / Billing Status", copy=False)
    entry_mode = fields.Selection(selection=ENTRY_MODE, string="Entry Mode", copy=False, 
                           tracking=True,default='manual')
    wages_type = fields.Selection(selection=TRANS_STATUS, string="Wages Type", copy=False)
    priority = fields.Selection(selection=TRANS_STATUS, string="Priority", tracking=True)
    warranty = fields.Selection(selection=WARRANTY_STATUS, string="Warranty",copy=False, tracking=True)
    email_status = fields.Selection(selection=MAIL_SMS_STATUS, string="Email Status", copy=False)
    sms_status = fields.Selection(selection=MAIL_SMS_STATUS, string="SMS Status", copy=False)
    jc_status = fields.Selection(selection=JS_STATUS, string="Job Card Status", copy=False)
    seq_num_reset = fields.Selection(selection=YEARS, string="Sequence Number Reset")
    tds = fields.Selection([('yes', "Yes"), ('no', "No")], "TDS Applicable", copy=False)
    company_type = fields.Selection(string="Company Type" ,selection=[('person', "Individual"),\
		    ('company', "Company")] ,copy=False)
    gst_category = fields.Selection([('registered', "Registered"), 
                    ('un_registered', "Un Registered")], "GST Category", copy=False)
    grade = fields.Selection([('a', "A"), ('b', "B"), ('c', "C")], "Grade", copy=False)
    rating = fields.Selection([('0', '0'), ('1', '1'), ('2', '2'),
                               ('3', '3'), ('4', '4'), ('5', '5')], string="Rating", copy=False)


    #Boolean 
    active = fields.Boolean(string="Visible", default=True)
    active_rpt = fields.Boolean(string="Visible in Report")
    active_trans = fields.Boolean(string="Visible in Transactions")
    manual_round_off = fields.Boolean(string="Apply Manual Round Off", default=False)
    trigger_del = fields.Boolean(string="Trigger Delete", default=False)

    #Many2one
    confirm_user_id = fields.Many2one('res.users', string="Confirmed By", readonly=True, 
                                      copy=False, ondelete='restrict')
    ap_rej_user_id = fields.Many2one('res.users', string="Approved/Reject By", readonly=True, 
                                     copy=False, ondelete='restrict')
    cancel_user_id = fields.Many2one('res.users', string="Cancelled By", readonly=True,
                                     copy=False, ondelete='restrict')
    update_user_id = fields.Many2one('res.users', string="Last Update By", readonly=True, copy=False,
                                    ondelete='restrict')
    attach_user_id = fields.Many2one('res.users', string="Attached By", readonly=True, copy=False,
                                    ondelete='restrict')
    user_id = fields.Many2one('res.users', string="Created By", readonly=True, copy=False,
                                    ondelete='restrict', default=lambda self: self.env.user.id)
    partner_id = fields.Many2one('res.partner', string="Partner Name", index=True,
              ondelete='restrict', tracking=True) #delegate=True,
    company_id = fields.Many2one('res.company', required=True, copy=False,
                      readonly=True, default=lambda self: self.env.company, ondelete='restrict')
    product_id = fields.Many2one('product.product', string="Product Name", 
                      ondelete='restrict', index=True)
    uom_id = fields.Many2one('uom.uom', string="UOM", ondelete='restrict')
    department_id = fields.Many2one('cm.master', string="Department", tracking=True, 
               ondelete='restrict', domain=[('status', 'in', ['active']),('active_trans', '=', True)])
    brand_id = fields.Many2one('cm.master', string="Brand", tracking=True,
               ondelete='restrict', domain=[('status', 'in', ['active']),('active_trans', '=', True)])
    model_id = fields.Many2one('cm.master', string="Model Name",
               ondelete='restrict', domain=[('status', 'in', ['active']),('active_trans', '=', True)])
    catg_id = fields.Many2one('cm.master', string="Category Name",
               ondelete='restrict', domain=[('status', 'in', ['active']),('active_trans', '=', True)])
    del_term_id = fields.Many2one('cm.master', string="Delivery Term", tracking=True,
               ondelete='restrict', domain=[('status', 'in', ['active']),('active_trans', '=', True)])
    inward_id = fields.Many2one('cm.master', string="Inward Type",
               ondelete='restrict', domain=[('status', 'in', ['active']),('active_trans', '=', True)])
    outward_id = fields.Many2one('cm.master', string="Outward Type",
               ondelete='restrict', domain=[('status', 'in', ['active']),('active_trans', '=', True)])
    trans_type = fields.Many2one('cm.master', string="Transaction Type",
               ondelete='restrict', domain=[('status', 'in', ['active']),('active_trans', '=', True)])
    city_id = fields.Many2one('cm.master', string="City",
               ondelete='restrict', domain=[('status', 'in', ['active']),('active_trans', '=', True)])
    state_id = fields.Many2one('res.country.state', string="State", ondelete='restrict')
    country_id = fields.Many2one('res.country', string="Country", ondelete='restrict')
    division_id = fields.Many2one('cm.master', string="Division", tracking=True,
               ondelete='restrict', domain=[('status', 'in', ['active']),('active_trans', '=', True)])
    project_id = fields.Many2one('cm.master', string="Project Name",
               ondelete='restrict', domain=[('status', 'in', ['active']),('active_trans', '=', True)])
    bank_id = fields.Many2one('cm.master', string="Bank Name", tracking=True,
               ondelete='restrict', domain=[('status', 'in', ['active']),('active_trans', '=', True)])
    currency_id = fields.Many2one('res.currency', string="Currency", readonly=True,
                                 copy=False, tracking=True, ondelete='restrict')
    period_id = fields.Many2one('cm.master', string="Period",
               ondelete='restrict', domain=[('status', 'in', ['active']),('active_trans', '=', True)])
    account_id = fields.Many2one('cm.master', string="Account Name",
               ondelete='restrict', domain=[('status', 'in', ['active']),('active_trans', '=', True)])
    transport_id = fields.Many2one('cm.master', string="Transport Name", #delegate=True,
               ondelete='restrict', domain=[('status', 'in', ['active']),('active_trans', '=', True)])
    employee_id = fields.Many2one('cm.master', string="Employee Name", tracking=True,
               ondelete='restrict', domain=[('status', 'in', ['active']),('active_trans', '=', True)])
    job_id = fields.Many2one('cm.master', string="Designation",
               ondelete='restrict', domain=[('status', 'in', ['active']),('active_trans', '=', True)])
    executive_id = fields.Many2one('cm.master', string="Executive", tracking=True,
               ondelete='restrict', domain=[('status', 'in', ['active']),('active_trans', '=', True)])
    segment_id = fields.Many2one('cm.master', string="Segment",
               ondelete='restrict', domain=[('status', 'in', ['active']),('active_trans', '=', True)])
    source_id = fields.Many2one('cm.master', string="Source Location",
               ondelete='restrict', domain=[('status', 'in', ['active']),('active_trans', '=', True)])
    destination_id = fields.Many2one('cm.master', string="Destination Location", tracking=True,
               ondelete='restrict', domain=[('status', 'in', ['active']),('active_trans', '=', True)])
    labor_id = fields.Many2one('cm.master', string="Labor Name",
               ondelete='restrict', domain=[('status', 'in', ['active']),('active_trans', '=', True)])
    branch_id = fields.Many2one('cm.master', string="Branch Name", tracking=True,
               ondelete='restrict', domain=[('status', 'in', ['active']),('active_trans', '=', True)])
    expense_id = fields.Many2one('cm.master', string="Expense",
               ondelete='restrict', domain=[('status', 'in', ['active']),('active_trans', '=', True)])
    tax_group_id = fields.Many2one('cm.master', string="Tax Group",
               ondelete='restrict', domain=[('status', 'in', ['active']),('active_trans', '=', True)])
    task_manager_id = fields.Many2one('res.users', string="Task Manager", tracking=True, 
                                 ondelete='restrict') #delegate=True,
    inactive_user_id = fields.Many2one('res.users', string="Inactivated By", readonly=True,
                                 copy=False, ondelete='restrict')
    title = fields.Many2one('res.partner.title', string="Title", ondelete='restrict', copy=False)
    model_name = fields.Many2one('ir.model', string="Model Name", copy=False)


    #Float
    qty = fields.Float(
        string="Quantity",
        digits=(2, 3))	
    bal_qty = fields.Float(
        string="Inward Pending Qty",
        compute='_compute_fuction',
        digits=(2, 3),
        store=True)	
    rec_qty = fields.Float(
        digits=(2, 3),
        string="Received Quantity", store=True)
    approve_qty = fields.Float(string="Approved Quantity", digits=(2, 3))
    reject_qty = fields.Float(
        string="Rejected Quantity",
        digits=(2, 3),
        store=True)
    unit_price = fields.Float(
        string="Unit Price")	
    unitprice_wt = fields.Float(
        string="Unit Price(WT)",
	help="Unit price with Taxes",
        compute='_compute_fuction',
        store=True)	
    disc_amt = fields.Float(
        string="Discount Amount",
        store=True)	
    disc_per = fields.Float(
        string="Discount(%)")	
    amt = fields.Float(
        string="Amount",
        compute='_compute_fuction',
        store=True)	
    tot_amt = fields.Float(
        string="Total Amount",
        compute='_compute_fuction',
        store=True)	
    net_amt = fields.Float(
        string="Net Amount",
        compute='_compute_fuction',
        store=True)	
    tax_amt = fields.Float(
        string="Tax amount(+)",
        compute='_compute_fuction',
        store=True)	
    bal_amt = fields.Float(
        string="Balance Amount",
        store=True)	
    other_amt = fields.Float(
        string="Other Charges(+)")	
    line_tot_amt = fields.Float(
        string="Line Total",
        compute='_compute_fuction',
        store=True)	
    tds_amt = fields.Float(
        string="TDS Amount")	
    freight_amt = fields.Float(
        string="Freight Amount")	
    amc_period = fields.Float(
        string="AMC Period(Months)")	
    tot_dis_amt = fields.Float(
        string="Total Discount Amount",
        compute='_compute_fuction',
        store=True)
    taxable_amt = fields.Float(
        string="Taxable Amount",
        compute='_compute_fuction',
        store=True)	
    round_off_amt = fields.Float(
        string="Round off amount(+/-)")	
    cgst_amt = fields.Float(
        string="CGST Amount",
        compute='_compute_fuction',
        store=True)	
    sgst_amt = fields.Float(
        string="SGST Amount",
        compute='_compute_fuction',
        store=True)	
    igst_amt = fields.Float(
        string="IGST Amount",
        compute='_compute_fuction',
        store=True)
    fixed_disc_amt = fields.Float(
        string="Fixed Discount Amount(-)",
        store=True, compute='_compute_fuction')
    grand_tot_amt = fields.Float(
        string="Grand Amount",
        store=True, compute='_compute_fuction')


    #HTML
    note = fields.Html(string="Note", copy=False)


    #Integer
    entry_seq = fields.Integer(string="Sequence", copy=False) #unique constraints
    version_no = fields.Integer(string="Version No", copy=False, readonly=True)
    cr_days = fields.Integer(string="Credit Days", copy=False)
    line_count = fields.Integer(string="Line Count", copy=False, readonly=True)


    #Text
    cancel_remarks = fields.Text(string="Cancel Remarks", copy=False)
    round_off_remark = fields.Text(string="Round Off Remarks", copy=False)
    inactive_remark = fields.Text(string="Inactive Remark", copy=False)
    closer_note = fields.Text(string="Closer Note", copy=False)
    batch_info = fields.Text(string="Info", copy=False)
    rating_feedback = fields.Text(string="Rating Feedback", copy=False)


    #Date
    from_date = fields.Date(string="From Date", default=fields.Date.today)
    to_date = fields.Date(string="To Date")
    dc_date = fields.Date(string="DC Date", copy=False, tracking=True)
    due_date = remind_date = fields.Date(string="Due Date", copy=False)
    remind_date = fields.Date(string="Reminder Date", copy=False, tracking=True)
    vendor_inv_date = fields.Date(string="Supplier / Vendor Invoice Date", copy=False, tracking=True)
    cheque_date = fields.Date(string="Cheque Date", copy=False, tracking=True)
    clearing_date = fields.Date(string="Clearing Date", copy=False)
    quote_date    = fields.Date(string="Quotation Date", default=fields.Date.today, copy=False, tracking=True)
    request_date  = fields.Date(string="Request Date", default=fields.Date.today)
    eff_from_date = fields.Date(string="Effect From Date", default=fields.Date.today)
    draft_date = fields.Date(string="Draft Date", copy=False, default=fields.Date.today)
    ack_date = fields.Date(string="Acknowledgement Date", copy=False)
    comply_date = fields.Date(string="Compliant Date", copy=False)
    receive_date = fields.Date(string="Received Date")
    ship_date = fields.Date(string="Shipping Date", copy=False)
    stmt_date = fields.Date(string="Statement Date", default=fields.Date.today)
    cr_date = fields.Date(string="Credit Date")
    dr_date = fields.Date(string="Debit Date", copy=False)
    enq_date = fields.Date(string="Enquiry Date", copy=False, default=fields.Date.today)
    customer_po_date = fields.Date(string="Customer PO Date", copy=False, tracking=True)
    join_date = fields.Date(string="Joining Date", copy=False, tracking=True, default=fields.Date.today)
    relive_date = fields.Date(string="Reliving Date", copy=False, tracking=True)
    clearing_date = fields.Date(string="Clearing Date", copy=False)
    birth_date = fields.Date(string="Date Of Birth", copy=False)
    entry_date = fields.Date(string="Entry Date", copy=False, default=fields.Date.today)
    delivery_date = fields.Date(string="Delivery Date", copy=False, tracking=True)
    fy_control_date = fields.Date(string="FY Control Date") #help="financial year"
    as_on_date = fields.Date(string="As on Date", default=fields.Date.today)
    effective_date = fields.Date(string="Effective From Date", copy=False)
    expiry_date = fields.Date(string="Expiry Date", copy=False)


    #Datetime
    confirm_date = fields.Datetime(string="Confirmed Date", readonly=True, copy=False)
    ap_rej_date = fields.Datetime(string="Approved/Reject Date", readonly=True, copy=False)
    cancel_date = fields.Datetime(string="Cancelled Date", readonly=True, copy=False)
    update_date = fields.Datetime(string="Last Update Date", readonly=True, copy=False)
    crt_date = fields.Datetime(string="Creation Date", readonly=True, copy=False, default=fields.Datetime.now)
    attach_date = fields.Datetime(string="Attached Date", readonly=True, copy=False)
    inactive_date = fields.Datetime(string="Inactivated Date", readonly=True, copy=False)

    #Many2many
    taxes_id = fields.Many2many('account.tax', string="Taxes", ondelete='restrict', check_company=True)
    attachment = fields.Many2many('ir.attachment', string="File", ondelete='restrict', check_company=True)


    @api.depends('qty','bal_qty')
    def _compute_fuction(self) -> bool:
        """ Auto sum of line count """
        self.bal_qty  = 100
        return True

    @validation
    def entry_confirm(self) -> bool:
        """ entry_confirm """
        if self.status == 'draft':
            self.write({'status': 'wfa',
                        'confirm_user_id': self.env.user.id,
                        'confirm_date': time.strftime('%Y-%m-%d %H:%M:%S')
                        })
        return True

    def entry_approve(self) -> bool:
        """ entry_approve """
        if self.status == 'wfa':
           self.write({'status': 'approved',
                        'ap_rej_user_id': self.env.user.id,
                        'ap_rej_date': time.strftime('%Y-%m-%d %H:%M:%S')
                        })
        return True

    def entry_reject(self) -> bool:
        """ entry_reject """
        if self.status == 'wfa':
            self.write({'status': 'rejected',
                        'ap_rej_user_id': self.env.user.id,
                        'ap_rej_date': time.strftime('%Y-%m-%d %H:%M:%S')
                        })
        return True

    def entry_cancel(self) -> bool:
        """ entry_cancel """
        if self.status == 'approved':
            #self._validatoins(action="cancel")
            self.write({'status': 'cancelled',
                        'cancel_user_id': self.env.user.id,
                        'cancel_date': time.strftime('%Y-%m-%d %H:%M:%S')
                        })
        return True

    def create(self, vals: dict) -> None:
        """ create """
        return super(FieldsDatabank, self).create(vals)

    def unlink(self) -> bool:
        """ Unlink Funtion """
        for rec in self:
            if not check_delete_access(self.env.user, self):
                raise UserError('Warning, You can not delete other than draft entries')
            else:
                models.Model.unlink(rec)
        return True

    def write(self, vals: dict) -> None:
        """ write """
        vals.update({'update_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                     'update_user_id': self.env.user.id, 
                       })
        return super(FieldsDatabank, self).write(vals)

    def validations(self) -> None:
        if 'entry_date' in self._fields:
           confirm_rec = self.env['fields.databank'].search([('entry_date','>',self.entry_date)])
        pass

    @validation
    def button_action(self) -> dict:
        print("--------------------------------->", self)
        return {
            'effect': {
            'fadeout': 'slow',
            'message': 'Everything Looks Good!',
	    'img_url': '/fields_databank/static/img/smily.gif',
            'type': 'rainbow_man',
                      }
               }	
        pass
