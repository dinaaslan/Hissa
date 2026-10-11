from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('student/register', views.student_register),
    path('student/login', views.student_login),
    path('tutor/register', views.tutor_register),
    path('tutor/login', views.tutor_login),
    path('dashboard', views.student_dashboard),
    path('tutor/availability', views.tutor_availability),
    path('logout', views.logout),
    path('about', views.about),
    path('tutor/slots/add', views.add_slot),
    path('tutor/slots/<int:slot_id>/edit', views.edit_slot),
    path('tutor/slots/<int:slot_id>/delete', views.delete_slot), 
]