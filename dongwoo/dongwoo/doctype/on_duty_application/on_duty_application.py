# Copyright (c) 2023, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class OnDutyApplication(Document):
	pass
@frappe.whitelist()
def get_employee_approvers(employee_id):
	# Fetch Employee document based on the selected employee_id
	employee_doc = frappe.get_doc('Employee', employee_id)

	# Extract approver details from the Employee document
	level_1_approver = employee_doc.get('level_1_approver')
	level_2_approver = employee_doc.get('level_2_approver')
	level_3_approver = employee_doc.get('level_3_approver')

	# Return a dictionary with the required values
	return {
		'level_1_approver': level_1_approver,
		'level_2_approver': level_2_approver,
		'level_3_approver': level_3_approver
	}

