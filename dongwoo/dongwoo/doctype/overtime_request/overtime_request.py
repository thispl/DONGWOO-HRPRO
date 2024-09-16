# Copyright (c) 2023, TEAMPRO and contributors
# For license information, please see license.txt
import frappe
from datetime import datetime , timedelta
from frappe import throw,_
from frappe.utils import cstr, add_days, date_diff, getdate, format_date
import frappe
from frappe.model.document import Document
from frappe.utils import date_diff
from datetime import datetime, time
from datetime import date,datetime,timedelta
import calendar
from frappe.utils import (
	add_days,
	ceil,
	cint,
	comma_and,
	flt,
	get_link_to_form,
	getdate,
	now_datetime,
	datetime,get_first_day,get_last_day,
	nowdate,
	today,
)
class OvertimeRequest(Document):
	def on_submit(self):
		if self.is_considered_as == 'Compensatory Off':
			to_date=add_days(self.ot_date,30)
			employee=frappe.get_all('Employee',{'status':'Active'},['*'])
			leave_ledger_entries = frappe.get_all(
					"Leave Ledger Entry",
					filters={'employee': self.employee, 'leave_type': 'Compensatory Off','docstatus':('!=',2)},
					fields=["*"],
					order_by="name DESC, creation DESC",
					limit_page_length=1
				)
			if leave_ledger_entries:
				latest_leave_entry = leave_ledger_entries[0]
				employees = frappe.get_all('Overtime Request', {'employee': self.employee}, ['*'])
				ad = frappe.new_doc('Leave Ledger Entry')
				ad.employee = self.employee
				ad.employee_name = self.employee_name
				ad.from_date = self.ot_date
				ad.to_date = to_date
				ad.leave_type='Compensatory Off'
				ad.transaction_type="Leave Allocation"
				if self.total_hours >= 8 and self.total_hours < 16:
					a=latest_leave_entry.leaves
					b=1
					c=a+b
					ad.leaves=c
				if self.total_hours >= 16:
					a=latest_leave_entry.leaves
					b=2
					c=a+b
					ad.leaves=c
				ad.save()
				ad.submit()
				frappe.db.commit()
			else:
			   
				employees = frappe.get_all('Overtime Request', {'employee': self.employee}, ['*'])
				ad = frappe.new_doc('Leave Ledger Entry')
				ad.employee = self.employee
				ad.employee_name = self.employee_name
				ad.from_date = self.ot_date
				ad.to_date = to_date
				ad.leave_type='compensatory Off'
				ad.transaction_type="Leave Allocation"
				if self.total_hours >= 8 and self.total_hours < 16:
					ad.leaves=1
				if self.total_hours >= 16:
					ad.leaves=2
				ad.save()
				ad.submit()
				frappe.db.commit()

		employees = frappe.get_all('Employee', {'status': 'Active'}, ['*'])
		self.festival_allowance=0
		for emp in employees:
			# frappe.errprint('hiii')
			holi_doc = frappe.get_doc('Holiday List', emp.holiday_list)

			for holiday in holi_doc.holidays:
				if emp.name==self.employee:
					# frappe.errprint(holiday.get('holiday_date'))
					attendance=frappe.get_all('Attendance',{'employee':self.employee,'attendance_date':self.ot_date},['*'])
					for att in attendance:
						if att.total_overtime_hours.total_seconds() > 0:
							self.shift_allowance = att.shift_allowance

							# # Assuming att.total_overtime_hours is a string in the format HH:MM:SS
							# total_overtime_time = datetime.strptime(att.total_overtime_hours, "%H:%M:%S")

							# # Convert time to timedelta
							# total_overtime_timedelta = timedelta(hours=total_overtime_time.hour, minutes=total_overtime_time.minute, seconds=total_overtime_time.second)

							# Calculate the total hours, including fractional hours
							total_hours = att.total_overtime_hours.total_seconds() / 3600
							frappe.errprint(f"Calculated Total Hours: {total_hours}")
							frappe.errprint(type(total_hours))
							self.total_hours = total_hours

							
						if frappe.db.exists('Overtime Request',{'ot_date':holiday.get('holiday_date')}):
							if self.employee_type == 'Staff' :
								# frappe.errprint(int(att.working_hours))
								# frappe.errprint(int(att.employee))
								# frappe.errprint('staff')
								c=int(att.working_hours)*100
								a=get_first_day(self.ot_date)
								b=get_last_day(self.ot_date)
								cal=float((date_diff(b, a))+1)
								# frappe.errprint(cal)
								salary=emp.gross_pay
								# frappe.errprint(salary)
								amt_1=salary/cal
								tot=amt_1+c
								if att.shift=='A':
									total=tot
									shift=0
								if att.shift=='B':
									if att.working_hours >= 4:
										total=tot
										shift=30
									else:
										total=tot
								if att.shift=='C':
									if att.working_hours >= 4:
										total=tot
										shift=50
										frappe.errprint('a')
									else:
										total=tot

								# frappe.errprint(amt_1)
								self.overtime_amount=tot 
								self.shift_allowance=shift
								frappe.db.set_value("Overtime Request",self.name,"overtime_amount",tot) 
								frappe.db.set_value("Overtime Request",self.name,"shift_allowance",shift) 
								nf=frappe.get_doc('NH and FH Holidays Salary', 'NH and FH Holidays Salary')
								for i in nf.trainee_nf_holiday_salary:
									# frappe.errprint(i.holiday_date) 
									if self.ot_date == i.holiday_date:
										if i.festival_allowance=='Pongal' or 'Deepavali':
											if att.working_hours < 7:
												self.festival_allowance=500


												frappe.db.set_value("Overtime Request",self.name,"festival_allowance",'500') 

											if att.working_hours >=7 :
												# frappe.errprint(self.ot_date)
												# frappe.errprint(i.holiday_date)

												self.festival_allowance=1000

										frappe.db.set_value("Overtime Request",self.name,"festival_allowance",1000) 
										# frappe.errprint('pongaldgfd')
								if self.ot_date == i.holiday_date :
									if i.festival_allowance=='Election':
										if att.working_hours >=7 :
											self.festival_allowance=400

											frappe.db.set_value("Overtime Request",self.name,"festival_allowance",400) 
								if self.ot_date == i.holiday_date :
									if i.festival_allowance=='Other NH/FH Holidays':
										if att.working_hours >=7 :
											self.festival_allowance=300

											frappe.db.set_value("Overtime Request",self.name,"festival_allowance",300) 

								self.total_amount=tot+shift+self.festival_allowance



						if frappe.db.exists('Overtime Request',{'ot_date':holiday.get('holiday_date')}):
							if self.employee_type=='Worker' or self.employee_type=="Trainee" :
								# frappe.errprint(int(att.working_hours))
								# frappe.errprint(int(att.employee))
								# frappe.errprint('Worker')
								a=get_first_day(self.ot_date)
								b=get_last_day(self.ot_date)
								# frappe.errprint(b)
								fromdate=a
								todate=b
								cal=float((date_diff(b, a))+1)
								# frappe.errprint(cal)
								salary=emp.gross_pay
								# frappe.errprint(salary)
								amt_1=salary/cal
								tot=amt_1*2
								if att.shift=='A':
									total=tot
									shift=0
								if att.shift=='B':
									if att.working_hours >= 4:
										total=tot
										shift=30
									else:
										total=tot
								if att.shift=='C':
									if att.working_hours >= 4:
										total=tot
										shift=50
										# frappe.errprint('a')
									else:
										total=tot                       
										# frappe.errprint('b')
								if self.is_considered_as != "Compensatory Off":
									self.overtime_amount=tot 
									self.shift_allowance=shift  

									frappe.db.set_value("Overtime Request",self.name,"overtime_amount",tot) 
									frappe.db.set_value("Overtime Request",self.name,"shift_allowance",shift) 
								# frappe.errprint(total)
								nf=frappe.get_doc('NH and FH Holidays Salary', 'NH and FH Holidays Salary')
								for i in nf.trainee_nf_holiday_salary:
									# frappe.errprint(i.holiday_date) 
									if self.ot_date == i.holiday_date and self.is_considered_as != "Compensatory Off":
										if i.festival_allowance=='Pongal' or 'Deepavali':
									

											if att.working_hours >=7 :
												self.festival_allowance=300

												frappe.db.set_value("Overtime Request",self.name,"festival_allowance",300) 
											# frappe.errprint('pongal')
								if self.ot_date == i.holiday_date and self.is_considered_as != "Compensatory Off":
									if i.festival_allowance=='Election':
										if att.working_hours >=7 :
											self.festival_allowance=300
											frappe.db.set_value("Overtime Request",self.name,"festival_allowance",300) 
								if self.ot_date == i.holiday_date and self.is_considered_as != "Compensatory Off":
									if i.festival_allowance=='Other NH/FH Holidays':
										if att.working_hours >=7 :
											self.festival_allowance=200
											frappe.db.set_value("Overtime Request",self.name,"festival_allowance",200) 

								self.total_amount=tot+shift+self.festival_allowance


					
@frappe.whitelist()
def get_attendance_values(employee, ot_date):
	attendance_doc = frappe.get_all('Attendance', 
		filters={'employee': employee, 'attendance_date': ot_date},
		fields=['shift', 'out_time', 'total_working_hours', 'overtime_hours']
	)
		

	if attendance_doc:
		return {
			'shift': attendance_doc[0]['shift'],
			'out_time': attendance_doc[0]['out_time'],
			'total_working_hours': attendance_doc[0]['total_working_hours'],
			'total_overtime_hours': attendance_doc[0]['overtime_hours']
		}
	# frappe.errprint()
	else:
		frappe.throw(_('No attendance record found for the specified employee and date.'))
	
