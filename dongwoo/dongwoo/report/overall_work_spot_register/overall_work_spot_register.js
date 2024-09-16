// Copyright (c) 2023, TEAMPRO and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Overall Work Spot Register"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"reqd": 1,
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"reqd": 1,
		},
		{
			"fieldname":"employee_type",
			"label": __("Employee Type"),
			"fieldtype": "Link",
			"options": "Employee Type",
			"reqd": 1,
			"get_query": function () {
				return {
					filters: {
						workspot_available: 1
					}
				};
			},
		}

	]
};
