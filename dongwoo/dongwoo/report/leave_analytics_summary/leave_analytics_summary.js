// Copyright (c) 2024, TEAMPRO and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Leave Analytics Summary"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"reqd": 1,
			on_change: function () {
				var from_date = frappe.query_report.get_filter_value('from_date')
				frappe.call({
					method: "dongwoo.dongwoo.report.monthly_attendance_register.monthly_attendance_register.get_to_date",
					args: {
						from_date: from_date
					},
					callback(r) {
						frappe.query_report.set_filter_value('to_date', r.message);
						frappe.query_report.refresh();
					}
				})
			}
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"reqd": 1,
		},
		{
			"fieldname": "employee_type",
			"label": __("Employee Type"),
			"fieldtype": "Link",
			"options": "Employee Type",
			"reqd": 1,
		},
	],
	"onload": function(report) {
		const reportTable = document.querySelector('.query-report');
		if (reportTable) {
			reportTable.style.direction = 'rtl';
			reportTable.style.textAlign = 'center';

			// Center align row values
			const rows = reportTable.querySelectorAll('tbody tr');
			rows.forEach(row => {
				row.style.textAlign = 'center';
			});
		}
	}
};
