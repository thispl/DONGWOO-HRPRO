import frappe
from frappe import _, msgprint
from calendar import month, monthrange
from datetime import date, timedelta, datetime,time
from frappe.utils import cstr, cint, getdate, get_last_day, get_first_day, add_days
from frappe.utils import cstr, add_days, date_diff, getdate, format_date

def execute(filters=None):
	columns , data =[] , []
	columns = get_columns(filters)
	data = get_data(filters)
	return columns , data

def get_columns(filters):
	columns = [
		_('Date')+':Date:150',
		_('Employee')+':Data:150',
		_('Employee Name')+':Data:150',
		_('Time')+':Data:150',
		_('Meal Type')+':Data:150',

		]
	return columns

def get_data(filters):
	data =[]


	employee_id = frappe.db.sql("""select * from `tabCanteen Checkin` where date between '%s' and '%s' """ % (filters.from_date, filters.now_date), as_dict=1)

	for t in employee_id:
		time = t.time.strftime("%H:%M:%S")  # extract time portion from datetime object
		row = [t.date, t.employee, t.employee_name, time, t.meal_type]  # use extracted time string in row
		data.append(row)

	
	return data


			

