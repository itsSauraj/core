from django.apps import AppConfig

class AdminPanelConfig(AppConfig):
	default_auto_field = 'django.db.models.BigAutoField'
	name = 'admin_panel'

	def ready(self):
		import admin_panel.signals
