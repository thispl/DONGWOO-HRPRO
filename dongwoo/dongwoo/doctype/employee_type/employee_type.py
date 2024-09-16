# Copyright (c) 2023, TEAMPRO and contributors
# For license information, please see license.txt
#
import frappe
from frappe.model.document import Document

class EmployeeType(Document):
	pass
@frappe.whitelist()
def update_order(type,order):
	employee = frappe.get_all("Employee",{'employee_type':type,'status':"Active"},['*'],order_by = "name")
	for emp in employee:
		frappe.db.set_value("Employee",emp.name,"order",order)
	return "OK"
