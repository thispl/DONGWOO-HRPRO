// Copyright (c) 2023, TEAMPRO and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Employeewise Meal Count Report"] = {
	"filters": [
		{
            "fieldname": "date",
            "label": __(" Date"),
            "fieldtype": "Date",
            "reqd": 1,
            "default": frappe.datetime.nowdate()
    
        },

	]
};
