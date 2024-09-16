// Copyright (c) 2023, TEAMPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on('Attendance Settings', {
	process_checkin(frm){
		frappe.call({
			"method": "dongwoo.custom.get_urc_to_ec",
			"args":{
				"from_date" : frm.doc.date,
			},
			freeze: true,
			freeze_message: 'Processing UnRegistered Employee Checkin to Employee Checkin....',
			callback(r){
				console.log(r.message)
				if(r.message == "ok"){
					frappe.msgprint("Checkin's are created in Successfully")
				}
			}
		})
	},
});
