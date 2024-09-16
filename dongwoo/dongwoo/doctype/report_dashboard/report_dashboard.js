// Copyright (c) 2023, TEAMPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on('Report Dashboard', {
	start_date(frm) {
		frappe.call({
			method: 'dongwoo.dongwoo.doctype.report_dashboard.report_dashboard.get_end_date',
			args: {
				frequency: "Monthly",
				start_date: frm.doc.start_date
			},
			callback: function (r) {
				if (r.message) {
					frm.set_value('end_date', r.message.end_date);
				}
			}
		});
	},
	download:function(frm){
		if (frm.doc.report == 'Personnel Record') {
			var path = 'dongwoo.dongwoo.doctype.report_dashboard.personnel_record.download'
			var args = 'start_date=%(start_date)s&end_date=%(end_date)s&employee_type=%(employee_type)s'
		}
		if (frm.doc.report == 'Organizational Chart') {
			var path = 'dongwoo.dongwoo.doctype.report_dashboard.organizational_chart.download'
			var args = 'start_date=%(start_date)s&end_date=%(end_date)s&employee_type=%(employee_type)s'
		}
		if (frm.doc.report == 'Overall Attendance Summary') {
			frappe.call({
				method : 'dongwoo.dongwoo.doctype.report_dashboard.overall_attendance_summary.download',
				args : {
					start_date : frm.doc.start_date,
					end_date : frm.doc.end_date
				}
			})
		}
		if (frm.doc.report == 'Daily Attendance Summary') {
			frappe.call({
				method : 'dongwoo.dongwoo.doctype.report_dashboard.daily_summary.download',
				args : {
					start_date : frm.doc.start_date,
					end_date : frm.doc.end_date
				}
			})
		}
		if (frm.doc.report == 'Today Canteen Count Report') {
			frappe.call({
				method : 'dongwoo.dongwoo.doctype.report_dashboard.today_summary.download',
				args : {
					start_date : frm.doc.start_date,
					end_date : frm.doc.end_date
				}
			})
		}
		if (frm.doc.report == 'Monthly Salary Report') {
			// console.log('hi')
			var path = 'dongwoo.dongwoo.doctype.report_dashboard.monthly_salary_report.download'
			var args = 'start_date=%(start_date)s&end_date=%(end_date)s&company=%(company)'
		
		}
		if (path) {
			window.location.href = repl(frappe.request.url +
				'?cmd=%(cmd)s&%(args)s', {
				cmd: path,
				args: args,
				start_date : frm.doc.start_date,
				end_date : frm.doc.end_date,
				employee_type :frm.doc.employee_type
			});
		}
		if (frm.doc.report == "Salary Statement Summary") {
			var path = 'dongwoo.dongwoo.doctype.report_dashboard.salary_statement_summary.download'
			var args = 'start_date=%(start_date)s&end_date=%(end_date)s&employee_type=%(employee_type)s'
		}
		
		// frm.add_custom_button('View Current Status', () => {
		// 	frappe.call({
		// 		method: 'dongwoo.dongwoo.doctype.report_dashboard.report_dashboard.get_latest_rq_job',  // Update this path
		// 		callback: function(r) {
		// 			if (r.message) {
		// 				frappe.set_route('Form', 'RQ Job', r.message);
		// 			} else {
		// 				frappe.msgprint(__('No RQ Job found.'));
		// 			}
		// 		}
		// 	});
		// });
		frm.add_custom_button('View Current Status', () => {
            frappe.set_route('Form','RQ Job');
        });
		
	}
});
