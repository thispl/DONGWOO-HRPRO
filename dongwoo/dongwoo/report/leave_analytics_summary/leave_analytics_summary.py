# Copyright (c) 2024, TEAMPRO and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from functools import total_ordering
from itertools import count
import frappe
from frappe import permissions
from frappe.utils import cstr, cint, getdate, get_last_day, get_first_day, add_days,date_diff
from math import floor
from frappe import msgprint, _
from calendar import month, monthrange
from datetime import date, timedelta, datetime,time

status_map = {
	"Present": "P",
	"On Leave":"On Leave",
	"Work From Home": "WFH",
	'Half Day':'HD',
	"Absent": "A",
	"Half Day": "HD",
	"Holiday": "HH",
	"Weekly Off": "WW",
	"Leave Without Pay": "LOP",
	"Casual Leave": "CL",
	"Earned Leave": "EL",
	"Special Leave": "SPL",
	"Sick Leave":"SL",
	"Medical Leave": 'MDL',
	"Privilege Leave": "PVL",
	"Compensatory Off": "C-OFF",
}

def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_columns(filters):
	columns = []
	columns += [
		_("Employee Type") + ":Data/:120",
		_("Leave Type") + ":Data/:150",
		_("Pre-defined Reasons") + ":Data/:270",
		_('Total')+ ":Data/:80"
	]
	return columns
	
def get_leave_types():
	return frappe.db.sql("""
		SELECT name 
		FROM `tabLeave Type` 
		ORDER BY report_order ASC
	""", as_dict=True)


def get_predefined_reasons(leave_type_name):
	leave_type_doc = frappe.get_doc("Leave Type", leave_type_name)
	return [reason.pre_defined_reason for reason in leave_type_doc.pre_defined_reason_table]


def get_data(filters):
	data = []
	unique_entries = set()

	leave_types = get_leave_types()
	leave_count = frappe.db.sql("""
    SELECT COUNT(total_leave_days) as count
    FROM `tabLeave Application`
    WHERE 
        employee_type = %s 
        AND from_date BETWEEN %s AND %s
        AND docstatus != 2
    """, (filters["employee_type"], filters["from_date"], filters["to_date"]), as_dict=True)
	leave_count = leave_count[0]["count"] if leave_count else 0
	data.append([filters["employee_type"], ' ', ' ', leave_count])

	for leave_type in leave_types:
		leave_type_name = leave_type["name"]

		predefined_reasons = get_predefined_reasons(leave_type_name)

		if predefined_reasons:
			leave_count = frappe.db.sql("""
			SELECT COUNT(total_leave_days) as count
			FROM `tabLeave Application`
			WHERE 
				employee_type = %s 
				AND from_date BETWEEN %s AND %s
				AND docstatus != 2
				AND leave_type = %s
			""", (filters["employee_type"], filters["from_date"], filters["to_date"],leave_type_name), as_dict=True)
			leave_count1 = leave_count[0]["count"] if leave_count else 0
			data.append([' ',leave_type_name, ' ',leave_count1])

			all_predefined_reasons = frappe.db.sql("""
				SELECT name 
				FROM `tabPre-Defined Reason`
				ORDER BY name ASC
			""", as_dict=True)

			for predefined_reason in all_predefined_reasons:
				reason_name = predefined_reason["name"]
				unique_key = (leave_type_name, reason_name)

				if unique_key not in unique_entries and frappe.db.exists(
					"Pre Defined Reason Table",
					{'parent': leave_type_name, 'pre_defined_reason': reason_name}
				):
					unique_entries.add(unique_key)
					leave_count = frappe.db.sql("""
					SELECT COUNT(total_leave_days) as count
					FROM `tabLeave Application`
					WHERE 
						employee_type = %s 
						AND from_date BETWEEN %s AND %s
						AND docstatus != 2
						AND leave_type = %s
						AND pre_defined_reson = %s
					""", (filters["employee_type"], filters["from_date"], filters["to_date"],leave_type_name,reason_name), as_dict=True)
					leave_count3 = leave_count[0]["count"] if leave_count else 0
					data.append([' ', ' ',reason_name,leave_count3])

		else:
			leave_count = frappe.db.sql("""
			SELECT COUNT(total_leave_days) as count
			FROM `tabLeave Application`
			WHERE 
				employee_type = %s 
				AND from_date BETWEEN %s AND %s
				AND docstatus != 2
				AND leave_type = %s
			""", (filters["employee_type"], filters["from_date"], filters["to_date"],leave_type_name), as_dict=True)
			leave_count2 = leave_count[0]["count"] if leave_count else 0
			data.append([' ',leave_type_name, ' ',leave_count2])

	return data


def get_dates(from_date,to_date):
	no_of_days = date_diff(add_days(to_date, 1), from_date)
	dates = [add_days(from_date, i) for i in range(0, no_of_days)]
	return dates

def get_employees(filters):
	conditions = ''
	left_employees = []
	if filters.employee_type:
		conditions += "and employee_type = '%s' " % (filters.employee_type)
	employees = frappe.db.sql("""select * from `tabEmployee` where status = 'Active' %s """ % (conditions), as_dict=True)
	left_employees = frappe.db.sql("""select * from `tabEmployee` where status = 'Left' and relieving_date >= '%s' %s """ %(filters.from_date,conditions),as_dict=True)
	employees.extend(left_employees)
	return employees
		
def check_holiday(date,emp):
	holiday_list = frappe.db.get_value('Employee',{'name':emp},'holiday_list')
	holiday = frappe.db.sql("""select `tabHoliday`.holiday_date,`tabHoliday`.weekly_off from `tabHoliday List` 
	left join `tabHoliday` on `tabHoliday`.parent = `tabHoliday List`.name where `tabHoliday List`.name = '%s' and holiday_date = '%s' """%(holiday_list,date),as_dict=True)
	doj= frappe.db.get_value("Employee",{'name':emp},"date_of_joining")
	status = ''
	if holiday :
		if doj <= holiday[0].holiday_date:
			if holiday[0].weekly_off == 1:
				status = "WW"     
			else:
				status = "HH"
		else:
			status = '-'
	return status

@frappe.whitelist()
def get_to_date(from_date):
	return get_last_day(from_date)