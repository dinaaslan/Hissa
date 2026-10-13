from django.urls import path
from . import views

urlpatterns = [
    path("", views.about),
    #REGISTER/ LOGIN/LOGOUT
    path("login", views.login_page),
    path("tutor/register", views.tutor_register),
    path("tutor/login", views.tutor_login),
    path("family/register", views.family_register),
    path("family/login", views.family_login),
    path("logout", views.logout), 
    path("dashboard", views.dashboard),
    #TUTOR DASHBOARD 
    path("bookings/<int:booking_id>/cancel", views.cancel_booking),
    path("tutor", views.tutor_dashboard),
    path("slots/create", views.create_slot),
    path("slots/<int:slot_id>/update", views.update_slot),
    path("slots/<int:slot_id>/delete", views.delete_slot),
]