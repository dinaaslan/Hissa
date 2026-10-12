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
    path("bookings/<int:booking_id>/cancel", views.cancel_booking),

]