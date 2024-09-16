// Copyright (c) 2023, TEAMPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on('Upload Work Spot for CL', {
	get_template: function (frm) {
        window.location.href = repl(frappe.request.url +
            '?cmd=%(cmd)s&date=%(date)s&contractor=%(contractor)s', {
            cmd: "dongwoo.dongwoo.doctype.upload_work_spot_for_cl.upload_work_spot_for_cl.get_template",
            date: frm.doc.date,
            contractor:frm.doc.contractor,
        })
	},
	upload: function (frm) {
		frappe.call({
			method: "dongwoo.dongwoo.doctype.upload_work_spot_for_cl.upload_work_spot_for_cl.upload",
			args: {
				date: frm.doc.date,
				contractor:frm.doc.contractor,
				attach:frm.doc.attach,
			},
			freeze_message: 'Updating Work Spot....',
			callback: function (r) {
				if (r.message=='OK'){
					frappe.msgprint("Work Spot for CL updated successfully")
				}
			 	else if (r.message[0]&&r.message[1]) {
					frappe.msgprint({
						title: __('Error'),
						indicator: 'red',
						message: __('Work Spot - {0} not found for employee {1}', [r.message[1], r.message[0]])
					});
				}
			}
		});
	},
});
