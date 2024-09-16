# Copyright (c) 2023, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class HRTimeSettings(Document):
	pass
@frappe.whitelist()
def create_appraisal(appraisal_start_date, appraisal_end_date):
	employees = frappe.db.sql("""select * from `tabEmployee` where status = 'Active' """,as_dict=1)
	for employee in employees:
		frappe.errprint(employee.designation)
		app = frappe.get_doc("Appraisal Template",employee.designation)
		apps = app.get('goals')
		appraisal = frappe.new_doc('Appraisal')
		appraisal.employee = employee.name
		appraisal.kra_template = employee.designation
		for i in apps:
			kra = i.kra
			frappe.errprint(i)
			per_weightage = i.per_weightage
			appraisal.append("goals",{
				'kra':kra,
				'per_weightage':per_weightage
			})
		appraisal.save()
		frappe.db.commit()
	frappe.msgprint("Appraisal has been created")

	