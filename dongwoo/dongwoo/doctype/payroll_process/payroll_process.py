# Copyright (c) 2023, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class PayrollProcess(Document):
	pass

@frappe.whitelist()
def get_leave_details(employee, date):
	allocation_records = get_leave_allocation_records(employee, date)
	leave_allocation = {}
	precision = cint(frappe.db.get_single_value("System Settings", "float_precision", cache=True))

	for d in allocation_records:
		allocation = allocation_records.get(d, frappe._dict())
		remaining_leaves = get_leave_balance_on(
			employee, d, date, to_date=allocation.to_date, consider_all_leaves_in_the_allocation_period=True
		)

		end_date = allocation.to_date
		leaves_taken = get_leaves_for_period(employee, d, allocation.from_date, end_date) * -1
		leaves_pending = get_leaves_pending_approval_for_period(
			employee, d, allocation.from_date, end_date
		)
		expired_leaves = allocation.total_leaves_allocated - (remaining_leaves + leaves_taken)

		leave_allocation[d] = {
			"total_leaves": flt(allocation.total_leaves_allocated, precision),
			"expired_leaves": flt(expired_leaves, precision) if expired_leaves > 0 else 0,
			"leaves_taken": flt(leaves_taken, precision),
			"leaves_pending_approval": flt(leaves_pending, precision),
			"remaining_leaves": flt(remaining_leaves, precision),
		}

	# is used in set query
	lwp = frappe.get_list("Leave Type", filters={"is_lwp": 1}, pluck="name")

	return {
		"leave_allocation": leave_allocation,
		"leave_approver": get_leave_approver(employee),
		"lwps": lwp,
	}