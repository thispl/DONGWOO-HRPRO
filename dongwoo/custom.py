import frappe
from datetime import datetime , timedelta
from frappe import throw,_
from frappe.utils import cstr, add_days, date_diff, getdate, format_date


@frappe.whitelist()
def get_urc_to_ec(from_date):
	print("HI")
	urc = frappe.db.sql("""select biometric_pin,biometric_time,log_type,locationdevice_id,name from `tabUnregistered Employee Checkin` where date(biometric_time) = '%s' """%(from_date),as_dict=True)
	for uc in urc:
		pin = uc.biometric_pin
		time = uc.biometric_time
		dev = uc.locationdevice_id
		typ = uc.log_type
		nam = uc.name
		if time != "":
			if frappe.db.exists('Employee',{'name':pin}):
				if frappe.db.exists('Employee Checkin',{'biometric_pin':pin,"time":time}):
					print("HI")
				else:
					print("HII")
					ec = frappe.new_doc('Employee Checkin')
					ec.biometric_pin = pin
					ec.employee = frappe.db.get_value('Employee',{'biometric_pin':pin},['employee_number'])
					ec.time = time
					ec.device_id = dev
					ec.log_type = typ
					ec.save(ignore_permissions=True)
					frappe.db.commit()
					print("Created")
					attendance = frappe.db.sql(""" delete from `tabUnregistered Employee Checkin` where name = '%s' """%(nam))
					print("Deleted")       
			else:
				print("hello")
	return "ok"

@frappe.whitelist()
def create_hooks_att():
	job = frappe.db.exists('Scheduled Job Type', 'push_punch')
	if not job:
		att = frappe.new_doc("Scheduled Job Type")
		att.update({
			"method": 'dongwoo.mark_attendance.mark_att',
			"frequency": 'Cron',
			"cron_format": '*/25 * * * *'
		})
		att.save(ignore_permissions=True)

@frappe.whitelist()
def get_summary(emp, year_start_date, year_end_date):
	att = frappe.db.sql("SELECT COUNT(*) AS count FROM `tabAttendance` WHERE employee = '%s' AND docstatus != 2 AND attendance_date BETWEEN '%s' AND '%s'" % (emp, year_start_date, year_end_date), as_dict=True) or [{'count': 0}]
	# frappe.errprint(att[0]['count'])

	att_p = frappe.db.sql("SELECT COUNT(*) AS count FROM `tabAttendance` WHERE employee = '%s' AND docstatus != 2 AND status = 'Present' AND attendance_date BETWEEN '%s' AND '%s'" % (emp, year_start_date, year_end_date), as_dict=True) or [{'count': 0}]
	# frappe.errprint(att_p[0]['count'])

	att_a = frappe.db.sql("SELECT COUNT(*) AS count FROM `tabAttendance` WHERE employee = '%s' AND docstatus != 2 AND status = 'Absent' AND attendance_date BETWEEN '%s' AND '%s'" % (emp, year_start_date, year_end_date), as_dict=True) or [{'count': 0}]
	# frappe.errprint(att_a[0]['count'])

	att_l = frappe.db.sql("SELECT COUNT(*) AS count FROM `tabAttendance` WHERE employee = '%s' AND docstatus != 2 AND status = 'On Leave' AND attendance_date BETWEEN '%s' AND '%s'" % (emp, year_start_date, year_end_date), as_dict=True) or [{'count': 0}]
	# frappe.errprint(att_l[0]['count'])

	att_h = frappe.db.sql("SELECT COUNT(*) AS count FROM `tabAttendance` WHERE employee = '%s' AND docstatus != 2 AND status = 'Half Day' AND attendance_date BETWEEN '%s' AND '%s'" % (emp, year_start_date, year_end_date), as_dict=True) or [{'count': 0}]
	# frappe.errprint(att_h[0]['count'])

	att_w = frappe.db.sql("SELECT COUNT(*) AS count FROM `tabAttendance` WHERE employee = '%s' AND docstatus != 2 AND status = 'Work From Home' AND attendance_date BETWEEN '%s' AND '%s'" % (emp, year_start_date, year_end_date), as_dict=True) or [{'count': 0}]
	# frappe.errprint(att_w[0]['count'])

	if att[0]['count'] != 0:
		p = round((att_p[0]['count'] or 0) / att[0]['count'] * 100, 2)
		# frappe.errprint(p)
		a = round((att_a[0]['count'] or 0) / att[0]['count'] * 100, 2)
		# frappe.errprint(a)
		l = round((att_l[0]['count'] or 0) / att[0]['count'] * 100, 2)
		# frappe.errprint(l)
		h = round((att_h[0]['count'] or 0) / att[0]['count'] * 100, 2)
		# frappe.errprint(h)
		w = round((att_w[0]['count'] or 0) / att[0]['count'] * 100, 2)

		data  = ''
		data = "<table style='width:100%'>"
		data += "<tr><td colspan = 24 style ='text-align:center;border:1px solid black;background-color:#3d316c;color:white;'><b>Overall Summary</b></td></tr>"
		data += "<tr><td colspan = 4 style ='text-align:center;border:1px solid black'><b>Status</b></td><td colspan = 4 style ='text-align:center;border:1px solid black'><b>Present</b></td><td colspan = 4 style ='text-align:center;border:1px solid black'><b>Absent</b></td><td colspan = 4 style ='text-align:center;border:1px solid black'><b>Half Day</b></td><td colspan = 4 style ='text-align:center;border:1px solid black'><b>On Leave</b></td><td colspan = 4 style ='text-align:center;border:1px solid black'><b>Work From Home</b></td></tr>"	
		data += "<tr><td colspan = 4 style ='text-align:center;border:1px solid black'><b>Percentage</b></td><td colspan = 4 style ='text-align:center;border:1px solid black'><b>%s</b></td><td colspan = 4 style ='text-align:center;border:1px solid black'><b>%s</b></td><td colspan = 4 style ='text-align:center;border:1px solid black'><b>%s</b></td><td colspan = 4 style ='text-align:center;border:1px solid black'><b>%s</b></td><td colspan = 4 style ='text-align:center;border:1px solid black'><b>%s</b></td></tr>"%(p,a,l,h,w)	
		data += "</table>"
		return data



@frappe.whitelist()
def employee_list(employee):
	employee=frappe.get_value("Employee",{"name":employee},["employee_number"])
	return employee
@frappe.whitelist()
def employee_list_value(employee):
	employee=frappe.get_value("Employee",{"name":employee},["employee_number"])
	return employee

@frappe.whitelist()
def update_designation(staffing_plan):
	designations = []
	staffing_plan_doc = frappe.get_doc("Staffing Plan", staffing_plan)   
	for detail in staffing_plan_doc.staffing_details:
		designations.append(detail.designation)   
	return designations,staffing_plan

@frappe.whitelist()
def update_designation_from_staffing_plan(staffing):
	staff = frappe.get_all("Staffing Plan Detail",{'parent':staffing},['*'])
	return staff

@frappe.whitelist()
def update_resume(job_applicant):
	doc=frappe.get_doc("Job Applicant",job_applicant)
	resume = doc.resume1
	return resume

@frappe.whitelist()
def date_of_joining():
	doj =frappe.get_all("Employee",{"status":"Active"},["date_of_joining","service_years_in_dwsi","name"])
	for i in doj:
		if i.date_of_joining:
			if not i.service_years_in_dwsi:
				print(i.date_of_joining)
				date_of_joining = i.date_of_joining 
				today = datetime.now()
				date = date_of_joining
				year = today.year - date.year
				month = today.month - date.month
				day = today.day - date.day

				if day < 0:
					month -= 1
					last_month_date = today.replace(day=1) - timedelta(days=1)
					day += last_month_date.day

				if month < 0:
					year -= 1
					month += 12
				value = (f"{year} Years {month} Month {day} Days")
				frappe.db.set_value("Employee",i.name,"service_years_in_dwsi",value) 

@frappe.whitelist()
def inactive_employee(doc,method):
	if doc.status=="Active":
		if doc.relieving_date:
			throw(_("Please remove the relieving date for the Active Employee."))
		
@frappe.whitelist()
def employee_type():
	from_date = "2023-11-01"
	to_date = "2023-11-07"
	attendance = frappe.db.sql("""select * from `tabAttendance` where attendance_date between '%s' and '%s' """%(from_date,to_date),as_dict=True)
	# att=frappe.db.get_value("Attendance",{"attendance_date":},["employee_type"])
	for att in attendance:
		print(att.name)
		if att.employee_type=="Worker" or att.employee_type=='D . Trainee':
			workspot=frappe.db.get_value("Employee",{"employee_number":att.employee},['workspot']) or ''
			if workspot:
				print(workspot)
				frappe.db.set_value("Attendance",att.name,'workspot',workspot)
		elif att=='Contract Employee':
			workspot=frappe.db.get_value("Workspot for CL",{"employee":att.employee,"date":att.attendance_date},['workspot']) or ''
			if workspot:
				print(workspot)
				frappe.db.set_value("Attendance",att.name,'workspot',workspot)

@frappe.whitelist()
def del_dept():
	dept=frappe.db.get_all("Designation",['*'])
	for d in dept:
		if not frappe.db.exists("Employee",{"designation":d.name}):
			frappe.db.sql("""delete from `tabDesignation` where name = %s""", (d.name),as_dict=True)
		else:
			print("hi")


	
@frappe.whitelist()
def update_salary():
	current_date = frappe.utils.nowdate()
	frappe.errprint(current_date)
	current_fiscal_year = frappe.get_value("Fiscal Year",{"year_start_date": ("<=", current_date), "year_end_date": (">=", current_date)}, fieldname="name")
	return current_fiscal_year


@frappe.whitelist()
def attendance_calc(from_date,to_date):
	
	late_count=0
	late_count1=0
	ad=''
	
	employees = frappe.get_all("Employee", {"status": "Active"}, ["*"])
	
	for emp in employees:
		shifts = frappe.get_all('Shift Type', ['*'])
		
		for shift in shifts:
			late_count = frappe.db.sql("""
				SELECT COUNT(name) AS count
				FROM `tabAttendance`
				WHERE
					employee = %s AND shift = %s
					AND time(in_time) > %s
					AND attendance_date BETWEEN %s AND %s
			""", (emp.name, shift.name, shift.start_time, from_date, to_date), as_dict=True)[0].count or 0

			print(f"Employee: {emp.name}, Shift: {shift.name}, shift:{shift.start_time} Late Count: {late_count}")

			late_count1 = frappe.db.sql("""
				SELECT COUNT(name) AS count
				FROM `tabAttendance`
				WHERE
					employee = %s AND shift = %s
					AND time(out_time) < %s
					AND attendance_date BETWEEN %s AND %s
			""", (emp.name, shift.name, shift.start_time, from_date, to_date), as_dict=True)[0].count or 0

			print(f"Employee: {emp.name}, Shift: {shift.name}, shift:{shift.start_time} Late Count: {late_count}")
			if late_count > 0 or late_count1 > 0:
				print('hiii')

				if not frappe.db.exists("Late In and Early Out Penalty", {"employee": emp.name,"from_date":from_date,"to_date":to_date}):
					ad = frappe.new_doc('Late In And Early Out Penalty')
					ad.employee = emp.name
					frappe.errprint(ad.employee)
					ad.employee_name=emp.first_name
					ad.designation=emp.designation
					ad.from_date=from_date
					ad.to_date=to_date
					ad.total_no_of_late_in=late_count
					ad.total_no_of_early_out=late_count1
					total=late_count+late_count1
					ad.total_no_of_late_deductions_day=total
					if total > 0:
						late=total/2
						ad.late_penalty_day=late
					leave=frappe.get_all('Leave Allocation',{'employee_name':emp.first_name},['*'])
					for j in leave:
						if j.leave_type not in ["Compensatory Off",'Sick Leave']:
							ad.append(
								"leave_deduction",
								{
									"leave_type": j.leave_type,
									"leave_balance": j.new_leaves_allocated,
			},
		)

					
					frappe.db.commit()
					ad.save(ignore_permissions=True)
					frappe.errprint("Late Penalty Created via Additional Salary")
				else:
					ad = frappe.get_doc('Late In And Early Out Penalty',{"employee": emp.name,"from_date":from_date,"to_date":to_date})
					ad.employee = emp.name
					ad.employee_name=emp.first_name
					ad.designation=emp.designation
					ad.from_date=from_date
					ad.to_date=to_date
					ad.total_no_of_late_in=late_count+ad.total_no_of_late_in
					ad.total_no_of_early_out=late_count1+ad.total_no_of_early_out
					total=late_count+late_count1
					ad.total_no_of_late_deductions_day=total+ad.total_no_of_late_deductions_day
					if total > 0:
						late=total/2
						ad.late_penalty_day=late+ad.late_penalty_day
					frappe.db.commit()
					ad.save(ignore_permissions=True)
					frappe.errprint("Late Penalty Created via Additional Salary")
				# return 'ok'


@frappe.whitelist()
def delete_department():
	dept = frappe.db.sql("""update `tabAttendance` set department = "HK & Garden" where department = "Garden"  """,as_dict = True)
	emptype = frappe.db.sql("""update `tabAttendance` set employee_type = "D . Trainee" where employee_type = "Trainee"  """,as_dict = True)
	# dept = frappe.db.sql("""update `tabEmployee Transfer` where employee = "DWSI1234" """,as_dict = True)
	# dept = frappe.db.sql("""update `tabEmployee Checkin` where employee = "DWSI1234" """,as_dict = True)
	# dept = frappe.db.sql("""update `tabShift Assignment` where employee = "DWSI1234" """,as_dict = True)
	# dept = frappe.db.sql("""update `tabEmployee` where name = "DWSI1234" """,as_dict = True)
	# dept = frappe.db.sql("""update `tabDesignation` where name = "Jr. Engineer" """,as_dict = True)
	# dept = frappe.db.sql("""update `tabLeave Allocation` set department = "IT" where department = "Network"  """,as_dict = True)
	# dept = frappe.db.sql("""update `tabLeave Application` set department = "IT" where department = "Network"  """,as_dict = True)
	# dept = frappe.db.sql("""update `tabSalary Slip` set department = "IT" where department = "Network"  """,as_dict = True)
	



@frappe.whitelist()
def get_reasons(leave_type):
	doc = frappe.get_doc("Leave Type", leave_type)
	reasons = [reason.pre_defined_reason for reason in doc.pre_defined_reason_table]
	return reasons

@frappe.whitelist()
def null_attendance():
	checkin = frappe.db.sql("""
		update `tabAttendance`
		set total_overtime_hours = null
		where attendance_date between "2024-04-30" and "2024-04-30"
	""", as_dict=True)
	checkin = frappe.db.sql("""
		update `tabAttendance`
		set in_time = null
		where attendance_date between "2024-04-30" and "2024-04-30"
	""", as_dict=True)
	checkin = frappe.db.sql("""
		update `tabAttendance`
		set out_time = null
		where attendance_date between "2024-04-30" and "2024-04-30"
	""", as_dict=True)
	checkin = frappe.db.sql("""
		update `tabAttendance`
		set out_time = null
		where attendance_date between "2024-04-30" and "2024-04-30"
	""", as_dict=True)
	checkin = frappe.db.sql("""
		update `tabAttendance`
		set total_extra_hours = null
		where attendance_date between "2024-04-30" and "2024-04-30"
	""", as_dict=True)
	checkin = frappe.db.sql("""
		update `tabAttendance`
		set shift=" "
		where attendance_date between "2024-04-30" and "2024-04-30"
	""", as_dict=True)
	# checkin = frappe.db.sql("""
	#     update `tabAttendance`
	#     set extra_hours = " "
	#     where attendance_date between "2024-04-30" and "2024-04-30"
	# """, as_dict=True)
	# checkin = frappe.db.sql("""
	#     update `tabAttendance`
	#     set overtime_hours =" "
	#     where attendance_date between "2024-04-30" and "2024-04-30"
	# """, as_dict=True)
	# checkin = frappe.db.sql("""
	#     update `tabAttendance`
	#     set overtime_hours =" "
	#     where attendance_date between "2024-04-30" and "2024-04-30"
	# """, as_dict=True)
	checkin = frappe.db.sql("""
		update `tabAttendance`
		set docstatus=0
		where attendance_date between "2024-04-30" and "2024-04-30"
	""", as_dict=True)
	checkin = frappe.db.sql("""update `tabEmployee Checkin` set attendance = '' where date(time) between "2024-04-30" and "2024-04-30" """,as_dict = True)
	checkin = frappe.db.sql("""update `tabEmployee Checkin` set skip_auto_attendance = 0 where date(time) between "2024-04-30" and "2024-04-30"  """,as_dict = True)

@frappe.whitelist()
def emp_type_order(doc,method):
	# frappe.errprint("HelloWorld")
	if doc.employee_type=="Staff":
		doc.employee_type_order='1'
	elif doc.employee_type=="Worker":
		doc.employee_type_order='2'
	elif doc.employee_type=="D . Trainee":
		doc.employee_type_order='3'
	elif doc.employee_type=="NAPS":
		doc.employee_type_order='4'
	elif doc.employee_type=="Contract Employee":
		doc.employee_type_order='5'
	else:
		doc.employee_type_order='6'


@frappe.whitelist()
def update_employee_no(name,employee_number):
	frappe.db.set_value("Employee",name,'employee_number',employee_number)
	frappe.rename_doc('Employee',name ,employee_number)
	return employee_number



import frappe
from datetime import date

@frappe.whitelist()
def dob_to_age():
	employees = frappe.get_all("Employee", filters={"status": "Active"}, fields=["name", "date_of_birth", "age"])

	for e in employees:
		dob = e.date_of_birth
		
		if not dob:
			frappe.log_error(f"Missing date_of_birth for Employee {e.name}")
			continue
		today = date.today()
		age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
		
		frappe.db.set_value("Employee", e.name, "age", age)
	frappe.db.commit()

	return f"Updated ages for {len(employees)} employees"


def create_overtime_requests():
	start_date = '2024-07-01'
	end_date = '2024-08-20'
	current_date = start_date
	while current_date <= end_date:
		attendance_records = frappe.get_all(
			"Attendance",
			filters={'docstatus': 1, 'attendance_date': current_date, 'employee_type': 'Worker'},
			fields=["employee", "attendance_date", "overtime_hours","total_working_hours","shift","in_time","out_time"]
		)
		for record in attendance_records:
			if record['overtime_hours'] > 0:
				in_time = record['in_time']
				out_time = record['out_time']
				ot = frappe.new_doc('Overtime Request')
				ot.employee = record['employee']
				ot.ot_date = record['attendance_date']
				ot.shift = record['shift']
				ot.from_time = in_time.strftime('%H:%M:%S')  
				ot.to_time = out_time.strftime('%H:%M:%S')
				ot.total_hour = record['total_working_hours']
				ot.total_hours = record['overtime_hours']
				ot.insert()
				ot.save(ignore_permissions=True)
				frappe.db.commit()
		current_date = add_days(current_date , 1)

@frappe.whitelist()
def ot_request_creation(doc,method):
	if doc.employee_type=='Worker' and doc.overtime_hours > 0:
		in_datetime = datetime.strptime(doc.in_time, '%Y-%m-%d %H:%M:%S')
		out_datetime = datetime.strptime(doc.out_time, '%Y-%m-%d %H:%M:%S')
		# ot_in = in_time.strftime('%H:%M:%S') 
		# ot_out = out_time.strftime('%H:%M:%S')
		ot = frappe.new_doc('Overtime Request')
		ot.employee = doc.employee
		ot.ot_date = doc.attendance_date
		ot.total_hour = doc.total_working_hours
		ot.shift = doc.shift
		ot.from_time = in_datetime.strftime('%H:%M:%S')  
		ot.to_time = out_datetime.strftime('%H:%M:%S')
		ot.total_hours = doc.overtime_hours
		ot.insert()
		ot.save(ignore_permissions=True)
		frappe.db.commit()





@frappe.whitelist()
def gross_change():
	emp='20121101'
	frappe.db.sql("""update `tabEmployee` set actual_gross=gross_pay where name="%s" """,(emp))

@frappe.whitelist()
def get_special_all():
	attendance=frappe.get_all("Attendance",{'employee_type':'Staff','working_hours':('>=',23),'attendance_date':('between',('2024-07-01','2024-07-31'))},['*'])
	i=0
	for att in attendance:
		day_of_week = att.attendance_date.weekday()
		if day_of_week in [0,1,2,3,4]:
			print(1000)
		elif day_of_week ==5:
			print(3500)
		elif day_of_week ==6:
			print(2500)
		print(att.attendance_date)
		i+=1
	print(i)

