from django.conf.urls import url
from . import views

app_name = 'usuarios'
urlpatterns = [
    url(r'^changePassword/$', views.changePassword, name='changePassword'),
]
