import frappe
from datetime import datetime

@frappe.whitelist(allow_guest=True)
def mark_checkin(**args):
	if frappe.db.exists('Employee',{'name':args['employee']}):
		try:
			if args['device_id'] == 'IN 1' or args['device_id'] == 'IN 2':
				if not frappe.db.exists('Employee Checkin',{'employee':args['employee'],'time':args['time']}):
					ec = frappe.new_doc('Employee Checkin')
					ec.employee = args['employee'].upper()
					ec.time = args['time']
					ec.device_id = args['device_id']
					ec.log_type = 'IN'
					ec.save(ignore_permissions=True)
					frappe.db.commit()
					return "Checkin Marked"
			elif args['device_id'] == 'OUT 1' or args['device_id'] == 'OUT 2':
				if not frappe.db.exists('Employee Checkin',{'employee':args['employee'],'time':args['time']}):
					ec = frappe.new_doc('Employee Checkin')
					ec.employee = args['employee'].upper()
					ec.time = args['time']
					ec.device_id = args['device_id']
					ec.log_type = 'OUT'
					ec.save(ignore_permissions=True)
					frappe.db.commit()
					return "Checkin Marked"     
			# elif args['device_id'] == 'C1' or args['device_id'] == 'C2':
			# 	if not frappe.db.exists('Canteen Checkin',{'employee':args['employee'],'time':args['time']}):
			# 		ec = frappe.new_doc('Canteen Checkin')
			# 		ec.employee = args['employee'].upper()
			# 		# ec.time = args['time']
			# 		ec.device_id = args['device_id']
			# 		att_time = args['time'].time()
			# 		att_date = args['time'].date()
			# 		ec.time = att_time
			# 		ec.date = att_date
			# 		# bff = frappe.get_value("Meal Type",{'name':"Breakfast"},['from_time'])
			# 		# bft = frappe.get_value("Meal Type",{'name':"Breakfast"},['to_time'])
			# 		# lf = frappe.get_value("Meal Type",{'name':"Lunch"},['from_time'])
			# 		# lt = frappe.get_value("Meal Type",{'name':"Lunch"},['to_time'])
			# 		# df = frappe.get_value("Meal Type",{'name':"Dinner"},['from_time'])
			# 		# dt = frappe.get_value("Meal Type",{'name':"Dinner"},['to_time'])
			# 		# sf = frappe.get_value("Meal Type",{'name':"Supper"},['from_time'])
			# 		# st = frappe.get_value("Meal Type",{'name':"Supper"},['to_time'])
			# 		# min_bf = datetime.strptime('06:00', '%H:%M').time()
			# 		# max_bf = datetime.strptime('13:00', '%H:%M').time()
			# 		# min_lu = datetime.strptime('13:00', '%H:%M').time()
			# 		# max_lu = datetime.strptime('18:30', '%H:%M').time()
			# 		# min_di = datetime.strptime('00:01', '%H:%M').time()
			# 		# max_di = datetime.strptime('03:00', '%H:%M').time()
			# 		# min_su = datetime.strptime('06:00', '%H:%M').time()
			# 		# max_su = datetime.strptime('10:00', '%H:%M').time()
			# 		# if bff >= att_time >= bft:
			# 		# 	ec.meal_type = "Breakfast"
			# 		# elif lf >= att_time >= lt:
			# 		# 	ec.meal_type = "Lunch"
			# 		# elif df >= att_time >= dt:
			# 		# 	ec.meal_type = "Dinner"
			# 		# elif sf >= att_time >= st:
			# 		# 	ec.meal_type = "Supper"
			# 		# else:
			# 		# 	ec.meal_type = ""
			# 		ec.save(ignore_permissions=True)
			# 		frappe.db.commit()
			# 		return "Checkin Marked"
		except:
			frappe.log_error(title="checkin error",message=args)
	else:
		try:
			if args['device_id'] == 'IN 1' or args['device_id'] == 'IN 2':
				if not frappe.db.exists('Unregistered Employee Checkin',{'biometric_pin':args['employee'],'biometric_time':args['time']}):
					ec = frappe.new_doc('Unregistered Employee Checkin')
					ec.biometric_pin = args['employee']
					ec.biometric_time = args['time']
					ec.locationdevice_id = args['device_id']
					ec.log_type = 'IN'
					ec.save(ignore_permissions=True)
					frappe.db.commit()
					return "Checkin Unmarked"
			elif args['device_id'] == 'OUT 1' or args['device_id'] == 'OUT 2':
				if not frappe.db.exists('Unregistered Employee Checkin',{'biometric_pin':args['employee'],'biometric_time':args['time']}):
					ec = frappe.new_doc('Unregistered Employee Checkin')
					ec.biometric_pin = args['employee']
					ec.biometric_time = args['time']
					ec.locationdevice_id = args['device_id']
					ec.log_type = 'OUT'
					ec.save(ignore_permissions=True)
					frappe.db.commit()
					return "Checkin Unmarked"
			# elif args['device_id'] == 'C1' or args['device_id'] == 'C2':
			# 	if not frappe.db.exists('Unregistered Employee Canteen Checkin',{'biometric_pin':args['employee'],'biometric_time':args['time']}):
			# 		ec = frappe.new_doc('Unregistered Employee Canteen Checkin')
			# 		ec.biometric_pin = args['employee']
			# 		# ec.time = args['time']
			# 		ec.device_id = args['device_id']
			# 		att_time = args['time'].time()
			# 		att_date = args['time'].date()
			# 		ec.biometric_time = att_time
			# 		ec.date = att_date
			# 		# bff = frappe.get_value("Meal Type",{'name':"Breakfast"},['from_time'])
			# 		# bft = frappe.get_value("Meal Type",{'name':"Breakfast"},['to_time'])
			# 		# lf = frappe.get_value("Meal Type",{'name':"Lunch"},['from_time'])
			# 		# lt = frappe.get_value("Meal Type",{'name':"Lunch"},['to_time'])
			# 		# df = frappe.get_value("Meal Type",{'name':"Dinner"},['from_time'])
			# 		# dt = frappe.get_value("Meal Type",{'name':"Dinner"},['to_time'])
			# 		# sf = frappe.get_value("Meal Type",{'name':"Supper"},['from_time'])
			# 		# st = frappe.get_value("Meal Type",{'name':"Supper"},['to_time'])
			# 		# min_bf = datetime.strptime('06:00', '%H:%M').time()
			# 		# max_bf = datetime.strptime('13:00', '%H:%M').time()
			# 		# min_lu = datetime.strptime('13:00', '%H:%M').time()
			# 		# max_lu = datetime.strptime('18:30', '%H:%M').time()
			# 		# min_di = datetime.strptime('00:01', '%H:%M').time()
			# 		# max_di = datetime.strptime('03:00', '%H:%M').time()
			# 		# min_su = datetime.strptime('06:00', '%H:%M').time()
			# 		# max_su = datetime.strptime('10:00', '%H:%M').time()
			# 		# if bff >= att_time >= bft:
			# 		# 	ec.meal_type = "Breakfast"
			# 		# elif lf >= att_time >= lt:
			# 		# 	ec.meal_type = "Lunch"
			# 		# elif df >= att_time >= dt:
			# 		# 	ec.meal_type = "Dinner"
			# 		# elif sf >= att_time >= st:
			# 		# 	ec.meal_type = "Supper"
			# 		# else:
			# 		# 	ec.meal_type = ""
			# 		ec.save(ignore_permissions=True)
			# 		frappe.db.commit()
			# 		return "Checkin Marked"
		except:
			frappe.log_error(title="checkin error",message=args)
