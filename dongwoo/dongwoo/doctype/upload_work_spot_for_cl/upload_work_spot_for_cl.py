# Copyright (c) 2023, TEAMPRO and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from csv import writer
from inspect import getfile
from unicodedata import name
import frappe
from frappe.utils import cstr, add_days, date_diff, getdate
from frappe import throw,_
from frappe.utils.csvutils import UnicodeWriter, read_csv_content
from frappe.utils.file_manager import get_file, upload
from frappe.model.document import Document
from datetime import datetime,timedelta,date,time
from frappe.utils import cint,today,flt,date_diff,add_days,add_months,date_diff,getdate,formatdate,cint,cstr


class UploadWorkSpotforCL(Document):
	def validate(self):
		contractor = frappe.db.sql("""select name from `tabUpload Work Spot for CL` where contractor = '%s' and date = '%s'""" % (self.contractor, self.date,), as_dict=True)
		if contractor:
			throw(_('Contractor Work Spot already uploaded for the selected date'))

@frappe.whitelist()
def get_template():
	args = frappe.local.form_dict

	w = UnicodeWriter()
	w = add_header(w)
	w = add_data(w, args)

	frappe.response['result'] = cstr(w.getvalue())
	frappe.response['type'] = 'csv'
	frappe.response['doctype'] = "Upload Work Spot for CL"

def add_header(w):
	w.writerow(['Employee ID','Employee Name','Workspot'])
	return w

def add_data(w, args):
	data = get_data(args)
	writedata(w, data)
	return w

@frappe.whitelist()
def get_data(args):
	if args.contractor:
		employee=frappe.db.get_all("Employee",{'contractor':args.contractor,'status':'Active'},['*'])
		data = []
		if employee:
			for e in employee:
				row =[e.employee_number,e.employee_name,'']
			data.append(row)
	return data
			

@frappe.whitelist()
def writedata(w, data):
	for row in data:
		w.writerow(row)

@frappe.whitelist()
def upload():
	args = frappe.local.form_dict
	if args.attach:
		filepath = get_file(args.attach)
		pps = read_csv_content(filepath[1])

		for pp in pps:
			if pp[0] != 'Employee ID':
				if pp[1]:
					workspot=frappe.db.exists("Workspot for CL",{'employee':pp[0],'date':args.date})
					if not workspot:
						if frappe.db.exists("Workspot",{"workspot":pp[2]}):
							doc = frappe.new_doc('Workspot for CL')
							doc.employee = pp[0]
							doc.workspot = pp[2]
							doc.employee_name = pp[1]
							doc.contractor = args.contractor
							doc.date = args.date
							doc.save(ignore_permissions=True)
							frappe.db.commit()
							return 'OK'
						else:
							return pp[1],pp[2]
					else:
						if frappe.db.exists("Workspot",{"workspot":pp[2]}):
							doc = frappe.get_doc('Workspot for CL',workspot)
							doc.employee = pp[0]
							doc.workspot = pp[2]
							doc.employee_name = pp[1]
							doc.contractor = args.contractor
							doc.date = args.date
							doc.save(ignore_permissions=True)
							return 'OK'
						else:
							return pp[1],pp[2]





