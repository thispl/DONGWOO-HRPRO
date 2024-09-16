# Copyright (c) 2023, TEAMPRO and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from functools import total_ordering
from itertools import count
import frappe
from frappe import permissions
from frappe.utils import cstr, cint, getdate, get_last_day, get_first_day, add_days
from frappe.utils import cstr, add_days, date_diff, getdate, format_date
from math import floor
from frappe import msgprint, _
from calendar import month, monthrange
from datetime import date, timedelta,datetime, time
import datetime as dt


def execute(filters=None):
	columns1 = get_columns1(filters)
	data = get_data(filters)
	return columns1, data

def get_columns1(filters):
	columns1 = []
	columns1 += [
		_("Work Spot") + ":Data/:150",
		_("Shift") + ":Data/:200",
	]
	dates = get_dates(filters.from_date,filters.to_date)
	for date in dates:
		date = datetime.strptime(date,'%Y-%m-%d')
		day = datetime.date(date).strftime('%d')
		columns1.append(_(day) + ":Data/:70")
	columns1.append(_("Total") + ":Data/:100")
	return columns1

def get_data(filters):
	data = []
	row = []
	dates = get_dates(filters.from_date, filters.to_date)
	
	
	workspot = frappe.db.sql("""select * from `tabWorkspot` order by name ASC""",as_dict = 1)
	for w in workspot:
		row = [w.name]
		shift = frappe.db.get_all("Shift Type", ["*"],order_by = "name ASC")
		data.append(row)
		for s in shift:
			monthly_count = 0
			daily_count = 0
			row1 = ["",s.name + ' Shift']
			for date in dates:
				daily_count = frappe.db.sql("""
					SELECT COUNT(*) AS count 
					FROM `tabAttendance` 
					WHERE attendance_date = %s AND docstatus != 2 AND shift = %s AND employee_type = %s AND workspot = %s
				""", (date,s.name,filters.employee_type,w.name), as_dict=True)[0]
				frappe.errprint(daily_count['count'])
				row1.append(daily_count['count'])
				row.append("")
				monthly_count += daily_count['count']			
			row1.append(monthly_count)
			row.append("")
			data.append(row1)
	shift = frappe.db.get_all("Shift Type", ["*"],order_by = "name ASC")
	row=["Total"]
	data.append(row)
	for s in shift:
		day_count = 0
		month_count = 0
		row1 = ["",s.name + ' Shift']
		for date in dates:
			day_count = frappe.db.sql("""
				SELECT count(*) as count 
				FROM `tabAttendance` 
				WHERE attendance_date = %s 
					AND shift = %s 
					AND docstatus != 2 
					AND employee_type = %s
					AND workspot != NULL
			""", (date, s.name, filters.employee_type), as_dict=True)[0]
			row1.append(day_count['count'])
			row.append("")
			month_count +=(day_count['count'])
		row1.append(month_count)
		row.append("")
		data.append(row1)
	return data

def get_dates(from_date,to_date):
	no_of_days = date_diff(add_days(to_date, 1), from_date)
	dates = [add_days(from_date, i) for i in range(0, no_of_days)]
	return dates


