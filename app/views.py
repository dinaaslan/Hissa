import bcrypt
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import Tutor, Family, Booking, Slot, CITIES, GRADES
from datetime import date, datetime, timedelta
from django.db import IntegrityError

# FIRST PAGE: renders the About page (everyone can see it)
def about(request):
    return render(request,"about.html")

#logging out function- clears session and returns to the About page 
def logout(request):
    request.session.clear()
    return redirect("/")

#SECOND PAGE: login and register according to the roles 
#if its already logged in, it will go to the right dashboard 
def login_page(request):
    if"tutor_id" in request.session:
        return redirect("/tutor")
    if "family_id" in request.session:
        return redirect("/dashboard")
    #after an error the same form is open
    open_form=request.session.pop("open_form", "tutor_login")

    form=request.session.pop("form", {})
    context={
        "open_form":open_form,
        "form":form,
        "cities":CITIES,
        "grades":GRADES,
    }
    return render(request, "login.html", context)

#error helper to put every error on the page under the right form and then go back 
def send_errors(request, errors, form_name):
    for message in errors.values():
        messages.error(request, message, extra_tags=form_name)
    request.session["open_form"] = form_name
    form={}
    for key in request.POST:
        if key not in["password", "confirm", "csrfmiddlewaretoken"]:
            form[key]=request.POST[key]
    request.session["form"]=form
    return redirect("/login")

#SECOND PAGE: Tutor login and register 
def tutor_register(request):
    if request.method != "POST":
        return redirect("/login")
    errors = Tutor.objects.register_validator(request.POST)
    if errors:
        return send_errors(request, errors, "tutor_register")
    hashed=bcrypt.hashpw(request.POST["password"].encode(), bcrypt.gensalt()).decode()
    tutor=Tutor.objects.create(
        full_name=request.POST['full_name'].strip(),
        subjects=request.POST['subjects'].strip(),
        grades=request.POST['grades'].strip(),
        city=request.POST['city'],
        bio=request.POST['bio'].strip(),
        price=int(request.POST['price']),
        email=request.POST['email'].lower(),
        password=hashed
    )
    request.session.flush()
    request.session['tutor_id']=tutor.id
    return redirect('/tutor')

def tutor_login(request):
    if request.method != "POST":
        return redirect("/login")
    tutor=Tutor.objects.filter(email=request.POST["email"].lower()).first()
    if tutor and  bcrypt.checkpw(request.POST["password"].encode(), tutor.password.encode()):
        request.session.clear()
        request.session["tutor_id"] = tutor.id
        return redirect("/tutor")
    return send_errors(request, {"login": "Wrong email or password."}, "tutor_login")

#SECOND PAGE: Family login and register 
def family_register(request):
    if request.method != "POST":
        return redirect("/login")
    errors = Family.objects.register_validator(request.POST)
    if errors:
        return send_errors(request, errors, "family_register")
    hashed=bcrypt.hashpw(request.POST["password"].encode(), bcrypt.gensalt()).decode()
    family=Family.objects.create(
        full_name=request.POST['full_name'].strip(),
        email=request.POST['email'].lower(),
        password=hashed
    )
    request.session.flush()
    request.session['family_id']=family.id
    return redirect('/dashboard')

def family_login(request):
    if request.method != "POST":
        return redirect("/login")
    family=Family.objects.filter(email=request.POST["email"].lower()).first()
    if family and  bcrypt.checkpw(request.POST["password"].encode(), family.password.encode()):
        request.session.clear()
        request.session["family_id"] = family.id
        return redirect("/dashboard")
    return send_errors(request, {"login": "Wrong email or password."}, "family_login")

#PAGE THREE: FAMILY DASHBOARD
#logged in families can see this page otherwise it will redirect to login/register
def dashboard(request):
    if "family_id" not in request.session:
        return redirect("/login")
    family=Family.objects.get(id=request.session["family_id"])
    today=date.today()
    #dropdown of subjects 
    chosen_subject=request.GET.get("subject", "")
    tutors=Tutor.objects.all()
    if chosen_subject!="":
        #__icontains means (contains this text, ignoring upper and lower case) so it matchs every tutor who has those subjects
        tutors=tutors.filter(subjects__icontains=chosen_subject)
    #city dropdown 
    chosen_city=request.GET.get("city", "")
    if chosen_city!="":
        tutors=tutors.filter(city=chosen_city)
    #counts each tutor's open hours from today onwords 
    for tutor in tutors:
        tutor.open_count=tutor.slots.filter(is_booked=False, date__gte=today).count()

    #building the dropdown list from each tutors subjects 
    all_subjects=[]
    for tutor in Tutor.objects.all():
        for subject in tutor.subjects.split(","):
            subject=subject.strip()
            if subject != "" and subject not in all_subjects:
                all_subjects.append(subject)
    all_subjects.sort()

    #the current family's bookings, soonest to latest 
    bookings=family.bookings.all().order_by("slot__date", "slot__start_time")
    context={
        "family":family,
        "tutors":tutors,
        "all_subjects":all_subjects,
        "chosen_subject":chosen_subject,
        "cities":CITIES,
        "chosen_city": chosen_city,
        "bookings":bookings,
    }
    return render(request, "dashboard.html", context)

#function to cancel the booking they made 
def cancel_booking(request, booking_id):
    if "family_id" not in request.session:
        return redirect("/login")
    if request.method != "POST":
        return redirect ("/dashboard")
    booking=Booking.objects.filter(id=booking_id).first()
    #the booking can be cancelled by the family that made the booking 
    if booking and booking.family_id == request.session["family_id"]:
        slot=booking.slot
        slot.is_booked=False 
        slot.save()
        booking.delete()
    return redirect("/dashboard")

#PAGE FOUR TUTOR PROFILE AND BOOKING
def tutor_profile(request,tutor_id):
    #only logged in families can view and book
    if "family_id" not in request.session:
        return redirect("/login")

    tutor=Tutor.objects.filter(id=tutor_id).first()
    if not tutor:
        return redirect("/dashboard")
    
    # to show what week: 0 is this week, 1 is next week etc
    week=request.GET.get("week", "0") 
    if week.isdigit():
        week=int(week)
    else:
        week=0

    #to show what day of the week
    today=date.today()
    saturday=today-timedelta(days=(today.weekday()-5)%7)
    first_day=saturday+timedelta(weeks=week)
    days=[]
    for i in range(7):
        #loops through the days from sat to fri
        days.append(first_day+timedelta(days=i))

    #then comes the tutors slots that week
    slots=tutor.slots.filter(date__gte=days[0], date__lte=days[-1])
    now=datetime.now()
    for slot in slots:
        slot.is_past=datetime.combine(slot.date, slot.start_time) <now #this is a slot that cannot be booked

    start_times=sorted(set(slot.start_time for slot in slots))
    rows=[]
    for start_time in start_times:
        cells=[]
        for day in days:
            found=None
            for slot in slots:
                if slot.date==day and slot.start_time==start_time:
                    found=slot #none is unavailable
            cells.append(found)
        rows.append ({"time": start_time, "cells": cells})
    context={
        "tutor": tutor,
        "days": days,
        "rows": rows,
        "week": week,
        "subjects": [subject.strip() for subject in tutor.subjects.split(",")],
    }
    return render(request, "tutor_profile.html", context)

def book(request):
    if "family_id" not in request.session:
        return redirect("/login")
    if request.method != "POST":
        return redirect("/dashboard")

    family=Family.objects.get(id=request.session["family_id"])
    back=f"/tutors/{request.POST['tutor_id']}?week={request.POST['week']}"
    slot=Slot.objects.filter(id=request.POST.get("slot_id", "0") or 0).first()
    if not slot:
        messages.error(request, "Please pick an open hour first")
        return redirect(back)
    if len(request.POST["note"]) >500:
        messages.error(request, "your note is too long (500 characters max)")
        return redirect(back)

    #we need to check again if someone have booked a slot a second go 
    starts_at=datetime.combine(slot.date, slot.start_time)
    if slot.is_booked or starts_at < datetime.now():
        messages.error(request, "this hour was just taken, please pick another")
        return redirect(back)
    try: 
        Booking.objects.create(slot=slot, family=family, note=request.POST["note"]. strip())
    except IntegrityError: 
        #the database only allows one booking per slot (1to1)
        messages.error(request, "this hour was just taken, please pick another")
        return redirect(back)

    slot.is_booked=True
    slot.save()
    messages.success(request, f"Booked! {slot.tutor.full_name} · {slot.date:%a %b %d} · {slot.start_time:%I:%M %p}")
    return redirect ("/dashboard")


#PAGE FIVE: TUTOR DASHBOARD 
def tutor_dashboard(request):
    # only logged-in tutors can see this page
    if "tutor_id" not in request.session:
        return redirect("/login")

    tutor = Tutor.objects.get(id=request.session["tutor_id"])

    # the subjects this tutor teaches, for the "Add a slot" dropdown
    my_subjects = []
    for subject in tutor.subjects.split(","):
        if subject.strip() != "":
            my_subjects.append(subject.strip())

    # all this tutor's slots from today on, soonest first
    slots = tutor.slots.filter(date__gte=date.today()).order_by("date", "start_time")

    # bookings for this tutor's slots (Booking -> slot -> tutor)
    bookings = Booking.objects.filter(slot__tutor=tutor).order_by("slot__date", "slot__start_time")
    #editing mode that keeps the filled slots 
    editing =None 
    if request.GET.get("edit"):
        editing=tutor.slots.filter(id=request.GET.get("edit"), is_booked=False).first()

    form=request.session.pop("old_slot", None)
    if form is None and editing:
        form={
            "date": editing.date.strftime("%Y-%m-%d"),
            "start": editing.start_time.strftime("%H:%M"),
            "end": editing.end_time.strftime("%H:%M"),
            "subject": editing.subject,
        }
    if form is None:
        form={"date": "", "start": "", "end": "", "subject": ""}
    #profile editing 
    editing_profile=request.GET.get("profile")=="edit"
    #after an error it shows what the tutor typed, otherwise their saved info
    profile_form=request.session.pop("old_profile", None)
    if profile_form is None:
        profile_form={
            "full_name":tutor.full_name,
            "subjects":tutor.subjects,
            "grades":tutor.grades,
            "city":tutor.city,
            "price":int(tutor.price),
            "bio":tutor.bio,
        }
    context = {
        "tutor": tutor,
        "my_subjects": my_subjects,
        "slots": slots,
        "bookings": bookings,
        "editing":editing,
        "form":form,
        "editing_profile":editing_profile,
        "profile_form":profile_form,
        "cities":CITIES,
        "grades":GRADES,
    }
    return render(request, "tutor_dashboard.html", context)
#TUTOR PROFILE EDIT FEATURE
def update_profile(request):
    if"tutor_id" not in request.session:
        return redirect("/login")
    if request.method !="POST":
        return redirect("/tutor")
    tutor=Tutor.objects.get(id=request.session["tutor_id"])
    errors=Tutor.objects.profile_validator(request.POST)
    if errors:
        for message in errors.values():
            messages.error(request, message, extra_tags="profile")
        #keep what the tutor typed so the form isnt reset 
        request.session["old_profile"]={
            "full_name":request.POST["full_name"],
            "subjects": request.POST["subjects"],
            "grades": request.POST["grades"],
            "city": request.POST.get("city", ""),
            "price": request.POST["price"],
            "bio": request.POST["bio"],
        }
        return redirect("/tutor?profile=edit")
    tutor.full_name=request.POST["full_name"].strip()
    tutor.subjects=request.POST["subjects"].strip()
    tutor.grades=request.POST["grades"]
    tutor.city=request.POST["city"]
    tutor.price=int(request.POST["price"])
    tutor.bio=request.POST["bio"].strip()
    tutor.save()
    messages.success(request, "Your profile was updated", extra_tags="profile")
    return redirect("/tutor")

#CREATE SLOT FEATURE
def create_slot(request):
    if "tutor_id" not in request.session:
        return redirect("/login")
    if request.method !="POST":
        return redirect("/tutor")
    tutor=Tutor.objects.get(id=request.session["tutor_id"])
    errors=Slot.objects.slot_validator(request.POST,tutor)
    if errors:
        for message in errors.values():
            messages.error(request,message)
        keep_slot_form(request)
        return redirect("/tutor")
    Slot.objects.create(
        tutor=tutor,
        date=request.POST["date"],
        start_time=request.POST["start"],
        end_time=request.POST["end"],
        subject=request.POST["subject"],
    )
    messages.success(request,"Your open hour was added")
    return redirect("/tutor")

#FEATURE TO KEEP THE FORM INFO AFTER AN ERROR
def keep_slot_form(request):
    request.session["old_slot"]={
        "date":request.POST["date"],
        "start":request.POST["start"],
        "end":request.POST["end"],
        "subject":request.POST["subject"],
    }

#UPDATE SLOT FEATURE
def update_slot(request,slot_id):
    if "tutor_id" not in request.session:
        return redirect("/login")
    if request.method !="POST":
        return redirect("/tutor")

    tutor=Tutor.objects.get(id=request.session["tutor_id"])
    #the tutor can edit their own slot and if nobody booked it yet 
    slot=tutor.slots.filter(id=slot_id, is_booked=False).first()
    if not slot:
        return redirect("/tutor")

    errors=Slot.objects.slot_validator(request.POST, tutor, slot_id)
    if errors:
        for message in errors.values():
            messages.error(request,message)
        keep_slot_form(request)
        #for staying in edit mode to fix it 
        return redirect(f"/tutor?edit={slot.id}") 
    slot.date=request.POST["date"]
    slot.start_time=request.POST["start"]
    slot.end_time=request.POST["end"]
    slot.subject=request.POST["subject"]
    slot.save()
    messages.success(request, "your open hour was updated")
    return redirect("/tutor")

#DELETE SLOT FEATURE
def delete_slot(request,slot_id):
    if "tutor_id" not in request.session:
        return redirect("/login")
    if request.method !="POST":
        return redirect("/tutor")
    slot=Slot.objects.filter(id=slot_id).first()
    #only the tutor who own and added the slot can delete it and if nobody booked it 
    if slot and slot.tutor_id==request.session["tutor_id"] and not slot.is_booked:
        slot.delete()
    return redirect("/tutor")







