from django.contrib import admin
from django.urls import path
from django.db import connection
from django.http import HttpResponse
@admin.register()
def db_info_view(request):
    db_settings = connection.settings_dict
    info = f"ENGINE: {db_settings['ENGINE']}<br>NAME: {db_settings['NAME']}<br>HOST: {db_settings['HOST']}<br>USER: {db_settings['USER']}"
    return HttpResponse(info)

class MyAdminSite(admin.AdminSite):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('db-info/', self.admin_view(db_info_view), name="db-info"),
        ]
        return custom_urls + urls

