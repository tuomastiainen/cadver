from django.contrib import admin

# Register your models here.

from django.contrib import admin
from django.apps import apps

app = apps.get_app_config('creocheck')

for model_name, model in app.models.items():
    admin.site.register(model)

class UploadFile(admin.ModelAdmin):
    list_display = ['fileLink']
    readonly_fields = ['fileLink']
