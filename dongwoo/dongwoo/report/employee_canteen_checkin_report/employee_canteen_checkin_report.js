// Copyright (c) 2023, TEAMPRO and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Employee Canteen Checkin Report"] = {
	"filters": [
		{
            "fieldname": "from_date",
            "label": __(" From Date"),
            "fieldtype": "Date",
            "reqd": 1,
            "default": frappe.datetime.month_start(),
		},
		{
			"fieldname": "now_date",
            "label": __(" Now Date"),
            "fieldtype": "Date",
            "reqd": 1,
            "default": frappe.datetime.nowdate(),
    
        },

	]
};
