# Copyright (c) 2024, TEAMPROO and contributors
# For license information, please see license.txt

# Copyright (c) 2024, TEAMPRO and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from email import message
import re
from frappe import _
import frappe
from frappe.model.document import Document
from datetime import date, timedelta, datetime,time
from frappe.utils import (getdate, cint, add_months, date_diff, add_days,

	nowdate, get_datetime_str, cstr, get_datetime, now_datetime, format_datetime,today, format_date)
# import pandas as pd
import math
from frappe.utils import add_months, cint, flt, getdate, time_diff_in_hours
import datetime as dt
from datetime import datetime, timedelta

class AttendanceRegularize(Document):

	def on_submit(self):
		if self.corrected_shift or self.corrected_in or self.corrected_out :
			att = frappe.db.exists('Attendance',{'employee':self.employee,'attendance_date':self.attendance_date})
			frappe.db.set_value('Attendance', att, 'shift', self.corrected_shift)
			frappe.db.set_value('Attendance', att, 'in_time', self.corrected_in)
			frappe.db.set_value('Attendance', att, 'out_time', self.corrected_out)
			attendance = frappe.db.get_all('Attendance',{'name':att},['*'])
			for att in attendance:
				if att.shift and att.in_time and att.out_time :
					if att.in_time and att.out_time:
						in_time = att.in_time
						out_time = att.out_time
					if isinstance(in_time, str):
						in_time = datetime.strptime(in_time, '%Y-%m-%d %H:%M:%S')
					if isinstance(out_time, str):
						out_time = datetime.strptime(out_time, '%Y-%m-%d %H:%M:%S')
					wh = time_diff_in_hours(out_time,in_time)
					if wh > 0 :
						if wh < 24.0:
							time_in_standard_format = time_diff_in_timedelta(in_time,out_time)
							frappe.db.set_value('Attendance', att.name, 'total_working_hours', str(time_in_standard_format))
							frappe.db.set_value('Attendance', att.name, 'working_hours', wh)
						else:
							wh = 24.0
							frappe.db.set_value('Attendance', att.name, 'total_working_hours',"23:59:59")
							frappe.db.set_value('Attendance', att.name, 'working_hours',wh)
						if wh < 4:
							frappe.db.set_value('Attendance',att.name,'status','Absent')
						elif wh >= 4 and wh < 6:
							frappe.db.set_value('Attendance',att.name,'status','Half Day')
						elif wh >= 6:
							frappe.db.set_value('Attendance',att.name,'status','Present')  
						shift_st = frappe.get_value("Shift Type",{'name':att.shift},['start_time'])
						shift_et = frappe.get_value("Shift Type",{'name':att.shift},['end_time'])
						out_time = datetime.strptime(str(att.out_time),'%Y-%m-%d %H:%M:%S').time()
						shift_et = datetime.strptime(str(shift_et), '%H:%M:%S').time()
						ot_hours = None
						hh = check_holiday(att.attendance_date,att.employee)
						if not hh:
							if shift_et < out_time:
								if out_time:
									difference = time_diff_in_timedelta_1(shift_et,out_time)
									diff_time = datetime.strptime(str(difference), '%H:%M:%S').time()
									if diff_time.hour > 0:
										if diff_time.minute >= 50:
											ot_hours = time(diff_time.hour+1,0,0)
										else:
											ot_hours = time(diff_time.hour,0,0)
									elif diff_time.hour == 0:
										if diff_time.minute >= 50:
											ot_hours = time(1,0,0)
									else:
											ot_hours = "00:00:00"			
					else:
						ot_hours = "00:00:00"
					if shift_et < out_time:	
						frappe.db.set_value("Attendance",att.name,"total_overtime_hours",ot_hours)
					else:
						frappe.db.set_value("Attendance",att.name,"total_overtime_hours","00:00:00")
					if str(ot_hours) != '00:00:00':
						if shift_et < out_time and out_time:	
							ftr = [3600, 60, 1]
							if ot_hours:
								hours = ot_hours.hour
								minutes = ot_hours.minute
								seconds = ot_hours.second
								hr = hours + minutes / 60 + seconds / 3600
								frappe.errprint(hr)
							else:
								hr = 0
							ot_hr = round(hr)
							frappe.errprint(ot_hr)
							ot_hours = "00:00:00"
						else:
							ot_hr = '0.0'
					else:
						ot_hours = "00:00:00"
					if shift_et < out_time:	
						frappe.errprint(ot_hr)
						frappe.db.set_value("Attendance",att.name,"overtime_hours",ot_hr) 
					else:
						frappe.errprint("else2")
						frappe.db.set_value("Attendance",att.name,"overtime_hours",'0.0')        
								
						
				else:
					frappe.db.set_value('Attendance',att.name,'total_working_hours',"00:00:00")
					frappe.db.set_value('Attendance',att.name,'working_hours',"0.0")
					frappe.db.set_value('Attendance',att.name,'extra_hours',"0.0")
					frappe.db.set_value('Attendance',att.name,'total_extra_hours',"00:00:00")
					frappe.db.set_value('Attendance',att.name,'total_overtime_hours',"00:00:00")
					frappe.db.set_value('Attendance',att.name,'overtime_hours',"0.0")
				hh = check_holiday(att.attendance_date,att.employee)
				if not hh:
					if att.shift and att.in_time:
						shift_time = frappe.get_value(
							"Shift Type", {'name': att.shift}, ["start_time"])
						shift_start_time = datetime.strptime(
							str(shift_time), '%H:%M:%S').time()
						start_time = dt.datetime.combine(att.attendance_date,shift_start_time)
						
						if att.in_time > datetime.combine(att.attendance_date, shift_start_time):
							frappe.db.set_value('Attendance', att.name, 'late_entry', 1)
							mark_late_early(att.attendance_date, att.attendance_date)
						else:
							frappe.db.set_value('Attendance', att.name, 'late_entry', 0)
							frappe.db.set_value('Attendance', att.name, 'late_entry_time', "00:00:00")
					if att.shift and att.out_time:
						shift_time = frappe.get_value(
							"Shift Type", {'name': att.shift}, ["end_time"])
						shift_end_time = datetime.strptime(
							str(shift_time), '%H:%M:%S').time()
						end_time = dt.datetime.combine(att.attendance_date,shift_end_time)
						if att.out_time < datetime.combine(att.attendance_date, shift_end_time):
							frappe.db.set_value('Attendance', att.name, 'early_exit', 1)
							mark_late_early(att.attendance_date, att.attendance_date)
						else:
							frappe.db.set_value('Attendance', att.name, 'early_exit', 0)
							frappe.db.set_value('Attendance', att.name, 'early_out_time',"00:00:00")
				else:
					frappe.db.set_value('Attendance', att.name, 'late_entry', 0)
					frappe.db.set_value('Attendance', att.name, 'late_entry_time', "00:00:00")
					frappe.db.set_value('Attendance', att.name, 'early_exit', 0)
					frappe.db.set_value('Attendance', att.name, 'early_out_time',  "00:00:00")
			frappe.db.set_value('Attendance', att.name, 'regularize_marked', 1)
			frappe.db.set_value('Attendance', att.name, 'attendance_regularize',self.name)
	

				
	def on_cancel(self):
		att = frappe.db.exists('Attendance',{'employee':self.employee,'attendance_date':self.attendance_date})
		if att:
			att_reg = frappe.db.get_value('Attendance',{'name':att},['attendance_regularize'])
			if att_reg == self.name:
				frappe.db.set_value('Attendance', att, 'total_working_hours',"00:00:00")
				frappe.db.set_value('Attendance', att, 'working_hours',"0.0")
				frappe.db.set_value('Attendance', att, 'extra_hours',"0.0")
				frappe.db.set_value('Attendance', att, 'total_extra_hours',"00:00:00")
				frappe.db.set_value('Attendance', att, 'total_overtime_hours',"00:00:00")
				frappe.db.set_value('Attendance', att, 'overtime_hours',"0.0")
				frappe.db.set_value('Attendance', att, 'shift', '')
				frappe.db.set_value('Attendance', att, 'in_time',"00:00:00")
				frappe.db.set_value('Attendance', att, 'out_time',"00:00:00")
				frappe.db.set_value('Attendance', att, 'attendance_regularize', '')
				frappe.db.set_value('Attendance', att, 'late_entry', 0)
				frappe.db.set_value('Attendance', att, 'late_entry_time', "00:00:00")
				frappe.db.set_value('Attendance', att, 'early_exit', 0)
				frappe.db.set_value('Attendance', att, 'early_out_time',  "00:00:00")

@frappe.whitelist()
def get_assigned_shift_details(emp,att_date):
	datalist = []
	data = {}
	assigned_shift = frappe.get_value("Employee",{'name':emp},['default_shift'])
	if assigned_shift != ' ':
		shift_in_time = frappe.db.get_value('Shift Type',{'name':assigned_shift},['start_time'])
		shift_out_time = frappe.db.get_value('Shift Type',{'name':assigned_shift},['end_time'])
	else:
		shift_in_time = ' '
		shift_out_time = ' '
	if frappe.db.exists('Attendance',{'employee':emp,'attendance_date':att_date}):
		if frappe.db.get_value('Attendance',{'employee':emp,'attendance_date':att_date},['in_time']):
			first_in_time = frappe.db.get_value('Attendance',{'employee':emp,'attendance_date':att_date},['in_time'])
		else:
			first_in_time = ' ' 
		if frappe.db.get_value('Attendance',{'employee':emp,'attendance_date':att_date},['out_time']):
			last_out_time = frappe.db.get_value('Attendance',{'employee':emp,'attendance_date':att_date},['out_time'])  
		else:
			last_out_time = ' '
		if frappe.db.get_value('Attendance',{'employee':emp,'attendance_date':att_date},['shift']):
			attendance_shift = frappe.db.get_value('Attendance',{'employee':emp,'attendance_date':att_date},['shift'])   
		else:
			attendance_shift = ' '
		attendance_marked = frappe.db.get_value('Attendance',{'employee':emp,'attendance_date':att_date},['name'])
		data.update({
			'assigned_shift':assigned_shift or ' ',
			'shift_in_time':shift_in_time or '00:00:00',
			'shift_out_time':shift_out_time or '00:00:00',
			'attendance_shift':attendance_shift or ' ',
			'first_in_time':first_in_time,
			'last_out_time':last_out_time,
			'attendance_marked':attendance_marked 
		})
		datalist.append(data.copy())
		return datalist	 
	else:
		frappe.throw(_("Attendance not Marked"))

def time_diff_in_timedelta(time1, time2):
		return time2 - time1

@frappe.whitelist()
def check_holiday(date,emp):
	holiday_list = frappe.db.get_value('Employee',{'name':emp},'holiday_list')
	holiday = frappe.db.sql("""select `tabHoliday`.holiday_date,`tabHoliday`.weekly_off from `tabHoliday List`
	left join `tabHoliday` on `tabHoliday`.parent = `tabHoliday List`.name where `tabHoliday List`.name = '%s' and holiday_date = '%s' """%(holiday_list,date),as_dict=True)
	doj= frappe.db.get_value("Employee",{'name':emp},"date_of_joining")
	if holiday :
		if doj < holiday[0].holiday_date:
			if holiday[0].weekly_off == 1:
				return "WW"     
			else:
				return "HH"
			
@frappe.whitelist()
def time_diff_in_timedelta_1(time1, time2):
	diff_timedelta = timedelta(hours=time2.hour - time1.hour, 
							   minutes=time2.minute - time1.minute, 
							   seconds=time2.second - time1.second)
	return diff_timedelta

@frappe.whitelist()
def validate_attendance_regularize_duplication(employee,att_date):
	exisiting=frappe.db.exists("Attendance Regularize",{'employee':employee,'attendance_date':att_date,'docstatus':1})
	if exisiting:
		return "Already Applied"
	
@frappe.whitelist()
def mark_late_early(from_date, to_date):
	attendance = frappe.db.get_all('Attendance', {'attendance_date': ('between', (from_date, to_date))}, ['*'])
	for att in attendance:
		late_entry_value=0
		late_entry_diff=None
		if att.in_time:
			if att.shift in ['A','B']:
				shift_time = frappe.get_value("Shift Type", {'name': att.shift}, ["start_time"])
				shift_start_time = datetime.strptime(str(shift_time), '%H:%M:%S').time()
				start_time = dt.datetime.combine(att.attendance_date,shift_start_time)
				
				if att.in_time > datetime.combine(att.attendance_date, shift_start_time):
					late_entry_value=1
					late_entry_diff= att.in_time -start_time
				else:
					late_entry_value=0
					late_entry_diff=None
			if att.shift in ['C']:
				shift_time = frappe.get_value("Shift Type", {'name': att.shift}, ["start_time"])
				shift_start_time = datetime.strptime(str(shift_time), '%H:%M:%S').time()
				start_time = datetime.combine(add_days(att.attendance_date, 1), shift_start_time)
				if att.in_time > datetime.combine(add_days(att.attendance_date,1), shift_start_time):
					late_entry_value=1
					late_entry_diff= att.in_time - start_time
				else:
					late_entry_value=0
					late_entry_diff=None
			frappe.db.set_value('Attendance', att.name, 'late_entry', late_entry_value)
			frappe.db.set_value('Attendance', att.name, 'late_entry_time', late_entry_diff)
		if att.shift and att.out_time: 
			early_out_value=0
			early_out_diff=None
			if att.shift in ['A','B']:
				shift_time = frappe.get_value("Shift Type", {'name': att.shift}, ["end_time"])
				shift_end_time = datetime.strptime(str(shift_time), '%H:%M:%S').time()
				end_time = dt.datetime.combine(att.attendance_date,shift_end_time)
				if att.out_time < datetime.combine(att.attendance_date, shift_end_time):
					early_out_value=1
					early_out_diff= end_time - att.out_time
				else:
					early_out_value=0
					early_out_diff=None
				
			if att.shift == "C":
				shift_time = frappe.get_value("Shift Type", {'name': att.shift}, ["end_time"])
				shift_end_time = datetime.strptime(str(shift_time), '%H:%M:%S').time()
				end_time = dt.datetime.combine(add_days(att.attendance_date,1),shift_end_time)
				if att.out_time < datetime.combine(add_days(att.attendance_date,1), shift_end_time):
					early_out_value=1
					early_out_diff= end_time - att.out_time
				else:
					early_out_value=0
					early_out_diff= None
			frappe.db.set_value('Attendance', att.name, 'early_exit', early_out_value)
			frappe.db.set_value('Attendance', att.name, 'early_out_time',early_out_diff)

	
					   
				