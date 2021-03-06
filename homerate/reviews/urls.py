from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'house/(?P<id>\d+)$', views.house, name='house'),
    url(r'unsave/(?P<id>\d+)$', views.unsave_house, name='unsave'),
    url(r'save/(?P<id>\d+)$', views.save_house, name='save'),
    url(r'new_report/(?P<id>\d+)/$', views.new_report, name='new_report'),
    url(r'edit_report/(?P<id>\d+)/$', views.edit_report, name='edit_report'),
    url(r'unflag/(?P<id>\d+)/$', views.unflag_report, name='unflag'),
    url(r'flag/(?P<id>\d+)/$', views.flag_report, name='flag'),
    url(r'delete_report/(?P<id>\d+)/$', views.delete_report, name='delete_report'),
    url(r'check_address/(?P<encoded_addr>.*$)', views.check_house, name='check_house'),
]