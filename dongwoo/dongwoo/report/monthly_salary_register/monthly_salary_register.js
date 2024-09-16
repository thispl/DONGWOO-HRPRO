// Copyright (c) 2023, TEAMPRO and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Monthly Salary Register"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From"),
			"fieldtype": "Date",
			"default": "",
			"reqd": 1,
			"width": "100px"
		},
		{
			"fieldname":"to_date",
			"label": __("To"),
			"fieldtype": "Date",
			"default": "",
			"reqd": 1,
			"width": "100px"
		},
		{
		    "fieldname":"employee_type",
			"label":__("Employee Type"),
			"fieldtype":"Select",
			"options":['',"Staff", "Worker", "Trainee","Contract Employee"],
			"default": "",
			"width": "100px"
		},
		{
			"fieldname": "currency",
			"fieldtype": "Link",
			"options": "Currency",
			"label": __("Currency"),
			"default": erpnext.get_currency(frappe.defaults.get_default("Company")),
			"width": "50px",
			"read_only":1
		},
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": "DongWoo Surfacetech (India) Pvt Ltd.",
			"width": "100px",
			"read_only":1
		},
		{
			"fieldname":"docstatus",
			"label":__("Document Status"),
			"fieldtype":"Select",
			"options":[,"Draft", "Submitted", "Cancelled"],
			"default": "Draft",
			"width": "100px"
		}

	]
};
