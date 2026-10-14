from django.urls import path
from . import views

urlpatterns = [
    #ABOUT PAGE
    path("", views.about),
    #REGISTER/ LOGIN/LOGOUT
    path("login", views.login_page),
    path("tutor/register", views.tutor_register),
    path("tutor/login", views.tutor_login),
    path("family/register", views.family_register),
    path("family/login", views.family_login),
    path("logout", views.logout), 
    # FAMILY DASHBOARD
    path("dashboard", views.dashboard),
    path("bookings/<int:booking_id>/cancel", views.cancel_booking),
    #TUTOR PROFILE AND BOOKING 
    path("tutors/<int:tutor_id>", views.tutor_profile),
    path("book", views.book),
    #TUTOR DASHBOARD 
    path("tutor", views.tutor_dashboard),
    path("slots/create", views.create_slot),
    path("slots/<int:slot_id>/update", views.update_slot),
    path("slots/<int:slot_id>/delete", views.delete_slot),
]