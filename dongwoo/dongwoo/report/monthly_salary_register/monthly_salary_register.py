# Copyright (c) 2023, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt
import erpnext
from frappe.utils.data import add_days, today
from frappe.utils import  formatdate
from frappe.utils import format_datetime

def execute(filters=None):
	if not filters:
		filters = {}
	currency = None
	if filters.get("currency"):
		currency = filters.get("currency")
	company_currency = erpnext.get_company_currency(filters.get("company"))
	salary_slips = get_salary_slips(filters, company_currency)
	if not salary_slips:
		return [], []
	
	columns, earning_types, ded_types = get_columns(salary_slips)
	ss_earning_map = get_ss_earning_map(salary_slips, currency, company_currency)
	ss_ded_map = get_ss_ded_map(salary_slips, currency, company_currency)
	doj_map = get_employee_doj_map()

	data = []
	for ss in salary_slips:
		row = [
			frappe.db.get_value('Employee',ss.employee,'department') or "",
			ss.employee,
			ss.employee_name,
			frappe.db.get_value('Employee',ss.employee,'bank_ac_no') or "",
			frappe.db.get_value('Employee',ss.employee,'mop') or "",
			frappe.db.get_value('Employee',ss.employee,'designation') or "",
			frappe.db.get_value('Employee',ss.employee,'employee_type') or "",
			frappe.db.get_value('Employee',ss.employee,'uan_number') or "-",
			formatdate(frappe.db.get_value('Employee',ss.employee,'date_of_joining') or ""),
			frappe.db.get_value('Employee',ss.employee,'basic') or 0,
			frappe.db.get_value('Employee',ss.employee,'house_rent_allowance') or 0,
			frappe.db.get_value('Employee',ss.employee,'medical_allowance') or 0,
			frappe.db.get_value('Employee',ss.employee,'conveyance_allowance') or 0,
			frappe.db.get_value('Employee',ss.employee,'education_allowance') or 0,
			frappe.db.get_value('Employee',ss.employee,'leave_and_travel_allowance') or 0,
			frappe.db.get_value('Employee',ss.employee,'dress_allowance') or 0,
			(int(frappe.db.get_value('Employee',ss.employee,'basic') or 0)+
			int(frappe.db.get_value('Employee',ss.employee,'house_rent_allowance') or 0)+
			int(frappe.db.get_value('Employee',ss.employee,'medical_allowance') or 0)+
			int(frappe.db.get_value('Employee',ss.employee,'conveyance_allowance') or 0)+
			int(frappe.db.get_value('Employee',ss.employee,'education_allowance') or 0)+
			int(frappe.db.get_value('Employee',ss.employee,'leave_and_travel_allowance') or 0)+
			int(frappe.db.get_value('Employee',ss.employee,'dress_allowance') or 0) )or 0,
			ss.lop or 0,
			ss.payment_days,
			ss.total_working_days,
			int(frappe.get_value('Salary Detail',{'salary_component':"Basic",'parent':ss.name},["amount"]) or 0),
			int(frappe.get_value('Salary Detail',{'salary_component':"House Rent Allowance",'parent':ss.name},["amount"]) or 0),
			int(frappe.get_value('Salary Detail',{'salary_component':"Medical Allowance",'parent':ss.name},["amount"]) or 0),
			int(frappe.get_value('Salary Detail',{'salary_component':"Conveyance Allowance",'parent':ss.name},["amount"]) or 0),
			int(frappe.get_value('Salary Detail',{'salary_component':"Education Allowance",'parent':ss.name},["amount"]) or 0),
			int(frappe.get_value('Salary Detail',{'salary_component':"Leave and Travel Allowance",'parent':ss.name},["amount"]) or 0),
			int(frappe.get_value('Salary Detail',{'salary_component':"Dress Allowance",'parent':ss.name},["amount"]) or 0),
			ss.gross_pay or 0,
			int(frappe.get_value('Salary Detail',{'salary_component':"Overtime ",'parent':ss.name},["amount"]) or 0),
			int(frappe.get_value('Salary Detail',{'salary_component':"Bus Fare ",'parent':ss.name},["amount"]) or 0),
			int(frappe.get_value('Salary Detail',{'salary_component':"Festival Allowance",'parent':ss.name},["amount"]) or 0),
			int(frappe.get_value('Salary Detail',{'salary_component':"Arrear",'parent':ss.name},["amount"]) or 0),
			int(frappe.get_value('Salary Detail',{'salary_component':"Attendance Bonus",'parent':ss.name},["amount"]) or 0),
			int(frappe.get_value('Salary Detail',{'salary_component':"Supervisor Allowance ",'parent':ss.name},["amount"]) or 0),
			int(frappe.get_value('Salary Detail',{'salary_component':"Shift Allowance ",'parent':ss.name},["amount"]) or 0),
			int(frappe.get_value('Salary Detail',{'salary_component':"Special Duty Allowance",'parent':ss.name},["amount"]) or 0),
			(int(frappe.get_value('Salary Detail',{'salary_component':"Overtime ",'parent':ss.name},["amount"]) or 0)+
			int(frappe.get_value('Salary Detail',{'salary_component':"Bus Fare ",'parent':ss.name},["amount"]) or 0)+
			int(frappe.get_value('Salary Detail',{'salary_component':"Festival Allowance",'parent':ss.name},["amount"]) or 0)+
			int(frappe.get_value('Salary Detail',{'salary_component':"Arrear",'parent':ss.name},["amount"]) or 0)+
			int(frappe.get_value('Salary Detail',{'salary_component':"Attendance Bonus",'parent':ss.name},["amount"]) or 0)+
			int(frappe.get_value('Salary Detail',{'salary_component':"Supervisor Allowance ",'parent':ss.name},["amount"]) or 0)+
			int(frappe.get_value('Salary Detail',{'salary_component':"Shift Allowance ",'parent':ss.name},["amount"]) or 0)+
			int(frappe.get_value('Salary Detail',{'salary_component':"Special Duty Allowance",'parent':ss.name},["amount"]) or 0)) or 0,
			int(frappe.get_value('Salary Detail',{'salary_component':"Provident Fund",'parent':ss.name},["amount"]) or 0),
			int(frappe.get_value('Salary Detail',{'salary_component':"Income Tax",'parent':ss.name},["amount"]) or 0),
			int(frappe.get_value('Salary Detail',{'salary_component':"Professional Tax",'parent':ss.name},["amount"]) or 0),
			int(frappe.get_value('Salary Detail',{'salary_component':"Advance",'parent':ss.name},["amount"]) or 0),
			ss.total_deduction,
			ss.net_pay
			]
		frappe.errprint(row)
		data.append(row)
	return columns,data
def get_columns(salary_slips):
	columns = [
		_("Department") + "::100",
		_("Employee") + ":Employee:120",
		_("Employee Name") + "::200",
		_("Account No") + "::200",
		_("MOP") + "::100",
		_("Designation") + "::100",
		_("Employee Type") + "::100",
		_("PF UAN No") + "::120",
		_("Date of Joining") + "::120",
		_("Fixed Basic") + ":Data:100",
		_("Fixed House Rent Allowance") + ":Data:200",
		_("Fixed Medical Allowance") + "::120",
		_("Fixed Conveyance Allowance") + ":Data:200",
		_("Fixed Education Allowance") + ":Data:200",
		_("Fixed Leave and Travel Allowance") + ":Data:200",
		_("Fixed Dress Allowance") + ":Data:200",
		_("Fixed Total") + ":Data:150",
		_("LOP") + ":Data:150",
		_("Payment Days") + ":Data:150",
		_("Total Working Days") + ":Data:150",
		_("Earned Basic") + ":Data:100",
		_("Earned House Rent Allowance") + ":Data:200",
		_("Earned MedicalAllowance") + ":Data:200",
		_("Earned Conveyance Allowance") + ":Data:200",
		_("Earned Education Allowance") + ":Data:200",
		_("Earned Leave and Travel Allowance") + ":Data:200",
		_("Earned Dress Allowance") + ":Data:200",
		_("Gross Pay") + ":Currency:150",
		_("OT Amount") + ":Data:120",
		_("Bus Fare") + ":Data:150",
		_("Festival Allowance") + ":Data:150",
		_("Arrears") + ":Data:150",
		_("Attentance Bonus") + ":Data:150",
		_("Supervisor Allowance") + ":Data:150",
		_("Shift Allowance") + ":Data:150",
		_("Special Duty Allowance") + ":Data:150",
		_("Total") + ":Data:120",
		_("Deduction Provident Fund") + ":Data:150",
		_("Deduction Income Tax") + ":Data:150",
		_("Deduction Professional Tax") + ":Data:150",
		_("Deduction Advance") + ":Data:150",
		_("Total Deductions") + ":Data:150",
		_("Net Pay") + ":Data:150",
	]

	salary_components = {_("Earning"): [], _("Deduction"): []}

	for component in frappe.db.sql(
		"""select distinct sd.salary_component, sc.type
		from `tabSalary Detail` sd, `tabSalary Component` sc
		where sc.name=sd.salary_component and sd.amount != 0 and sd.parent in (%s)"""
		% (", ".join(["%s"] * len(salary_slips))),
		tuple([d.name for d in salary_slips]),
		as_dict=1,
	):
		salary_components[_(component.type)].append(component.salary_component)
	return columns, salary_components[_("Earning")], salary_components[_("Deduction")]

def get_salary_slips(filters, company_currency):
	filters.update({"from_date": filters.get("from_date"), 
	"to_date": filters.get("to_date"),
	})
	conditions, filters = get_conditions(filters, company_currency)
	salary_slips = frappe.db.sql(
		"""select * from `tabSalary Slip` where docstatus != 2 and %s """% conditions,
		filters,
		as_dict=1,
	)
	return salary_slips or []
def get_conditions(filters, company_currency):
	conditions = ""
	doc_status = {"Draft": 0, "Submitted": 1, "Cancelled": 2}
	# employee_type={"Staff":0, "Worker":1, "trainee":2,"Contract Employee":3}
	if filters.get("docstatus"):
		conditions += "docstatus = {0}".format(doc_status[filters.get("docstatus")])
	if filters.get("from_date"):
		conditions += " and start_date >= %(from_date)s"
	if filters.get("to_date"):
		conditions += " and end_date <= %(to_date)s"
	if filters.get("company"):
		conditions += " and company = %(company)s"
	if filters.get("employee_type"):
		conditions += " and employee_type = %(employee_type)s"
	if filters.get("currency") and filters.get("currency") != company_currency:
		conditions += " and currency = %(currency)s"
	return conditions, filters

def get_employee_doj_map():
	return frappe._dict(frappe.db.sql("""SELECT employee,date_of_joining FROM `tabEmployee` """))

def get_ss_earning_map(salary_slips, currency, company_currency):
	ss_earnings = frappe.db.sql(
		"""select sd.parent, sd.salary_component, sd.amount, ss.exchange_rate, ss.name
		from `tabSalary Detail` sd, `tabSalary Slip` ss where sd.parent=ss.name and sd.parent in (%s)"""
		% (", ".join(["%s"] * len(salary_slips))),
		tuple([d.name for d in salary_slips]),
		as_dict=1,
	)
	
	ss_earning_map = {}
	for d in ss_earnings:
		ss_earning_map.setdefault(d.parent, frappe._dict()).setdefault(d.salary_component, 0.0)
		if currency == company_currency:
			ss_earning_map[d.parent][d.salary_component] += flt(d.amount) * flt(
				d.exchange_rate if d.exchange_rate else 1
			)
		else:
			ss_earning_map[d.parent][d.salary_component] += flt(d.amount)
	return ss_earning_map


def get_ss_ded_map(salary_slips, currency, company_currency):
	ss_deductions = frappe.db.sql(
		"""select sd.parent, sd.salary_component, sd.amount, ss.exchange_rate, ss.name
		from `tabSalary Detail` sd, `tabSalary Slip` ss where sd.parent=ss.name and sd.parent in (%s)"""
		% (", ".join(["%s"] * len(salary_slips))),
		tuple([d.name for d in salary_slips]),
		as_dict=1,
	)

	ss_ded_map = {}
	for d in ss_deductions:
		ss_ded_map.setdefault(d.parent, frappe._dict()).setdefault(d.salary_component, 0.0)
		if currency == company_currency:
			ss_ded_map[d.parent][d.salary_component] += flt(d.amount) * flt(
				d.exchange_rate if d.exchange_rate else 1
			)
		else:
			ss_ded_map[d.parent][d.salary_component] += flt(d.amount)
	return ss_ded_map
