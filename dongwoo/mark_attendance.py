import frappe
from frappe.utils import time_diff_in_hours 
from datetime import datetime
from frappe.utils.data import today, add_days, add_years
from dateutil.relativedelta import relativedelta
from datetime import timedelta, time,date
from frappe.utils import time_diff_in_hours, formatdate, get_first_day,get_last_day, nowdate, now_datetime
from frappe.utils import (getdate, cint, add_months, date_diff, add_days,
    nowdate, get_datetime_str, cstr, get_datetime, now_datetime, format_datetime)
from frappe.utils.data import ceil, get_time, get_year_start
import datetime as dt
from datetime import datetime, timedelta

def get_dates(from_date,to_date):
    no_of_days = date_diff(add_days(to_date, 1), from_date)
    dates = [add_days(from_date, i) for i in range(0, no_of_days)]
    return dates


@frappe.whitelist()
def mark_att_specific():
    from_date = "2024-08-14"
    to_date = "2024-08-29"
    checkins = frappe.db.sql("""select * from `tabEmployee Checkin` where date(time) between '%s' and '%s' order by time ASC """%(from_date,to_date),as_dict=1)
    for c in checkins:
        employee = frappe.db.exists('Employee',{'status':'Active','date_of_joining':['<=',from_date],'name':c.employee})
        if employee:  
            # print(c.log_type)
            mark_attendance_from_checkin(c.employee,c.time,c.log_type)
    mark_absent(from_date,to_date)
    mark_wh_ot(from_date,to_date)   
    get_assigned_shift(from_date, to_date)
    update_workspot(from_date,to_date)
    mark_att_present(from_date, to_date)
    mark_late_early(from_date,to_date)
    return "ok"     	

@frappe.whitelist()
def mark_att():
    # from_date='2024-07-03'
    # to_date ='2024-07-21'
    from_date = add_days(today(),-1)
    to_date = today()
    checkins = frappe.db.sql("""
    select * 
    from `tabEmployee Checkin` 
    where date(time) between '%s' and '%s' 
        
    order by time ASC 
""" % (from_date, to_date), as_dict=1)

    # checkins = frappe.db.sql("""select * from `tabEmployee Checkin` where employee='20110602' and date(time) between '%s' and '%s' and skip_auto_attendance = '0' order by skip_auto_attendance, time ASC """%(from_date,to_date),as_dict=1)
    for c in checkins:
        employee = frappe.db.exists('Employee',{'status':'Active','date_of_joining':['<=',from_date],'name':c.employee})
        if employee:  
            mark_attendance_from_checkin(c.employee,c.time,c.log_type)
    mark_absent(from_date,to_date)
    mark_wh_ot(from_date,to_date)   
    get_assigned_shift(from_date, to_date)
    update_workspot(from_date,to_date)
    mark_att_present(from_date, to_date)
    mark_late_early(from_date,to_date)
    return "ok"     	        

def mark_attendance_from_checkin(employee,time,log_type):
    if log_type == 'IN':
        att_time = time.time()
        shift = ''
        att_date = time.date()
        max_in = datetime.strptime('05:30','%H:%M').time()
        before_in = frappe.db.sql("""select * from `tabEmployee Checkin` where employee = '%s' and log_type = 'IN' and date(time) = '%s' and TIME(time) < '%s' order by time ASC """%(employee,att_date,max_in),as_dict=True)
        after_in = frappe.db.sql("""select * from `tabEmployee Checkin` where employee = '%s' and log_type = 'IN' and date(time) = '%s' and TIME(time) > '%s' order by time ASC """%(employee,att_date,max_in),as_dict=True)
        if before_in and not after_in:
            att_date = add_days(att_date,-1)
            att = frappe.db.exists('Attendance',{"employee":employee,'attendance_date':att_date,'docstatus':['!=','2']})   
            if not att:
                att = frappe.new_doc("Attendance")
                att.employee = employee
                att.attendance_date = att_date
                att.shift = get_actual_shift_start(get_time(before_in[0].time))
                att.status = 'Absent'
                att.in_time = before_in[0].time
                att.total_working_hours = "00:00:00"
                att.working_hours = "0.0"
                att.extra_hours = "0.0"
                att.total_extra_hours = "00:00:00"
                att.total_overtime_hours = "00:00:00"
                att.overtime_hours = "0.0"
                att.late_entry_time = "00:00:00"
                att.early_out_time = "00:00:00"
                att.save(ignore_permissions=True)
                frappe.db.commit()
                for c in before_in:
                    frappe.db.set_value('Employee Checkin', c.name, 'skip_auto_attendance', 1)
                    frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
                return att  
            else:
                att = frappe.get_doc("Attendance",att)
                if att.docstatus == 0 or att.docstatus == 1:
                    if att.status != 'Present':  
                        att.employee = employee
                        att.attendance_date = att_date
                        att.shift = shift
                        att.status = 'Absent'
                        att.in_time =before_in[0]['time']
                        att.shift = get_actual_shift_start(get_time(before_in[0]['time']))
                        att.total_working_hours = "00:00:00"
                        att.working_hours = "0.0"
                        att.extra_hours = "0.0"
                        att.total_extra_hours = "00:00:00"
                        att.total_overtime_hours = "00:00:00"
                        att.overtime_hours = "0.0"
                        att.late_entry_time = "00:00:00"
                        att.early_out_time = "00:00:00"
                        att.save(ignore_permissions=True)
                        frappe.db.commit()
                        for c in before_in:
                            frappe.db.set_value('Employee Checkin', c.name, 'skip_auto_attendance', 1)
                            frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
                        return att 
        if after_in and not before_in:
            att = frappe.db.exists('Attendance',{"employee":employee,'attendance_date':att_date,'docstatus':['!=','2']})   
            if not att:
                att = frappe.new_doc("Attendance")
                att.employee = employee
                att.attendance_date = att_date
                att.shift = get_actual_shift_start(get_time(after_in[0].time))
                att.status = 'Absent'
                att.in_time = after_in[0].time
                att.total_working_hours = "00:00:00"
                att.working_hours = "0.0"
                att.extra_hours = "0.0"
                att.total_extra_hours = "00:00:00"
                att.total_overtime_hours = "00:00:00"
                att.overtime_hours = "0.0"
                att.late_entry_time = "00:00:00"
                att.early_out_time = "00:00:00"
                att.save(ignore_permissions=True)
                frappe.db.commit()
                for c in after_in:
                    frappe.db.set_value('Employee Checkin', c.name, 'skip_auto_attendance', 1)
                    frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
                return att  
            else:
                att = frappe.get_doc("Attendance",att)
                if att.docstatus == 0 or att.docstatus == 1:
                    if att.status != 'Present':
                        att.employee = employee
                        att.attendance_date = att_date
                        att.shift = shift
                        att.status = 'Absent'
                        att.in_time =after_in[0]['time']
                        att.shift = get_actual_shift_start(get_time(after_in[0]['time']))
                        att.total_working_hours = "00:00:00"
                        att.working_hours = "0.0"
                        att.extra_hours = "0.0"
                        att.total_extra_hours = "00:00:00"
                        att.total_overtime_hours = "00:00:00"
                        att.overtime_hours = "0.0"
                        att.late_entry_time = "00:00:00"
                        att.early_out_time = "00:00:00"
                        att.save(ignore_permissions=True)
                        frappe.db.commit()
                        for c in after_in:
                            frappe.db.set_value('Employee Checkin', c.name, 'skip_auto_attendance', 1)
                            frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
                        return att
        if after_in and before_in:
            print('Both passed')
            if before_in:
                print('pass1')
                prev_date = add_days(att_date,-1)
                prev_att = frappe.db.exists('Attendance',{"employee":employee,'attendance_date':prev_date,'docstatus':['!=','2']})   
                if not prev_att:
                    prev_att = frappe.new_doc("Attendance")
                    prev_att.employee = employee
                    prev_att.attendance_date = prev_date
                    prev_att.shift = get_actual_shift_start(get_time(before_in[0].time))
                    prev_att.status = 'Absent'
                    prev_att.in_time = before_in[0].time
                    prev_att.total_working_hours = "00:00:00"
                    prev_att.working_hours = "0.0"
                    prev_att.extra_hours = "0.0"
                    prev_att.total_extra_hours = "00:00:00"
                    prev_att.total_overtime_hours = "00:00:00"
                    prev_att.overtime_hours = "0.0"
                    prev_att.late_entry_time = "00:00:00"
                    prev_att.early_out_time = "00:00:00"
                    prev_att.save(ignore_permissions=True)
                    frappe.db.commit()
                    for c in before_in:
                        frappe.db.set_value('Employee Checkin', c.name, 'skip_auto_attendance', 1)
                        frappe.db.set_value("Employee Checkin",c.name, "attendance", prev_att.name)
                    return prev_att  
                else:
                    print('passs2')
                    prev_att = frappe.get_doc("Attendance",prev_att)
                    if prev_att.docstatus == 0 or prev_att.docstatus == 1:
                        if prev_att.status != 'Present':
                            prev_att.employee = employee
                            prev_att.attendance_date = prev_date
                            prev_att.shift = shift
                            prev_att.status = 'Absent'
                            prev_att.in_time =before_in[0]['time']
                            prev_att.shift = get_actual_shift_start(get_time(before_in[0]['time']))
                            prev_att.total_working_hours = "00:00:00"
                            prev_att.working_hours = "0.0"
                            prev_att.extra_hours = "0.0"
                            prev_att.total_extra_hours = "00:00:00"
                            prev_att.total_overtime_hours = "00:00:00"
                            prev_att.overtime_hours = "0.0"
                            prev_att.late_entry_time = "00:00:00"
                            prev_att.early_out_time = "00:00:00"
                            prev_att.save(ignore_permissions=True)
                            frappe.db.commit()
                            for c in before_in:
                                frappe.db.set_value('Employee Checkin', c.name, 'skip_auto_attendance', 1)
                                frappe.db.set_value("Employee Checkin",c.name, "attendance", prev_att.name)
                            # return prev_att
            
            att = frappe.db.exists('Attendance',{"employee":employee,'attendance_date':att_date,'docstatus':['!=','2']})   
            if not att:
                print('attnot')
                att = frappe.new_doc("Attendance")
                att.employee = employee
                att.attendance_date = att_date
                att.shift = get_actual_shift_start(get_time(after_in[0].time))
                att.status = 'Absent'
                att.in_time = after_in[0].time
                att.total_working_hours = "00:00:00"
                att.working_hours = "0.0"
                att.extra_hours = "0.0"
                att.total_extra_hours = "00:00:00"
                att.total_overtime_hours = "00:00:00"
                att.overtime_hours = "0.0"
                att.late_entry_time = "00:00:00"
                att.early_out_time = "00:00:00"
                att.save(ignore_permissions=True)
                frappe.db.commit()
                for c in after_in:
                    frappe.db.set_value('Employee Checkin', c.name, 'skip_auto_attendance', 1)
                    frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
                return att  
            else:
                print('presentatt')
                att = frappe.get_doc("Attendance",att)
                if att.docstatus == 0 or att.docstatus == 1:
                    if att.status != 'Present':
                        att.employee = employee
                        att.attendance_date = att_date
                        att.shift = shift
                        att.status = 'Absent'
                        att.in_time =after_in[0].time
                        print(after_in[0].time)
                        print(att.in_time)
                        att.shift = get_actual_shift_start(get_time(after_in[0].time))
                        att.total_working_hours = "00:00:00"
                        att.working_hours = "0.0"
                        att.extra_hours = "0.0"
                        att.total_extra_hours = "00:00:00"
                        att.total_overtime_hours = "00:00:00"
                        att.overtime_hours = "0.0"
                        att.late_entry_time = "00:00:00"
                        att.early_out_time = "00:00:00"
                        att.save(ignore_permissions=True)
                        frappe.db.commit()
                        for c in after_in:
                            frappe.db.set_value('Employee Checkin', c.name, 'skip_auto_attendance', 1)
                            frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
                        return att
    if log_type == 'OUT':
        shift = ''
        att_date = time.date()
        att_time = time.time()
        max_out = datetime.strptime('10:30','%H:%M').time()
        if att_time < max_out:
            yesterday = add_days(att_date,-1)
            checkins = frappe.db.sql("""select * from `tabEmployee Checkin` where employee = '%s' and log_type = 'OUT' and date(time) = '%s' and TIME(time) < '%s' order by time ASC """%(employee,att_date,max_out),as_dict=True)
            att = frappe.db.exists("Attendance",{'employee':employee,'attendance_date':yesterday})
            if att:
                att = frappe.get_doc("Attendance",att)
                if att.docstatus != 2:
                    if att.status != 'Present':    
                        if att.out_time is None:
                            if att.shift is None:
                                if len(checkins) > 0:
                                    att.shift = get_actual_shift(get_time(checkins[-1].time))
                                    att.out_time = checkins[-1].time
                                    for c in checkins:
                                        print(c.name)
                                        frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance',1)
                                        frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
                                else:
                                    att.shift = get_actual_shift(get_time(checkins[0].time))
                                    att.out_time = checkins[0].time
                                    frappe.db.set_value('Employee Checkin',checkins[0].name,'skip_auto_attendance',1)
                                    frappe.db.set_value("Employee Checkin",checkins[0].name, "attendance", att.name)
                            else:
                                if len(checkins) > 0:
                                    att.out_time = checkins[-1].time
                                    for c in checkins:
                                        frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance',1)
                                        frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
                                else:
                                    att.out_time = checkins[0].time
                                    frappe.db.set_value('Employee Checkin',checkins[0].name,'skip_auto_attendance',1)
                                    frappe.db.set_value("Employee Checkin",checkins[0].name, "attendance", att.name)
                            # att.status = 'Absent'    
                            att.save(ignore_permissions=True)
                            frappe.db.commit()
                            return att
                        else:
                            print('Outtime not present')
                            if att.shift is None:
                                if len(checkins) > 0:
                                    print("More")
                                    print(att.name)
                                    att.shift = get_actual_shift(get_time(checkins[-1].time))
                                    att.out_time = checkins[-1].time
                                    for c in checkins:
                                        print(c.name)
                                        frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance',1)
                                        frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
                                else:
                                    print("less")
                                    print(att.name)
                                    att.shift = get_actual_shift(get_time(checkins[0].time))
                                    att.out_time = checkins[0].time
                                    frappe.db.set_value('Employee Checkin',checkins[0].name,'skip_auto_attendance',1)
                                    frappe.db.set_value("Employee Checkin",checkins[0].name, "attendance", att.name)
                            else:
                                if len(checkins) > 0:
                                    att.out_time = checkins[-1].time
                                    att.shift = get_actual_shift(get_time(checkins[-1].time))
                                    print(att.out_time)
                                    for c in checkins:
                                        frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance',1)
                                        frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
                                else:
                                    att.out_time = checkins[0].time
                                    att.shift = get_actual_shift(get_time(checkins[0].time))
                                    print(att.out_time)
                                    frappe.db.set_value('Employee Checkin',checkins[0].name,'skip_auto_attendance',1)
                                    frappe.db.set_value("Employee Checkin",checkins[0].name, "attendance", att.name)
                            # att.status = 'Absent'    
                            att.save(ignore_permissions=True)
                            frappe.db.commit()
                            return att
            else:
                att = frappe.new_doc("Attendance")
                att.employee = employee
                att.attendance_date = yesterday
                att.status = 'Absent'
                if len(checkins) > 0:
                    att.out_time = checkins[-1].time
                    att.shift = get_actual_shift(get_time(checkins[-1].time))
                    for c in checkins:
                        frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance',1)
                        frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
                else:
                    att.out_time = checkins[0].time
                    att.shift = get_actual_shift(get_time(checkins[0].time))
                    frappe.db.set_value('Employee Checkin',checkins[0].name,'skip_auto_attendance',1)
                    frappe.db.set_value("Employee Checkin",checkins[0].name, "attendance", att.name)
                att.total_working_hours = "00:00:00"
                att.working_hours = "0.0"
                att.extra_hours = "0.0"
                att.total_extra_hours = "00:00:00"
                att.total_overtime_hours = "00:00:00"
                att.overtime_hours = "0.0"
                att.late_entry_time = "00:00:00"
                att.early_out_time = "00:00:00"
                att.save(ignore_permissions=True)
                frappe.db.commit()
                for c in checkins:
                    frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance',1)
                    frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
                return att	
        else:
            checkins = frappe.db.sql("""select * from `tabEmployee Checkin` where employee ='%s' and log_type = 'OUT' and date(time) = '%s' and TIME(time) > '%s' order by time ASC"""%(employee,att_date,max_out),as_dict=True)
            att = frappe.db.exists("Attendance",{'employee':employee,'attendance_date':att_date})
            if att:
                 
                att = frappe.get_doc("Attendance",att)
                if att.docstatus != 2:
                    if att.status != 'Present': 
                        if not att.out_time:
                            if att.shift == '':
                                if len(checkins) > 0:
                                    att.shift = get_actual_shift(get_time(checkins[-1].time))
                                    att.out_time = checkins[-1].time
                                    for c in checkins:
                                        frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance',1)
                                        frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
                                else:
                                    att.shift = get_actual_shift(get_time(checkins[0].time))
                                    att.out_time = checkins[0].time
                                    frappe.db.set_value('Employee Checkin',checkins[0].name,'skip_auto_attendance',1)
                                    frappe.db.set_value("Employee Checkin",checkins[0].name, "attendance", att.name)
                            else:
                                if len(checkins) > 0:
                                    att.out_time = checkins[-1].time
                                    for c in checkins:
                                        frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance',1)
                                        frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
                                else:
                                    att.out_time = checkins[0].time
                                    frappe.db.set_value('Employee Checkin',checkins[0].name,'skip_auto_attendance',1)
                                    frappe.db.set_value("Employee Checkin",checkins[0].name, "attendance", att.name)
                            att.status = 'Absent'    
                            att.save(ignore_permissions=True)
                            frappe.db.commit()
                            return att
                        else:
                            return att
            else:
                att = frappe.new_doc("Attendance")
                att.employee = employee
                att.attendance_date = att_date
                att.shift = shift
                att.status = 'Absent'
                if len(checkins) > 0:
                    att.shift = get_actual_shift(get_time(checkins[-1].time))
                    att.out_time = checkins[-1].time
                else:
                    att.shift = get_actual_shift(get_time(checkins[0].time))
                    att.out_time = checkins[0].time
                att.total_working_hours = "00:00:00"
                att.working_hours = "0.0"
                att.extra_hours = "0.0"
                att.total_extra_hours = "00:00:00"
                att.total_overtime_hours = "00:00:00"
                att.overtime_hours = "0.0"
                att.late_entry_time = "00:00:00"
                att.early_out_time = "00:00:00"
                att.save(ignore_permissions=True)
                frappe.db.commit()
                for c in checkins:
                    frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance',1)
                    frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
                return att 


def is_between(time, time_range):
    if time_range[1] < time_range[0]:
        return time >= time_range[0] or time <= time_range[1]
    return time_range[0] <= time <= time_range[1]

def get_actual_shift_start(get_shift_time):
    from datetime import datetime
    from datetime import date, timedelta,time
    shift1 = frappe.db.get_value('Shift Type',{'name':'A'},['checkin_start_time','checkin_end_time'])
    shift2 = frappe.db.get_value('Shift Type',{'name':'B'},['checkin_start_time','checkin_end_time'])
    shift3 = frappe.db.get_value('Shift Type',{'name':'C'},['checkin_start_time','checkin_end_time'])
    att_time_seconds = get_shift_time.hour * 3600 + get_shift_time.minute * 60 + get_shift_time.second
    shift = ''
    if shift1[0].total_seconds() < att_time_seconds < shift1[1].total_seconds():
        shift = 'A'
    if shift2[0].total_seconds() < att_time_seconds < shift2[1].total_seconds():
        shift = 'B'
    if shift3[0].total_seconds() < att_time_seconds < shift3[1].total_seconds():
        shift = 'C'
    return shift

def get_actual_shift(get_shift_time):
    from datetime import datetime
    from datetime import date, timedelta,time
    shift1 = frappe.db.get_value('Shift Type',{'name':'A'},['checkout_start_time','checkout_end_time'])
    shift2 = frappe.db.get_value('Shift Type',{'name':'B'},['checkout_start_time','checkout_end_time'])
    shift3 = frappe.db.get_value('Shift Type',{'name':'C'},['checkout_start_time','checkout_end_time'])
    att_time_seconds = get_shift_time.hour * 3600 + get_shift_time.minute * 60 + get_shift_time.second
    shift = ''
    if shift1[0].total_seconds() < att_time_seconds < shift1[1].total_seconds():
        shift = 'A'
    if shift2[0].total_seconds() < att_time_seconds < shift2[1].total_seconds():
        shift = 'B'
    if shift3[0].total_seconds() < att_time_seconds < shift3[1].total_seconds():
        shift = 'C'
    return shift

@frappe.whitelist()
def mark_absent(from_date,to_date):
        dates = get_dates(from_date,to_date)
        for date in dates:
            employee = frappe.db.get_all('Employee',{'status':'Active','date_of_joining':['<=',from_date]})
            for emp in employee:
                hh = check_holiday(date,emp.name)
                if not hh:
                    if not frappe.db.exists('Attendance',{'attendance_date':date,'employee':emp.name,'docstatus':('!=','2')}):
                        att = frappe.new_doc("Attendance")
                        att.employee = emp.name
                        att.status = 'Absent'
                        att.attendance_date = date
                        att.total_working_hours = "00:00:00"
                        att.working_hours = "0.0"
                        att.extra_hours = "0.0"
                        att.total_extra_hours = "00:00:00"
                        att.total_overtime_hours = "00:00:00"
                        att.overtime_hours = "0.0"
                        att.late_entry_time = "00:00:00"
                        att.early_out_time = "00:00:00"
                        att.save(ignore_permissions=True)
                        frappe.db.commit()  

def check_holiday(date,emp):
    holiday_list = frappe.db.get_value('Employee',{'name':emp},'holiday_list')
    holiday = frappe.db.sql("""select `tabHoliday`.holiday_date,`tabHoliday`.weekly_off from `tabHoliday List`
    left join `tabHoliday` on `tabHoliday`.parent = `tabHoliday List`.name where `tabHoliday List`.name = '%s' and holiday_date = '%s' """%(holiday_list,date),as_dict=True)
    doj= frappe.db.get_value("Employee",{'name':emp},"date_of_joining")
    status = ''
    if frappe.db.exists('Shift Assignment',{'start_date':date,'employee':emp,'shift_type':'WW','docstatus':1}):
        return "WW"
    elif holiday :
        if doj < holiday[0].holiday_date:
            if holiday[0].weekly_off == 1:
                return "WW"     
            else:
                return "HH"
def mark_wh_ot(from_date, to_date):
# @frappe.whitelist()
# def mark_wh_ot():
#     from_date='2024-08-20'
#     to_date='2024-08-20'
    attendance = frappe.db.get_all('Attendance', {'attendance_date': ('between', (from_date,to_date)),'docstatus': ('!=', '2')}, ['*'])
    for att in attendance:
        if att.shift and att.in_time and att.out_time:
            in_time = att.in_time
            out_time = att.out_time
            if att.on_duty_application != "":
                if att.in_time and att.out_time:
                    in_time = att.in_time
                    out_time = att.out_time
            else:
                if att.session_from_time and att.session_to_time: 
                    in_time = att.session_from_time
                    out_time = att.session_to_time
            frappe.errprint(att.name)
            att_wh = time_diff_in_hours(out_time, in_time)
            tot_wh=0
            if att.att_permission is not None:
                att_hours=frappe.db.get_value("Permission",{'name':att.att_permission},['total_time'])
                if att_hours is not None:   
                    perm_time=int(att_hours)
                    if perm_time > 0:
                        # print(type(att.permission_hour))
                        wh = round(att_wh, 2) + perm_time
            else:
                # print(type(wh))
                wh = round(att_wh, 2)
            # wh=round(att_wh, 2)
            time_in_standard_format = "{:02d}:{:02d}:{:02d}".format(int(wh), int((wh * 60) % 60), int((wh * 3600) % 60))
            if wh < 24.0:
                twh = time_in_standard_format
                frappe.db.set_value('Attendance', att.name, 'total_working_hours', twh)
                frappe.db.set_value('Attendance', att.name, 'working_hours', wh)
            else:
                twh = "23:59:59"
                frappe.db.set_value('Attendance', att.name, 'total_working_hours', twh)
                frappe.db.set_value('Attendance', att.name, 'working_hours', wh)
            if wh < 4:
                frappe.db.set_value("Attendance", att.name, "status", "Absent")
            elif 4 <= wh < 8:
                if att.shift == "C" and 7 <= wh <= 8:
                    frappe.db.set_value("Attendance", att.name, "status", "Present")
                else:
                    frappe.db.set_value("Attendance", att.name, "status", "Half Day")
                day_of_week = att.attendance_date.strftime("%A")
                if day_of_week == "Saturday" and att.employee_type == "Staff":
                    frappe.db.set_value("Attendance", att.name, "status", "Present")
            else:
                frappe.db.set_value("Attendance", att.name, "status", "Present")
            hh = check_holiday(att.attendance_date,att.employee)
            if not hh:
                if att.actual_shift is not None and att.actual_shift == 'WW':
                    hours, minutes, seconds = map(int, twh.split(":"))
                    twh_1 = timedelta(hours=hours, minutes=minutes, seconds=seconds)
                    time_diff = twh_1
                    ot_hours = None
                    if time_diff.seconds >= 3600:
                        if time_diff.seconds % 3600 <= 1800:
                            ot_hours = time(time_diff.seconds // 3600, 0, 0)
                        else:
                            ot_hours = time(time_diff.seconds // 3600, 30, 0)
                    if ot_hours is not None:
                        ot_hr = round((ot_hours.hour + ot_hours.minute / 60), 1)
                    else:                   
                        ot_hr = 0
                    frappe.db.set_value('Attendance', att.name, 'extra_hours', wh)
                    frappe.db.set_value('Attendance', att.name, 'total_extra_hours', twh)
                    frappe.db.set_value('Attendance', att.name, 'total_overtime_hours', ot_hours)
                    frappe.db.set_value('Attendance', att.name, 'overtime_hours', ot_hr)
                else:
                    day_of_week = att.attendance_date.strftime("%A")
                    shift_time = time(0, 0, 0)
                    if day_of_week == "Saturday" and att.employee_type == "Staff":
                        shift_time = frappe.get_value("Shift Type", {'name': att.shift}, ["ot_time"])
                    else:
                        shift_time = frappe.get_value("Shift Type", {'name': att.shift}, ["end_time"])
                    shift_end_time = dt.datetime.strptime(str(shift_time), '%H:%M:%S').time()
                    shift_date = None
                    if att.shift in ["C","B"] :
                        shift_date = add_days(att.attendance_date,+1)
                        
                    else:
                        shift_date = att.attendance_date
                    ot_date_str = datetime.strptime(str(shift_date),'%Y-%m-%d').date()
                    end_time = datetime.combine(ot_date_str, shift_end_time)
                    end_time = frappe.utils.get_datetime(end_time)
                    out_time = frappe.utils.get_datetime(att.out_time)
                    if out_time > end_time:
                        extra_hours = time_diff_in_hours(out_time, end_time)
                        total_extra_hours = out_time - end_time
                        ot_hours = time(0, 0, 0)
                        time_diff = out_time - end_time
                        ot_hours = None
                        if time_diff.seconds >= 3600:
                            if time_diff.seconds % 3600 <= 1800:
                                ot_hours = time(time_diff.seconds // 3600, 0, 0)
                            else:
                                ot_hours = time(time_diff.seconds // 3600, 30, 0)
                        if ot_hours is not None:
                            ot_hr = round((ot_hours.hour + ot_hours.minute / 60), 1)
                        else:
                            ot_hr = 0
                        
                    else:
                        extra_hours = 0.0
                        total_extra_hours = "00:00:00"
                        ot_hours = "00:00:00"
                        ot_hr = 0.0			
                    frappe.db.set_value('Attendance', att.name, 'extra_hours', round(extra_hours, 2))
                    frappe.db.set_value('Attendance', att.name, 'total_extra_hours', total_extra_hours)
                    frappe.db.set_value('Attendance', att.name, 'total_overtime_hours', ot_hours)
                    frappe.db.set_value('Attendance', att.name, 'overtime_hours', ot_hr)
            else:
                hours, minutes, seconds = map(int, twh.split(":"))
                twh_1 = timedelta(hours=hours, minutes=minutes, seconds=seconds)
                time_diff = twh_1
                ot_hours = None
                if time_diff.seconds >= 3600:
                    if time_diff.seconds % 3600 <= 1800:
                        ot_hours = time(time_diff.seconds // 3600, 0, 0)
                    else:
                        ot_hours = time(time_diff.seconds // 3600, 30, 0)
                if ot_hours is not None:
                    ot_hr = round((ot_hours.hour + ot_hours.minute / 60), 1)
                else:                   
                    ot_hr = 0
                frappe.db.set_value('Attendance', att.name, 'extra_hours', wh)
                frappe.db.set_value('Attendance', att.name, 'total_extra_hours', twh)
                frappe.db.set_value('Attendance', att.name, 'total_overtime_hours', ot_hours)
                frappe.db.set_value('Attendance', att.name, 'overtime_hours', ot_hr)
            if in_time > out_time:
                frappe.db.set_value('Attendance', att.name, 'total_working_hours', 0)
                frappe.db.set_value('Attendance', att.name, 'working_hours', 0)
                frappe.db.set_value('Attendance', att.name, 'status', 'Absent')
                frappe.db.set_value('Attendance', att.name, 'extra_hours',0)
                frappe.db.set_value('Attendance', att.name, 'total_extra_hours', 0)
                frappe.db.set_value('Attendance', att.name, 'total_overtime_hours', 0)
                frappe.db.set_value('Attendance', att.name, 'overtime_hours', 0)
        else:
            frappe.db.set_value('Attendance', att.name, 'total_working_hours', "00:00:00")
            frappe.db.set_value('Attendance', att.name, 'working_hours', "0.0")
            frappe.db.set_value('Attendance', att.name, 'extra_hours', "0.0")
            frappe.db.set_value('Attendance', att.name, 'total_extra_hours', "00:00:00")
            frappe.db.set_value('Attendance', att.name, 'total_overtime_hours', "00:00:00")
            frappe.db.set_value('Attendance', att.name, 'overtime_hours', "0.0")
            frappe.db.set_value('Attendance', att.name, 'late_entry_time', "00:00:00")
            frappe.db.set_value('Attendance', att.name, 'early_out_time',"00:00:00")
        

@frappe.whitelist()
def submit_att(from_date,to_date,employee_type,department):
    if department == "All Departments":
        att = frappe.db.sql("""select * from tabAttendance where attendance_date between '%s' and '%s' and docstatus = 0 and employee_type = '%s' """%(from_date,to_date,employee_type),as_dict=True)
    elif department != "All Departments":
        att = frappe.db.sql("""select * from tabAttendance where attendance_date between '%s' and '%s' and docstatus = 0 and employee_type = '%s' and department = '%s' """%(from_date,to_date,employee_type,department),as_dict=True)
    for a in att:
        od = frappe.get_doc("Attendance",{'name':a.name})
        od.submit()
        frappe.db.commit()
    return "ok"

@frappe.whitelist()
def submit_att_with_employee(from_date,to_date,employee):
    att = frappe.db.sql("""select * from tabAttendance where attendance_date between '%s' and '%s' and docstatus = 0 and employee = '%s' """%(from_date,to_date,employee),as_dict=True)
    for a in att:
        od = frappe.get_doc("Attendance",{'name':a.name})
        od.save(ignore_permissions=True)
        od.submit()
        frappe.db.commit()
    return "ok"

@frappe.whitelist()
def update_workspot(from_date,to_date):
    attendance = frappe.db.sql("""select * from tabAttendance where attendance_date between '%s' and '%s' """%(from_date,to_date),as_dict=True)
    for att in attendance:
        if att.employee_type=="Worker" or att.employee_type=='Trainee':
            workspot=frappe.db.get_value("Employee",{"employee_number":att.employee},['workspot']) or ''
            if workspot:
                frappe.db.set_value("Attendance",att.name,'workspot',workspot)
        elif att=='Contract Employee':
            workspot=frappe.db.get_value("Workspot for CL",{"employee":att.employee,"date":att.attendance_date},['workspot']) or ''
            if workspot:
                frappe.db.set_value("Attendance",att.name,'workspot',workspot)

@frappe.whitelist()
def mark_att_present(from_date, to_date):
    attendance = frappe.db.get_all('Attendance', {'attendance_date': ('between', (from_date, to_date)),'docstatus': 0}, ['*'])
    for att in attendance:
        if att.status == 'Present':
            frappe.db.set_value('Attendance', att.name, 'docstatus', 1)


@frappe.whitelist()
def mark_late_early(from_date, to_date):
    attendance = frappe.db.get_all('Attendance', {'attendance_date': ('between', (from_date, to_date))}, ['*'])
    for att in attendance:
        late_entry_value=0
        late_entry_diff=None
        if att.in_time:
            if att.shift in ['A','B']:
                # print("A,B")
                shift_time = frappe.get_value("Shift Type", {'name': att.shift}, ["start_time"])
                shift_start_time = datetime.strptime(str(shift_time), '%H:%M:%S').time()
                start_time = dt.datetime.combine(att.attendance_date,shift_start_time)
                
                if att.in_time > datetime.combine(att.attendance_date, shift_start_time):
                    # frappe.db.set_value('Attendance', att.name, 'late_entry', 1)
                    # frappe.db.set_value('Attendance', att.name, 'late_entry_time', att.in_time - start_time)
                    late_entry_value=1
                    late_entry_diff= att.in_time -start_time
                else:
                    # frappe.db.set_value('Attendance', att.name, 'late_entry', 0)
                    # frappe.db.set_value('Attendance', att.name, 'late_entry_time', None)
                    late_entry_value=0
                    late_entry_diff=None
            if att.shift in ['C']:
                # print("C")
                shift_time = frappe.get_value("Shift Type", {'name': att.shift}, ["start_time"])
                shift_start_time = datetime.strptime(str(shift_time), '%H:%M:%S').time()
                start_time = datetime.combine(add_days(att.attendance_date, 1), shift_start_time)
                if att.in_time > datetime.combine(add_days(att.attendance_date,1), shift_start_time):
                    # frappe.db.set_value('Attendance', att.name, 'late_entry', 1)
                    # frappe.db.set_value('Attendance', att.name, 'late_entry_time', att.in_time - start_time)
                    late_entry_value=1
                    late_entry_diff= att.in_time - start_time
                else:
                    # frappe.db.set_value('Attendance', att.name, 'late_entry', 0)
                    # frappe.db.set_value('Attendance', att.name, 'late_entry_time', None)
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
                    # frappe.db.set_value('Attendance', att.name, 'early_exit', 1)
                    # frappe.db.set_value('Attendance', att.name, 'early_out_time', end_time - att.out_time )
                    early_out_value=1
                    early_out_diff= end_time - att.out_time
                else:
                    # frappe.db.set_value('Attendance', att.name, 'early_exit', 0)
                    # frappe.db.set_value('Attendance', att.name, 'early_out_time',None)
                    early_out_value=0
                    early_out_diff=None
                
            if att.shift == "C":
                shift_time = frappe.get_value("Shift Type", {'name': att.shift}, ["end_time"])
                shift_end_time = datetime.strptime(str(shift_time), '%H:%M:%S').time()
                end_time = dt.datetime.combine(add_days(att.attendance_date,1),shift_end_time)
                if att.out_time < datetime.combine(add_days(att.attendance_date,1), shift_end_time):
                    # frappe.db.set_value('Attendance', att.name, 'early_exit', 1)
                    # frappe.db.set_value('Attendance', att.name, 'early_exit', 1)
                    # frappe.db.set_value('Attendance', att.name, 'early_out_time', end_time - att.out_time )
                    early_out_value=1
                    early_out_diff= end_time - att.out_time
                else:
                    # frappe.db.set_value('Attendance', att.name, 'early_exit', 0)
                    # frappe.db.set_value('Attendance', att.name, 'early_out_time',None)
                    early_out_value=0
                    early_out_diff= None
            frappe.db.set_value('Attendance', att.name, 'early_exit', early_out_value)
            frappe.db.set_value('Attendance', att.name, 'early_out_time',early_out_diff)

    
                       
                

@frappe.whitelist()
def update_checkin_att():
    checkin = frappe.db.sql("""update `tabEmployee Checkin` set attendance = '' where date(time) between "2024-05-01" and "2024-05-17" """,as_dict = True)
    # print(checkin)
    checkin = frappe.db.sql("""update `tabEmployee Checkin` set skip_auto_attendance = 0 where date(time) between "2024-05-01" and "2024-05-17"  """,as_dict = True)
    # print(checkin)
    checkin = frappe.db.sql("""update `tabAttendance` set shift = NULL where attendance_date between "2024-05-01" and "2024-05-17" """,as_dict = True)
    # print(checkin)
    checkin = frappe.db.sql("""update `tabAttendance` set in_time = NULL where attendance_date between "2024-05-01" and "2024-05-17" """,as_dict = True)
    # print(checkin)
    checkin = frappe.db.sql("""update `tabAttendance` set out_time = NULL where attendance_date between "2024-05-01" and "2024-05-17" """,as_dict = True)
    # print(checkin)
    checkin = frappe.db.sql("""update `tabAttendance` set docstatus = 0 where attendance_date between "2024-05-01" and "2024-05-17" """,as_dict = True)
    # print(checkin)
    checkin = frappe.db.sql("""update `tabAttendance` set status = "Absent" where attendance_date between "2024-05-01" and "2024-05-17" """,as_dict = True)
    # print(checkin)
    checkin = frappe.db.sql("""update `tabAttendance` set late_entry = 0 where attendance_date between "2024-05-01" and "2024-05-17" """,as_dict = True)
    # print(checkin)
    checkin = frappe.db.sql("""update `tabAttendance` set late_entry_time = NULL where attendance_date between "2024-05-01" and "2024-05-17" """,as_dict = True)
    # print(checkin)
    checkin = frappe.db.sql("""update `tabAttendance` set early_exit = 0 where attendance_date between "2024-05-01" and "2024-05-17" """,as_dict = True)
    # print(checkin)
    checkin = frappe.db.sql("""update `tabAttendance` set early_out_time = NULL where attendance_date between "2024-05-01" and "2024-05-17" """,as_dict = True)
    # print(checkin)
    checkin = frappe.db.sql("""update `tabAttendance` set total_working_hours = NULL where attendance_date between "2024-05-01" and "2024-05-17" """,as_dict = True)
    # print(checkin)
    checkin = frappe.db.sql("""update `tabAttendance` set working_hours = 0 where attendance_date between "2024-05-01" and "2024-05-17" """,as_dict = True)
    # print(checkin)
    checkin = frappe.db.sql("""update `tabAttendance` set extra_hours = 0 where attendance_date between "2024-05-01" and "2024-05-17" """,as_dict = True)
    # print(checkin)
    checkin = frappe.db.sql("""update `tabAttendance` set total_extra_hours = NULL where attendance_date between "2024-05-01" and "2024-05-17" """,as_dict = True)
    # print(checkin)
    checkin = frappe.db.sql("""update `tabAttendance` set total_overtime_hours = NULL where attendance_date between "2024-05-01" and "2024-05-17" """,as_dict = True)
    # print(checkin)
    checkin = frappe.db.sql("""update `tabAttendance` set overtime_hours = 0 where attendance_date between "2024-05-01" and "2024-05-17" """,as_dict = True)
    # print(checkin)

@frappe.whitelist()
def attendance_check():
    checkin = frappe.db.sql("""
        UPDATE `tabAttendance`
        SET early_out_time = NULL,early_exit =0
        WHERE early_out_time = '00:00:00'
        AND attendance_date BETWEEN '2024-07-07' AND '2024-07-23'
    """, as_dict=True)
    # checkin = frappe.db.sql("""
    #     UPDATE `tabAttendance`
    #     SET late_entry_time = NULL,late_entry =0
    #     WHERE late_entry_time = '00:00:00'
    #     AND attendance_date BETWEEN '2024-07-23' AND '2024-07-23'
    # """, as_dict=True)
    # checkin = frappe.db.sql("""update `tabAttendance` set late_entry_time = ' ' where employee ='20070422' and late_entry_time = '00:00:00' and attendance_date between "2024-07-21" and "2024-07-21" """,as_dict = True)

    # checkin = frappe.db.sql("""update `tabEmployee Checkin` set skip_auto_attendance = 0 where date(time) between "2024-07-23" and "2024-07-23" """,as_dict = True)
    # print(checkin)    

@frappe.whitelist()
def get_assigned_shift(from_date, to_date):
    attendance = frappe.db.get_all('Attendance', {'attendance_date': ('between', (from_date, to_date)),'docstatus': ('!=',2)}, ['*'])
    for att in attendance:
        attendance_date=att.attendance_date
        att_employee=att.employee
        get_att = frappe.db.exists("Shift Assignment", {'employee': att_employee, 'start_date': attendance_date, 'end_date': attendance_date, 'docstatus': 1})
        if get_att:
            assign_name=frappe.db.get_value("Shift Assignment", {'employee': att_employee, 'start_date': attendance_date, 'end_date': attendance_date, 'docstatus': 1},['name'])
            sa = frappe.get_doc("Shift Assignment",assign_name)
            act_shift=sa.shift_type
            if act_shift:
                frappe.db.set_value("Attendance",att.name,'actual_shift',act_shift)