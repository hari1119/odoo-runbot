from odoo import models, tools, fields, api, _

from odoo.exceptions import UserError
from functools import wraps

import re
import os

try:
  import validators
except ImportError:
  os.system('python -m pip install validators')

import validators

PATTERN : str = r'[!@#$%^&*()_+{}\[\]:;<>,.?\/\\~-]'

def check_previous_entrydate(self, date) -> bool:
    """ To check the self model previous entry date """
    return bool(self.env[self._name].with_context(active_test=False).search([
              ('entry_date','>',date),('status','in',['approved']),('id','!=',self.id)]))

def is_future_date(date) -> bool:
    """ If date is in future return True """ 
    return True if date > fields.Date.today() else False

def is_past_date(date) -> bool:
    """ If date is in past return True """ 
    return True if date < fields.Date.today() else False

def is_special_char(env, text: str, skip_chars: str = None) -> bool:
    """ Special Character Checking """
    if not skip_chars:
        skip_chars = env['ir.config_parameter'].sudo().get_param('custom_properties.skip_chars')
    special_chars: str = PATTERN
    for char in skip_chars or []:
        special_chars = special_chars.replace(char, '')
    return bool(re.search(special_chars, text))

def is_special_char_pre_or_suf(env, text: str, skip_chars:str = None) -> bool:
    """ Special Character Checking in prefix/suffix"""
    if not skip_chars:
        skip_chars = env['ir.config_parameter'].sudo().get_param('custom_properties.skip_chars')
    special_chars: str = PATTERN
    for char in skip_chars or []:
        special_chars = special_chars.replace(char, '')
    return True if len(text.strip(special_chars)) != len(text) else False

def is_negative(num: int | float) -> bool:
    """ If nagative identified return True """
    return True if num < 0 else False

def is_mobile_num(char: str) -> str:
    """check the mobile number"""
    return True if re.match("^((\+){0,1}[0-9]{10,15})$", char) == None else False

def check_duplicate_module_wise(self, field_name: str, field_value: str | int) -> bool:
    """ Module wise duplicate identifier """
    return True if self.env[self._name].with_context(active_test=False).search_count(\
                     [(f'{field_name}', '=', field_value)]) > 1 else False

def check_age_below_eighteen(birth_date: str) -> bool:
    """ Is age lesser than 18 means return True, Ex. formart should be like --> 1999-11-09 """
    year, month, day = map(int, str(birth_date).split("-"))
    today = fields.Date.today()
    #24  = 2024 - 1999 - ((5, 28) < (11, 9)
    age : int = today.year - year - ((today.month, today.day) < (month, day))
    return True if age < 18 else False

def is_alphanum(text: str) -> bool:
    """ Check other then alpha numaric """
    return text.isalnum()
def is_valid_mail(mail: str)-> bool:
    """ Email validation """
    return True if re.match(r"^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,6}$", mail) == None else False

def check_delete_access(user, record) -> bool:
    """ Record delete access based in the res.config.settings """
    return True if ((user.id == record.user_id.id\
		or record.env['ir.config_parameter'].sudo().get_param('custom_properties.del_draft_entry')\
		or user.has_group('cm_user_mgmt.group_mgmt_admin')) and\
		record.entry_mode == 'manual' and record.status == 'draft') else False

def validate_fax(fax_number: str) -> bool:
    """Validates a fax number using a regular expression."""

    pattern = r"^(\+?\d{1,3})?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$"
    return bool(re.match(pattern, fax_number))

def is_valid_website(url: str) -> bool:
    """
    Checks if a given URL is valid.
    Returns:
        True if the URL is valid, False otherwise.
    """
    return validators.url(url)

def is_valid_address(address: str) -> bool:
    """ If the address in valid pattern return True else False """
    pattern = r"\d+\s[A-Za-z\s]+\w+"
    return bool(re.match(pattern, address))

def is_valid_gst(gst_num: str) -> bool:
    """ GST (Goods and Services Tax) number """  
    regex = "^[0-9]{2}[A-Z]{5}[0-9]{4}" + "[A-Z]{1}[1-9A-Z]{1}" + "Z[0-9A-Z]{1}$"
    return bool(re.match(regex, gst_num))

def is_less_than_zero(value: int) -> bool:
    return True if value <= 0 else False

def is_number(value: str) -> bool:
    return value.isnumeric()

def is_ifsc_code(code: str) -> bool:
    regex = "^[A-Z]{4}0[A-Z0-9]{6}$"
    return bool(re.match(regex, code))
    
def validation(method) -> None:
    @wraps(method)
    def wrapper(*args, **kwargs) -> None:
        self = args[0] if args[0] else False
        warning_msg: list[str] = []
        print("<------------------------", self._fields['short_name'].modified)
        self._fields['short_name'].string = "test"
        if self:
            if self.env['ir.config_parameter'].sudo().get_param('custom_properties.server_side_validation'):
                if 'delivery_date' in self._fields and 'entry_date' in self._fields and self.delivery_date\
				and self.entry_date and self._fields['delivery_date'].modified == False:
                    if self.delivery_date < self.entry_date:
                       raise UserError("Delivery date should be greater than or equal to order date. Ref no is draft_no")
                    else:
                      pass
                else:
                    pass
                if 'from_date' in self._fields and 'to_date' in self._fields and self.from_date and self.to_date:
                    if self.from_date > self.to_date:
                       raise UserError("From date should not be greater than to date")
                    
                if 'due_date' in self._fields and 'entry_date' in self._fields and self.due_date and self.entry_date:
                    if self.entry_date > self.due_date:  
                       raise UserError("Due date should not be less than entry date")

                if 'vendor_inv_date' in self._fields and 'entry_date' in self._fields and self.vendor_inv_date\
                           and self.entry_date:
                    if self.entry_date > self.vendor_inv_date:  
                       raise UserError("Vendor invoice date should not be less than entry date")
            


                if 'quote_date' in self._fields and 'entry_date' in self._fields and self.quote_date\
                           and self.entry_date:
                    if self.entry_date < self.quote_date:  
                       raise UserError("Quotation date should not be greater than entry date")

                if 'ack_date' in self._fields and 'entry_date' in self._fields and self.ack_date\
                           and self.entry_date:
                    if self.entry_date > self.ack_date:  
                       raise UserError("Acknowledgement date should not be less than entry date")

                if 'ship_date' in self._fields and 'entry_date' in self._fields and self.ship_date\
                           and self.entry_date:
                    if self.entry_date > self.ship_date:  
                       raise UserError("Shipping date should not be less than entry date")

                if 'enq_date' in self._fields and 'entry_date' in self._fields and self.enq_date\
                           and self.entry_date:
                    if self.entry_date > self.enq_date:  
                       raise UserError("Enquiry date should not be less than entry date")

                if 'customer_po_date' in self._fields and 'entry_date' in self._fields and self.customer_po_date\
                           and self.entry_date:
                    if self.entry_date < self.customer_po_date:  
                       raise UserError("Customer PO date should not be greater than entry date")

                if 'relive_date' in self._fields and 'join_date' in self._fields and self.relive_date\
                           and self.join_date:
                    if self.join_date > self.relive_date:  
                       raise UserError("Reliving date should not be less than joining date")


                ## Future Date
                if 'entry_date' in self._fields and self.entry_date and is_future_date(self.entry_date):
                    warning_msg.append("\nOrder date should not be greater than current date")
                if 'request_date' in self._fields and self.request_date and is_future_date(self.request_date):
                    warning_msg.append("\nRequest date should not be greater than current date")
                if 'draft_date' in self._fields and self.draft_date and is_future_date(self.draft_date):
                    warning_msg.append("\nDraft date should not be greater than current date")
                if 'ack_date' in self._fields and self.ack_date and is_future_date(self.ack_date):
                    warning_msg.append("\nAcknowledgement date should not be greater than current date")
                if 'comply_date' in self._fields and self.comply_date and is_future_date(self.comply_date):
                    warning_msg.append("\nCompliant date should not be greater than current date")
                if 'receive_date' in self._fields and self.receive_date and is_future_date(self.receive_date):
                    warning_msg.append("\nReceived date should not be greater than current date")
                if 'ship_date' in self._fields and self.ship_date and is_future_date(self.ship_date):
                    warning_msg.append("\nShipping date should not be greater than current date")
                if 'enq_date' in self._fields and self.enq_date and is_future_date(self.enq_date):
                    warning_msg.append("\nEnquiry date should not be greater than current date")
                if 'join_date' in self._fields and self.join_date and is_future_date(self.join_date):
                    warning_msg.append("\nJoining date should not be greater than current date")
                if 'birth_date' in self._fields and self.birth_date and is_future_date(self.birth_date):
                    warning_msg.append("\nBirth date should not be greater than current date")
                if 'dc_date' in self._fields and self.dc_date and is_future_date(self.dc_date):
                    warning_msg.append("\nDC date should not be greater than current date")


                ## Past Date
                if 'cheque_date' in self._fields and self.cheque_date and is_past_date(self.cheque_date):
                    warning_msg.append("\nCheque date should not be less than current date")
                if 'clearing_date' in self._fields and self.clearing_date and is_past_date(self.clearing_date):
                    warning_msg.append("\nClearing date should not be less than current date")
                if 'eff_from_date' in self._fields and self.eff_from_date and is_past_date(self.eff_from_date):
                    warning_msg.append("\nEffective from date should not be less than current date")
                if 'relive_date' in self._fields and self.relive_date and is_past_date(self.relive_date):
                    warning_msg.append("\nReliving date should not be less than current date")
                if 'remind_date' in self._fields and self.remind_date and is_past_date(self.remind_date):
                    warning_msg.append("\nRemind date should not be less than current date")

                #Special characte
                if 'quote_ref' in self._fields and self.quote_ref and is_special_char(self.env, self.quote_ref):
                   warning_msg.append("\nSpecial character is not allowed in %s"%\
                                      (self._fields.get('quote_ref').string))
                if 'vendor_inv_no' in self._fields and self.vendor_inv_no and is_special_char(self.env, self.vendor_inv_no):
                   warning_msg.append("\nSpecial character is not allowed in %s"%\
                                      (self._fields.get('vendor_inv_no').string))
                if 'ref_no' in self._fields and self.ref_no and is_special_char(self.env, self.ref_no):
                   warning_msg.append("\nSpecial character is not allowed in %s"%\
                                      (self._fields.get('ref_no').string))
                if 'short_name' in self._fields and self.short_name and is_special_char(self.env, self.short_name):
                   warning_msg.append("\nSpecial character is not allowed in %s"%\
                                      (self._fields.get('short_name').string))
                if 'ack_no' in self._fields and self.ack_no and is_special_char(self.env, self.ack_no):
                   warning_msg.append("\nSpecial character is not allowed in %s"%\
                                      (self._fields.get('ack_no').string))
                if 'cheque_favor' in self._fields and self.cheque_favor and is_special_char(self.env, self.cheque_favor):
                   warning_msg.append("\nSpecial character is not allowed in %s"%\
                                      (self._fields.get('cheque_favor').string))
                if 'tin_no' in self._fields and self.tin_no and is_special_char(self.env, self.tin_no):
                   warning_msg.append("\nSpecial character is not allowed in %s"%\
                                      (self._fields.get('tin_no').string))
                if 'pan_no' in self._fields and self.pan_no and is_special_char(self.env, self.pan_no):
                   warning_msg.append("\nSpecial character is not allowed in %s"%\
                                      (self._fields.get('pan_no').string))
                if 'cst_no' in self._fields and self.cst_no and is_special_char(self.env, self.cst_no):
                   warning_msg.append("\nSpecial character is not allowed in %s"%\
                                      (self._fields.get('cst_no').string))
                if 'vat_no' in self._fields and self.vat_no and is_special_char(self.env, self.vat_no):
                   warning_msg.append("\nSpecial character is not allowed in %s"%\
                                      (self._fields.get('vat_no').string))
                if 'gst_no' in self._fields and self.gst_no:
                    if is_special_char(self.env, self.gst_no):
                       warning_msg.append("\nSpecial character is not allowed in %s"%\
                                      (self._fields.get('gst_no').string))
                if 'contact_person' in self._fields and self.contact_person:
                    if is_special_char(self.env, self.contact_person):
                       warning_msg.append("\nSpecial character is not allowed in %s"%\
                                      (self._fields.get('contact_person').string))
                if 'branch_name' in self._fields and self.branch_name:
                    if is_special_char(self.env, self.branch_name):
                       warning_msg.append("\nSpecial character is not allowed in %s"%\
                                      (self._fields.get('contact_person').string))

                if 'bank_name' in self._fields and self.bank_name:
                    if is_special_char(self.env, self.bank_name):
                       warning_msg.append("\nSpecial character is not allowed in %s"%\
                                      (self._fields.get('bank_name').string))
                if 'acc_holder_name' in self._fields and self.acc_holder_name:
                    if is_special_char(self.env, self.acc_holder_name):
                       warning_msg.append("\nSpecial character is not allowed in %s"%\
                                      (self._fields.get('acc_holder_name').string))
                if 'landmark' in self._fields and self.landmark:
                    if is_special_char(self.env, self.landmark):
                       warning_msg.append("\nSpecial character is not allowed in %s"%\
                                      (self._fields.get('landmark').string))

                #Check nagative value #SPELL CHECK
                if 'disc_amt' in self._fields and self.disc_amt and is_negative(self.disc_amt):
                   warning_msg.append("\nNegative value is not allowed in %s"\
                                                     %(self._fields.get('disc_amt').string))
                if 'disc_per' in self._fields and self.disc_per and is_negative(self.disc_per):
                   warning_msg.append("\nNegative value is not allowed in %s"\
                                                     %(self._fields.get('disc_per').string))
                if 'mobile_no' in self._fields and self.mobile_no and is_mobile_num(self.mobile_no):
                   warning_msg.append("\nNumbers only allowed in %s"\
                                                     %(self._fields.get('mobile_no').string))
                if 'mobile_no1' in self._fields and self.mobile_no1 and is_mobile_num(self.mobile_no1):
                   warning_msg.append("\nNumbers only allowed in %s"\
                                                     %(self._fields.get('mobile_no1').string))
                if 'phone_no' in self._fields and self.phone_no and is_mobile_num(self.phone_no):
                   warning_msg.append("\nNumbers only allowed in %s"\
                                                     %(self._fields.get('phone_no').string))
                #Digits
                if 'adhar_no' in self._fields and self.adhar_no and is_not_digits(self.adhar_no): #TODO
                   warning_msg.append("\nNumbers only allowed in %s"\
                                                     %(self._fields.get('adhar_no').string))
                #Age
                if 'birth_date' in self._fields and self.birth_date and check_age_below_eighteen(self.birth_date): 
                   warning_msg.append("\nAge must above 18 in %s"\
                                                     %(self._fields.get('birth_date').string))
            else:
                pass

            if 'entry_date' in self._fields and check_previous_entrydate(self, self.entry_date):
                warning_msg.append("\nOrder date should not be less than previous approved entry date")
            if 'request_date' in self._fields and check_previous_entrydate(self, self.request_date):
                warning_msg.append("\nRequest date should not be less than previous approved entry date")
            if 'draft_date' in self._fields and check_previous_entrydate(self, self.draft_date):
                warning_msg.append("\nDraft date should not be less than previous approved entry date")
            if 'comply_date' in self._fields and check_previous_entrydate(self, self.comply_date):
                warning_msg.append("\nCompliant date should not be less than previous approved entry date")
            if 'dc_date' in self._fields and check_previous_entrydate(self, self.dc_date):
                warning_msg.append("\nDC date should not be less than previous approved entry date")
            if 'remind_date' in self._fields and check_previous_entrydate(self, self.remind_date):
                warning_msg.append("\nRemind date should not be less than previous approved entry date")

            #Unique Check #SPELL CHECK
            if 'adhar_no' in self._fields and self.adhar_no and check_duplicate_module_wise(self, 'adhar_no', self.adhar_no):
                warning_msg.append(f"\nThe {self._fields.get('adhar_no').string} must be unique")
            if 'account_no' in self._fields and self.account_no and\
                 check_duplicate_module_wise(self, 'account_no', self.account_no):
                warning_msg.append(f"\nThe {self._fields.get('account_no').string} must be unique")
            if 'entry_seq' in self._fields and self.entry_seq and\
                 check_duplicate_module_wise(self, 'entry_seq', self.entry_seq):
                warning_msg.append(f"\nThe {self._fields.get('entry_seq').string} must be unique")
            if 'short_name' in self._fields and self.short_name and\
                 check_duplicate_module_wise(self, 'short_name', self.short_name):
                warning_msg.append(f"\nThe {self._fields.get('short_name').string} must be unique")
            if 'tin_no' in self._fields and self.tin_no and\
                 check_duplicate_module_wise(self, 'tin_no', self.tin_no):
                warning_msg.append(f"\nThe {self._fields.get('tin_no').string} must be unique")
            if 'pan_no' in self._fields and self.pan_no and\
                 check_duplicate_module_wise(self, 'pan_no', self.pan_no):
                warning_msg.append(f"\nThe {self._fields.get('pan_no').string} must be unique")
            if 'cst_no' in self._fields and self.cst_no and\
                 check_duplicate_module_wise(self, 'cst_no', self.cst_no):
                warning_msg.append(f"\nThe {self._fields.get('cst_no').string} must be unique")
            if 'vat_no' in self._fields and self.vat_no and\
                 check_duplicate_module_wise(self, 'vat_no', self.vat_no):
                warning_msg.append(f"\nThe {self._fields.get('vat_no').string} must be unique")
            if 'gst_no' in self._fields and self.gst_no and\
                 check_duplicate_module_wise(self, 'gst_no', self.gst_no):
                warning_msg.append(f"\nThe {self._fields.get('gst_no').string} must be unique")

            #Alpha-num
            if 'gst_no' in self._fields and self.gst_no and not is_alphanum(self.gst_no):
                warning_msg.append(f"\nOnly alphabet(a-z) and numbers(0-9) only allowed in {self._fields.get('gst_no').string}")

            #Email
            if 'email' in self._fields and self.email and is_valid_mail(self.email):
                warning_msg.append(f"\nEmail is not valid, check the given email")
            if 'from_mail_id' in self._fields and self.from_mail_id and is_valid_mail(self.from_mail_id):
                warning_msg.append(f"\nFrom mail is not valid, check the given from mail")
            if 'mail_bcc' in self._fields and self.mail_bcc and is_valid_mail(self.mail_bcc):
                warning_msg.append(f"\n{self._fields.get('mail_bcc').string} is not valid, check the given {self._fields.get('mail_bcc').string}")
            if 'mail_cc' in self._fields and self.mail_cc and is_valid_mail(self.mail_cc):
                warning_msg.append(f"\n{self._fields.get('mail_cc').string} is not valid, check the given {self._fields.get('mail_cc').string}")
            if 'mail_to' in self._fields and self.mail_to and is_valid_mail(self.mail_to):
                warning_msg.append(f"\n{self._fields.get('mail_to').string} is not valid, check the given {self._fields.get('mail_to').string}")
            if 'mail_from' in self._fields and self.mail_from and is_valid_mail(self.mail_from):
                warning_msg.append(f"\n{self._fields.get('mail_from').string} is not valid, check the given {self._fields.get('mail_from').string}")
            #Fax
            if 'fax' in self._fields and self.fax and not validate_fax(self.fax):
                warning_msg.append(f"\n{self._fields.get('fax').string} is not valid, check the given {self._fields.get('fax').string}")

            #IFSC
            if 'ifsc_code' in self._fields and self.ifsc_code and not is_ifsc_code(self.ifsc_code):
                warning_msg.append(f"\n{self._fields.get('ifsc_code').string} is not valid,\
				check the given {self._fields.get('ifsc_code').string}")

	    #Website	
            if 'website' in self._fields and self.website and not is_valid_website(self.website):
                warning_msg.append(f"\n{self._fields.get('website').string} is not valid,\
				check the given {self._fields.get('website').string}")
	   
	    #Address
            if 'street' in self._fields and self.street and not is_valid_address(self.street):
                warning_msg.append(f"\nStreet is not valid, check the given {self._fields.get('street').string}")
            if 'street1' in self._fields and self.street1 and not is_valid_address(self.street1):
                warning_msg.append(f"\nStreet1 is not valid, check the given {self._fields.get('street1').string}")

	    #GST	
            if 'gst_no' in self._fields and self.gst_no and not is_valid_gst(self.gst_no):
                warning_msg.append(f"\nGST is not valid, check the given {self._fields.get('gst_no').string}")


	    #Check Zero	
            if 'qty' in self._fields and is_less_than_zero(self.qty):
                warning_msg.append(f"\n\n {self._fields.get('qty').string} must be grather than zero.")
            if 'tds_amt' in self._fields and is_less_than_zero(self.tds_amt):
                warning_msg.append(f"\n\n {self._fields.get('tds_amt').string} must be grather than zero.")

	    #Only number
            if 'pincode' in self._fields and self.pincode and not is_number(self.pincode):
                warning_msg.append(f"\n {self._fields.get('pincode').string} must be a number values.")


        else:
            pass
        if warning_msg:
            ...
		#raise UserError(_(warning_msg))
	    #raise UserError(_("Warning!\n\nQty must be greater than zero."))
        return method(*args, **kwargs)
    return wrapper
