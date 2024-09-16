# Copyright (c) 2023, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint
from calendar import month, monthrange
from datetime import date, timedelta, datetime,time
from frappe.utils import cstr, cint, getdate, get_last_day, get_first_day, add_days
from frappe.utils import cstr, add_days, date_diff, getdate, format_date

def execute(filters=None):
	columns, data = [], []
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_columns(filters):
	columns = [
		_('Date')+':Data:150',
		_('Breakfast')+':Data:150',
		_('Lunch')+':Data:150',
		_('Dinner')+':Data:150',
		_('Supper')+':Data:150',
		 ]
	return columns

def get_data(filters):
	data = []
	dates = get_dates(filters)
	breakfast = 0
	lunch =0
	dinner =0
	supper=0
	for date in dates:
		date = datetime.strptime(date,'%Y-%m-%d')
		mon =  str(date.strftime('%Y-%m-%d'))
		breakfast = frappe.db.count('Canteen Checkin', {'date':mon,'meal_type':"Breakfast"}) or 0
		lunch = frappe.db.count('Canteen Checkin', {'date': mon, 'meal_type':"Lunch"}) or 0
		dinner = frappe.db.count('Canteen Checkin', {'date': mon, 'meal_type':"Dinner"}) or 0
		supper = frappe.db.count('Canteen Checkin', {'date': mon, 'meal_type':"Supper"}) or 0
		row= [format_date(mon),breakfast,lunch,dinner,supper]
		data.append(row)
	return data

def get_dates(filters):
	no_of_days = date_diff(add_days(filters['now_date'], 1), filters['from_date'])
	dates = [add_days(filters['from_date'], i) for i in range(0, no_of_days)]
	return dates
