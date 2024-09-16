from . import __version__ as app_version

app_name = "dongwoo"
app_title = "DONGWOO"
app_publisher = "TEAMPRO"
app_description = "hrms customization for Dongwoo"
app_email = "veeramayandi.p@groupteampro.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/dongwoo/css/dongwoo.css"
# app_include_js = "/assets/dongwoo/js/dongwoo.js"

# include js, css files in header of web template
# web_include_css = "/assets/dongwoo/css/dongwoo.css"
# web_include_js = "/assets/dongwoo/js/dongwoo.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "dongwoo/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
#	"methods": "dongwoo.utils.jinja_methods",
#	"filters": "dongwoo.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "dongwoo.install.before_install"
# after_install = "dongwoo.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "dongwoo.uninstall.before_uninstall"
# after_uninstall = "dongwoo.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "dongwoo.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {
	"Salary Slip": "dongwoo.dongwoo.overrides.CustomSalarySlip",
    "Shift Assignment": "dongwoo.dongwoo.overrides.CustomShiftAssignment"
}

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "Employee":{
		"validate": ["dongwoo.custom.inactive_employee","dongwoo.custom.emp_type_order"]
        # "before_rename":"dongwoo.custom.before_rename"
	},
    "Attendance":{
		"on_submit": ["dongwoo.custom.ot_request_creation"]
        # "before_rename":"dongwoo.custom.before_rename"
	},
    "Permission":{
		"on_submit": ["dongwoo.dongwoo.doctype.permission.permission.att_permission_update"],
        "on_cancel" : ["dongwoo.dongwoo.doctype.permission.permission .att_permission_cancel"]
        # "before_rename":"dongwoo.custom.before_rename"
	},

}

# Scheduled Tasks
# ---------------

scheduler_events = {
#	"all": [
#		"dongwoo.tasks.all"
#	],
	"daily": [
		"dongwoo.dongwoo.email_reminders.send_birthday_reminders",
		"dongwoo.dongwoo.email_reminders.send_work_anniversary_reminders",
        
	],
#	"hourly": [
#		"dongwoo.tasks.hourly"
#	],
	"weekly": [
		"dongwoo.dongwoo.email_reminders.send_holidays_reminder_in_advance",
        "dongwoo.dongwoo.doctype.shift_schedule.shift_plan.shift_plan_excel",
	],
#	"monthly": [
#		"dongwoo.tasks.monthly"
#	],
"cron":{
		"*/25 * * * *" :[
			'dongwoo.mark_attendance.mark_att',
            'dongwoo.emaill_alerts1.download',
            # 'dongwoo.emaill_alerts1.create_background_job_for_attendance_Summary'
		],
        "20 09 * * *":'dongwoo.emaill_alerts1.create_background_job_for_attendance_Summary'
	}
}

# Testing
# -------

# before_tests = "dongwoo.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "dongwoo.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "dongwoo.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]


# User Data Protection
# --------------------

# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_by}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_by}",
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_3}",
#		"strict": False,
#	},
#	{
#		"doctype": "{doctype_4}"
#	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"dongwoo.auth.validate"
# ]
