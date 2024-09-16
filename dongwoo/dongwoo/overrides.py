from email import message
import frappe
from frappe import _
import datetime, math
from hrms.payroll.doctype.salary_slip.salary_slip import SalarySlip
from hrms.hr.doctype.shift_assignment.shift_assignment import ShiftAssignment

from hrms.hr.utils import get_holiday_dates_for_employee
from hrms.hr.utils import get_holidays_for_employee
from frappe.utils import cstr, add_days, date_diff,format_datetime,ceil,flt
from frappe.utils import (getdate, cint, add_months, date_diff, add_days,nowdate, get_datetime_str, cstr, get_datetime, now_datetime, format_datetime, format_date,get_time)
from datetime import time,timedelta
class CustomSalarySlip(SalarySlip):

    # def get_payment_days(self, joining_date, relieving_date, include_holidays_in_total_working_days):
    #     if not joining_date:
    #         joining_date, relieving_date = frappe.get_cached_value(
    #             "Employee", self.employee, ["date_of_joining", "relieving_date"]
    #         )

    #     start_date = getdate(self.start_date)
    #     if joining_date:
    #         if getdate(self.start_date) <= joining_date <= getdate(self.end_date):
    #             start_date = joining_date
    #         elif joining_date > getdate(self.end_date):
    #             return

    #     end_date = getdate(self.end_date)
    #     if relieving_date:
    #         if getdate(self.start_date) <= relieving_date <= getdate(self.end_date):
    #             end_date = relieving_date
    #         elif relieving_date < getdate(self.start_date):
    #             frappe.throw(_("Employee relieved on {0} must be set as 'Left'").format(relieving_date))

    #     payment_days = date_diff(end_date, start_date) + 1

    #     if not cint(include_holidays_in_total_working_days):
    #         ww_count = frappe.db.count("Shift Assignment",{"employee":self.employee,"shift_type":"WW","start_date": ["between", [self.start_date,self.end_date]]})
    #         holidays = self.get_holidays_for_employee(start_date, end_date) 
    #         payment_days -= len(holidays) + ww_count

    #     return payment_days

    # def get_holidays_for_employee(self, start_date, end_date):
        
    #     return get_holiday_dates_for_employee(self.employee, start_date, end_date)

    def get_date_details(self):
        if self.salary_structure == 'Staff':
            ot_hrs = frappe.db.sql("""
                SELECT SUM(overtime_hours) AS ot_total 
                FROM `tabAttendance`
                WHERE attendance_date BETWEEN %s AND %s 
                AND employee = %s 
                AND docstatus = 1
            """, (self.start_date, self.end_date, self.employee), as_dict=True)
            if ot_hrs and len(ot_hrs) > 0:
                self.ot_hours = ot_hrs[0].ot_total or 0
            else:
                self.ot_hours = 0
        elif self.salary_structure == 'Worker':
            ot_hrs = frappe.db.sql("""
            SELECT SUM(total_hours) AS ot_total 
            FROM `tabOvertime Request`
            WHERE ot_date BETWEEN %s AND %s 
            AND employee = %s 
            AND docstatus = 1
            """, (self.start_date, self.end_date, self.employee), as_dict=True)
            if ot_hrs and len(ot_hrs) > 0:
                self.ot_hours = ot_hrs[0].ot_total or 0
            else:
                self.ot_hours = 0
        else:
            self.ot_hours = 0
        
        if self.employee_type=="Worker" or self.employee_type=="D . Trainee":
            b_pre = frappe.db.count("Attendance", {
                "employee": self.employee,
                "shift": "B",
                "attendance_date": ['between', (self.start_date, self.end_date)],
                "status": "Present",
                "docstatus": 1
            })
            b_hd = frappe.db.count("Attendance", {
                "employee": self.employee,
                "shift": "B",
                "attendance_date": ['between', (self.start_date, self.end_date)],
                "status": "Half Day",
                "docstatus": 1
            })
            b_count=b_pre+b_hd*0.5
            c_pre = frappe.db.count("Attendance", {
                "employee": self.employee,
                "shift": "C",
                "attendance_date": ['between', (self.start_date, self.end_date)],
                "status": "Present",
                "docstatus": 1
            })
            c_hd = frappe.db.count("Attendance", {
                "employee": self.employee,
                "shift": "C",
                "attendance_date": ['between', (self.start_date, self.end_date)],
                "status": "Half Day",
                "docstatus": 1
            })
            c_count=c_pre+c_hd*0.5
            self.custom_no_of_2_shift=b_count
            self.custom_no_of_3_shift=c_count
            frappe.errprint(b_count)
            frappe.errprint(c_count)
            # self.save(ignore_permissions=True)
            if self.payment_days==self.total_working_days:
                if self.employee_type=="Worker":
                    l_count = frappe.db.count("Attendance", {
                    "employee": self.employee,
                    "attendance_date": ('between', (self.start_date, self.end_date)),
                    "leave_application": ('!=',''),
                    "docstatus": 1
                    })
                    if l_count<1:
                        frappe.errprint("considered")
                        self.att_bonus=800
                        # frappe.errprint(self.attendance_bonus)
                    else:
                        frappe.errprint("notconsidered")
                        self.att_bonus=0
                if self.employee_type=="D . Trainee":
                    frappe.errprint("1")
                    l_count = frappe.db.count("Attendance", {
                    "employee": self.employee,
                    "attendance_date": ('between', (self.start_date, self.end_date)),
                    "leave_application": ('!=',''),
                    "docstatus": 1
                    })
                    if l_count<1:
                        self.att_bonus=800
                    else:
                        if l_count==1:
                            l_name = frappe.db.get_value("Attendance", {
                            "employee": self.employee,
                            "leave_application": ('!=',''),
                            "docstatus": 1},['leave_application'])
                            ltype=frappe.db.get_value("Leave Application",{'name':l_name},['leave_type'])
                            check_lwp=frappe.db.get_value("Leave Type",{'name':ltype},['is_lwp'])
                            if check_lwp==0:
                                self.att_bonus=500
                            else:
                                self.att_bonus=0
                        else:
                            self.att_bonus=0
        if self.employee_type=="Staff":
            frappe.errprint("FROM HERE")
            attendance=frappe.get_all("Attendance",{"employee": self.employee,'employee_type':'Staff','working_hours':('>=',23),'attendance_date':('between',(self.start_date,self.end_date))},['attendance_date','out_time'])
            self.special_all=0
            if attendance:
                shift_et = frappe.db.get_value("Shift Type", {'name': 'C'}, ['end_time'])
                if isinstance(shift_et, str):
                    shift_et = time.fromisoformat(shift_et)
                holiday_dates = get_holiday_dates_for_employee(self.employee, self.start_date, self.end_date)
                for holiday in holiday_dates:
                    day_before_holidays = [add_days(holiday,-1)]
                for att in attendance:
                    # if isinstance(att.out_time, datetime):
                    #     out_time = att.out_time.time()
                    # else:
                    out_time = att.out_time.time()
                    out_time_timedelta = timedelta(hours=out_time.hour, minutes=out_time.minute, seconds=out_time.second)
                    # out_time = att.out_time.time() if isinstance(att.out_time, datetime) else att.out_time
                    if out_time_timedelta >= shift_et:
                        day_of_week = att.attendance_date.weekday()
                        if cstr(att.attendance_date) in holiday_dates:
                            self.special_all+=2500
                            frappe.errprint("holiday_date")
                        elif cstr(att.attendance_date) in day_before_holidays:
                            self.special_all+=3000
                        else:
                            if day_of_week in [0,1,2,3,4]:
                                self.special_all+=1000
                            elif day_of_week ==5:
                                self.special_all+=3000
                            elif day_of_week ==6:
                                self.special_all+=2500
                frappe.errprint(self.special_all)

class CustomShiftAssignment(ShiftAssignment):
    def on_submit(self):
        if self.shift_type!='WW':
            if frappe.db.exists("Attendance", {"attendance_date": self.start_date, "employee": self.employee, "docstatus": ["!=",2]}):
                att=frappe.db.get_value("Attendance", {"attendance_date": self.start_date, "employee": self.employee, "docstatus": ["!=",2]},['name'])
                frappe.db.set_value("Attendance",att,'actual_shift',self.shift_type)
            else:
                att = frappe.new_doc("Attendance")
                att.employee = self.employee
                att.actual_shift =self.shift_type
                att.attendance_date = self.start_date
                att.status = 'Absent'
                att.total_working_hours = '00:00:00'
                att.total_extra_hours = '00:00:00'
                att.total_overtime_hours = '00:00:00'
                att.save()
        