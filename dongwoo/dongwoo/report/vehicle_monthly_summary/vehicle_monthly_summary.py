# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import erpnext
from datetime import date
from calendar import month, monthrange
from datetime import date, timedelta, datetime,time
from frappe.utils import cstr, cint, getdate, get_last_day, get_first_day, add_days
from frappe.utils import cstr, add_days, date_diff, getdate, format_date


def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data


def get_columns(filters):
	columns = []
	columns += [
		_("Description") + ":Link/Employee:150"
	]
	dates = get_dates(filters)
	for date in dates:
		date = datetime.strptime(date,'%Y-%m-%d')
		day = datetime.date(date).strftime('%d')
		columns.extend([day])
	return columns

def get_dates(filters):
	no_of_days = date_diff(add_days(filters['to_date'], 1), filters['from_date'])
	dates = [add_days(filters['from_date'], i) for i in range(0, no_of_days)]
	return dates
		
def get_data(filters):
	data = []
	des = frappe.db.sql(""" select * from `tabVehicle Check List` """,as_dict=True)
	for ve in des:
		# frappe.errprint(ve)	
		row = [ve.name]
		dates = get_dates(filters)
		for date in dates:
			vce = frappe.get_value("Vehicle Checklist Entry",{'date':date,'vehicle':filters.vehicle},['name']) or ''
			# frappe.errprint(vce)
			con = frappe.get_value("Checklist Table",{'parent':vce,'description':ve.name},['select']) or '-'
			# frappe.errprint(con)
			if con == "YES":
				row += ["✔"]
			elif con == "NO":
				row += ["✘"]
			else:
				row += ["-"]	

		data.append(row)
	return data