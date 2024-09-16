import frappe
from frappe import _, msgprint
import math

def execute(filters=None):
	columns , data =[] , []
	columns = get_columns(filters)
	data = get_data(filters)
	return columns , data

def get_columns(filters):
	columns = [
		_('Date')+':Data:150',
		_('Employee')+':Data:150',
		_('Employee Name')+':Data:150',
		_('Breakfast')+':Data:150',
		_('Lunch')+':Data:150',
		_('Dinner')+':Data:150',
		_('Supper')+':Data:150',
		_('Total')+':Data:150',
        ]
	return columns

def get_data(filters):
	data =[]
	employee_id= frappe.db.sql("""select * from `tabEmployee` where status = 'Active' """,as_dict=1)
	breakfast = 0
	lunch = 0
	dinner = 0
	supper = 0
	total = 0
	b_data = "✘"
	l_data = "✘"
	d_data = "✘"
	s_data = "✘"
	for t in employee_id:
		username = frappe.db.sql("""select * from `tabCanteen Checkin` where employee = '%s' and date = '%s' """%(t.employee,filters.date),as_dict=1)
		for i in username:
			if i.meal_type == "Breakfast":
				breakfast = 1
				b_data = "✔"
			elif i.meal_type == "Lunch":
				lunch = 1
				l_data = "✔"
			elif i.meal_type == "Dinner":
				dinner = 1
				d_data = "✔"
			else:
				supper = 1
				s_data = "✔"
		total = breakfast + lunch + dinner + supper
		row = [filters.date,t.employee,t.employee_name,b_data,l_data,d_data,s_data,int(total)]
		data.append(row)
	
	return data

			

