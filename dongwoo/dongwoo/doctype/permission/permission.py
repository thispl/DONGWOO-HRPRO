# Copyright (c) 2023, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from datetime import datetime
from frappe import _, msgprint
from urllib.request import ftpwrapper
from frappe.model.document import Document
from frappe.utils import get_first_day, get_last_day, format_datetime,get_url_to_form,today

class Permission(Document):
	@frappe.whitelist()
	def hour_res(self):
		data = []
		total = 0
		month_start = get_first_day(today())
		month_end = get_last_day(today())
		permission = frappe.db.get_all('Permission',{'employee':self.employee,"permission_date": ('between',(month_start,month_end))},['*'])    
		for per in permission:
			total_per_time = frappe.db.get_value('Permission',{'name':per.name},['total_time'])
			data.append(total_per_time)
		total = sum(map(int, [i for i in data if i.isdigit()]))
		total_hours = total + self.total_time
		frappe.errprint(total_hours)
		if total_hours > int(4):
			frappe.throw(_("Only 4 Hours permissions are allowed for a month"))
	
	# # Saturday Restriction Code
	@frappe.whitelist()
	def sat_res(self):
		dates = frappe.db.get_value('permission',{'employee':self.employee,},['permission_date'])
		day = self.permission_date
		date_obj = datetime.strptime(day, '%Y-%m-%d')
		if date_obj.weekday() == 5:
			frappe.throw(_("Permission not allowed in Saturday"))
@frappe.whitelist()
def att_permission_update(doc,method):
	frappe.errprint("Present")
	if frappe.db.exists("Attendance",{'attendance_date':doc.permission_date,'employee':doc.employee,'docstatus':['!=',2]}):
		frappe.errprint("if")
		att=frappe.db.get_value("Attendance",{'attendance_date':doc.permission_date,'employee':doc.employee,'docstatus':['!=',2]},['name'])
		frappe.errprint(att)
		att_perm=frappe.get_doc("Attendance",att)
		att_perm.att_permission = doc.name
		att_perm.save(ignore_permissions=True)
		frappe.db.commit()
@frappe.whitelist()
def att_permission_cancel(doc,method):
	if frappe.db.exists("Attendance",{'att_permission':doc.name,'docstatus':['!=',2]}):
		att=frappe.db.get_value("Attendance",{'att_permission':doc.name,'docstatus':['!=',2]},['name'])
		att_perm=frappe.get_doc("Attendance",att)
		att_perm.att_permission = ''
		att_perm.save(ignore_permissions=True)
		frappe.db.commit()