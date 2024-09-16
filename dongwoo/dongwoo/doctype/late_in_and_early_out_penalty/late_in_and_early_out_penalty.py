# Copyright (c) 2023, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from datetime import datetime
from frappe import _, msgprint
from urllib.request import ftpwrapper
from frappe.model.document import Document
from frappe.utils import get_first_day, get_last_day, format_datetime,get_url_to_form,today
import frappe
from datetime import datetime, timedelta
from datetime import datetime, timedelta
import calendar


class LateInAndEarlyOutPenalty(Document):
    def on_submit(self):
        first_day_of_month = datetime.now().replace(day=1)
        last_day_of_month = (first_day_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)

        for i in self.leave_deduction:
            leave_ledger_entries = frappe.get_all(
                    "Leave Ledger Entry",
                    filters={'employee': self.employee, 'leave_type': i.leave_type},
                    fields=["*"],
                    order_by="name DESC, creation DESC",
                    limit_page_length=1
                )

            if leave_ledger_entries:
                latest_leave_entry = leave_ledger_entries[0]
                if i.leave_days != 0:
                    if i.leave_type == latest_leave_entry .leave_type:
                        ad = frappe.new_doc('Leave Ledger Entry')
                        ad.employee = latest_leave_entry.employee
                        ad.employee_name = latest_leave_entry.employee_name
                        ad.from_date = first_day_of_month
                        ad.leave_type=i.leave_type
                        ad.to_date = last_day_of_month
                        ad.transaction_type = latest_leave_entry.transaction_type
                        ad.leaves = float(latest_leave_entry.leaves) - float(i.leave_days)
                        ad.transaction_name = latest_leave_entry.transaction_name
                   
                       
                    ad.submit()
                    frappe.db.commit()
            else:
                frappe.errprint('hiii')
                first_day_of_month = datetime.now().replace(day=1)
                last_day_of_month = (first_day_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)
                if i.leave_days != 0:
                    ad = frappe.new_doc('Leave Ledger Entry')
                    ad.employee = self.employee
                    ad.employee_name = self.employee_name
                    ad.from_date = first_day_of_month
                    ad.to_date = last_day_of_month
                    ad.leave_type = i.leave_type
                    if i.leave_days != 0:
                        if i.leave_type == 'Leave Without Pay':
                            ad.leaves =float(i.leave_days)                                
                    if i.leave_days != 0:
                        if i.leave_type == 'Causal Leave':
                            ad.leaves = float(i.leave_days)   
                    if i.leave_days != 0:
                        if i.leave_type == 'Earned Leave':
                            ad.leaves = float(i.leave_days)
                            
                ad.submit()
                frappe.db.commit()
            
