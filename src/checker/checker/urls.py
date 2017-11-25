"""checker URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""


from django.conf.urls import url
from django.contrib import admin
from creocheck import views
from django.conf import settings
from django.views.static import serve


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.index, {}, "index"),
    url(r'^checks_admin/$', views.checks_admin, {}, "checks_admin"),
    url(r'^checks_admin_filter/(?P<active_assignment>\d+)$', views.checks_admin_filter, {}, "checks_admin_filter"),
    url(r'^checks_admin/check/(?P<pk>\d+)$', views.admin_check_detail, {}, "admin_check_detail"),
    url(r'^checks_admin/user/(?P<pk>\d+)$', views.admin_user_detail, {}, "admin_user_detail"),
    url(r'^checks_admin/excel_export/', views.admin_excel_export, {}, "admin_excel_export"),
    url(r'^receive-file$', views.receive_file, {}, "receive_file"),
    url(r'^update_tasks/$', views.update_tasks, {}, "update_tasks"),
    url(r'^task/(?P<pk>\d+)$', views.task_detail, {}, "index"),
    url(r'^login/$', views.activate_user_collection, {}, "activate_user_collection"),
    url(r'^logout/$', views.logout, {}, "logout"),
    url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT, 'show_indexes': False}),
]
