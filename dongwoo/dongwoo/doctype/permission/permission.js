// Copyright (c) 2023, TEAMPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on('Permission', {
	permission_date(frm){
		frm.call('sat_res').then(j=>{
			// if (j.message) {
			// 	frm.fields_dict.perm.$wrapper.empty().append(j.message)
			// }
		})	
	},
	total_time(frm){
		frm.call('hour_res').then(j=>{
			
		})	
	},
						
});
