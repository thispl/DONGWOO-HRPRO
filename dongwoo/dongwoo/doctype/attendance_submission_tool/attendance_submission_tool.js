// Copyright (c) 2023, TEAMPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on('Attendance Submission Tool', {
	refresh: function(frm) {
		// frm.disable_save()
	},
	submit_attendance(frm){
		if (frm.doc.employeewise == 0){
			frappe.call({
				"method": "dongwoo.mark_attendance.submit_att",
				"args":{
					"from_date" : frm.doc.from_date,
					"to_date" : frm.doc.to_date,
					"employee_type" : frm.doc.employee_type,
					"department" : frm.doc.department,
				},
				freeze: true,
				freeze_message: 'Submit the Attendance....',
				callback(r){
					console.log(r.message)
					if(r.message == "ok"){
						frappe.msgprint("Attendance is submitted Successfully")
					}
				}
			})
		}
		else{
			frappe.call({
				"method": "dongwoo.mark_attendance.submit_att_with_employee",
				"args":{
					"from_date" : frm.doc.from_date,
					"to_date" : frm.doc.to_date,
					"employee":frm.doc.employee
				},
				freeze: true,
				freeze_message: 'Submit the Attendance....',
				callback(r){
					console.log(r.message)
					if(r.message == "ok"){
						frappe.msgprint("Attendance is submitted Successfully")
					}
				}
			})
		}
	},
});
