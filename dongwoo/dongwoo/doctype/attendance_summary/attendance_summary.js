frappe.ui.form.on('Attendance Summary', {
	refresh: function (frm) {
        frm.fields_dict.html.$wrapper.empty();
        frm.disable_save();
        frappe.model.clear_table(frm.doc, "attendance");

        // Check if the user is a System Manager or if no employee is selected
        if (frappe.user.has_role('System Manager') || !frm.doc.employee) {
            frm.fields_dict.html.$wrapper.empty().append("<center><h2>Please select an employee</h2></center>");
            frm.set_value('employee', null); // Reset employee field
        
            // Set default values for from_date and to_date
			var today = frappe.datetime.nowdate();
			frm.set_value('from_date', frappe.datetime.month_start(today));
			frm.set_value('to_date', frappe.datetime.month_end(today));
        }

        frm.trigger('get_data'); // Moved here to ensure it's triggered after setting dates
    },
    onload: function (frm) {
		// Check if the user is a System Manager or if no employee is selected
		if (frappe.user.has_role('System Manager')) {
			frm.fields_dict.employee.$input.prop("disabled", true); // Disable employee field
			frm.set_value('employee', null); // Reset employee field
		} else {
			frappe.call({
				method: 'dongwoo.dongwoo.doctype.attendance_summary.attendance_summary.get_employee',
				args: {},
				callback: function (r) {
					frm.set_value('employee', r.message[0]);
					frm.set_value('employee_name', r.message[1]);
					frm.trigger('get_data');
				}
			});
	
			// Set the query for the employee field
			frm.set_query('employee', function (doc) {
				return {
					filters: {
						"status": "Active",
						"department": frm.doc.department // Adjust as needed
					}
				};
			});
		}
	
		// Set default values for from_date and to_date
        var today = frappe.datetime.nowdate();
        frm.set_value('from_date', frappe.datetime.month_start(today));
        frm.set_value('to_date', frappe.datetime.month_end(today));

	
		frm.trigger('get_data');
	},
	
    employee: function (frm) {
        frm.trigger('get_data');
    },
    from_date: function (frm) {
        frm.trigger('get_data');
    },
    to_date: function (frm) {
        frm.trigger('get_data');
    },
    get_data: function (frm) {
        if (frm.doc.employee) {
            if (!frappe.is_mobile()) {
                frm.trigger('get_data_system');
            } else {
                frm.trigger('get_data_mobile');
            }
        } else {
            frm.fields_dict.html.$wrapper.empty().append("<center><h2>Please select an employee</h2></center>");
        }
    },
    get_data_system: function (frm) {
        if (frm.doc.employee) {
            frappe.call({
                method: "dongwoo.dongwoo.doctype.attendance_summary.attendance_summary.get_data_system",
                args: {
                    emp: frm.doc.employee,
                    from_date: frm.doc.from_date,
                    to_date: frm.doc.to_date
                },
                callback: function (r) {
                    frm.fields_dict.html.$wrapper.empty().append(r.message);
                }
            });
        } else {
            frm.fields_dict.html.$wrapper.empty().append("<center><h2>Attendance Not Found</h2></center>");
        }
    },
    get_data_mobile: function (frm) {
        if (frm.doc.employee) {
            frappe.call({
                method: "dongwoo.dongwoo.doctype.attendance_summary.attendance_summary.get_data_system",
                args: {
                    emp: frm.doc.employee,
                    from_date: frm.doc.from_date,
                    to_date: frm.doc.to_date
                },
                callback: function (r) {
                    frm.fields_dict.html.$wrapper.empty().append(r.message);
                }
            });
        } else {
            frm.fields_dict.html.$wrapper.empty().append("<center><h2>Attendance Not Found</h2></center>");
        }
    },
});
