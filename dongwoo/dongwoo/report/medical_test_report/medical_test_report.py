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
		_('Employee Name')+':Data:150',
		_('Employee ')+':Data:150',
 		_('Age')+':Data:150',
		_('Gender')+':Data:150',
		_('Hemoglobin')+':Data:150',
		_('Packed Cell Volume')+':Data:150',
		_('White Blood Cells')+':Data:150',
 		_('Red Blood Cells')+':Data:150',
 		_('Platelet')+':Data:150',
 		_('Neutrophils')+':Data:150',
 		_('Lymphocytes')+':Data:150',
 		_('Eosinophils')+':Data:150',
 		_('Monocytes')+':Data:150',
 		_('Erythrocyte Sedimentation Rate')+':Data:150',
 		_('Blood Group')+':Data:150',
 		_('Random Blood Sugar')+':Data:150',
 		_('Urea')+':Data:150',
 		_('Creatinine')+':Data:150',
 		_('Albumin')+':Data:150',
 		_('Suger')+':Data:150',
 		_('Puscells ')+':Data:150',
 		_('Epithelial Cells ')+':Data:150',
 		_('Red Blood Cell')+':Data:150',
 		_('Urinary Casts')+':Data:150',
 		_('Crystals ')+':Data:150',
 		_('X Ray')+':Data:150',
 		_('Audio')+':Data:150',
 		_('Pulmonary Function Test')+':Data:150',
		_('ECG')+':Data:150',
		_('Eye')+':Data:150',
		_('Remarks')+':Data:150',
          ]
	return columns

def get_data(filters):
	data = []
	employee= frappe.db.sql("""select * from `tabYearly Medical Test` where date between '%s' and '%s' """ %(filters.from_date, filters.to_date) , as_dict=1)
	for t in employee:
		row = [t.employee_name,t.employee,t.age,t.gender,t.hemoglobin,t.packed_cell_volume,t.white_blood_cells,t.red_blood_cells,t.platelet,t.neutrophils,t.lymphocytes,t.eosinophils,t.monocytes,t.erythrocyte_sedimentation_rate,t.blood_group,t.random_blood_sugar,t.urea,t.creatinine,t.albumin,t.suger,t.puscells,t.epithelial_cells,t.red_blood_cell,t.urinary_casts,t.crystals,t.x_ray,t.audio,t.pulmonary_function_test,t.ecg,t.eye,t.remarks]
		data.append(row)
	return data

