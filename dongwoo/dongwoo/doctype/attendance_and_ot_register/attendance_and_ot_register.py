# Copyright (c) 2023, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import (
	DATE_FORMAT,
	add_to_date,
	getdate,
)
from dateutil.relativedelta import relativedelta

class AttendanceandOTRegister(Document):
	pass
@frappe.whitelist()
def get_end_date(start_date, frequency):
	start_date = getdate(start_date)
	frequency = frequency.lower() if frequency else "monthly"
	kwargs = (
		get_frequency_kwargs(frequency) if frequency != "bimonthly" else get_frequency_kwargs("monthly")
	)
	end_date = add_to_date(start_date, **kwargs) - relativedelta(days=1)
	if frequency == "monthly":
		return dict(end_date=end_date.strftime(DATE_FORMAT))

	else:
		return dict(end_date="")


def get_frequency_kwargs(frequency_name):
	frequency_dict = {
		"monthly": {"months": 1},
		"fortnightly": {"days": 14},
		"weekly": {"days": 7},
		"daily": {"days": 1},
	}
	return frequency_dict.get(frequency_name)
