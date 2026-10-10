from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import date
import bcrypt
from .models import Student, Tutor, Slot, GRADE_CHOICES

#these are helper for access control 
def get_logged_student(request):
    if 'student_id' in request.session:
        return Student.objects.filter(id=request.session['student_id']).first()
    return None 
def get_logged_tutor(request): 
    if 'tutor_id' in request.session:
        return Tutor.objects.filter(id=request.session['tutor_id']).first()
    return None 
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())

#landing page, register, and login for both students and tutors
def index(request):
    if get_logged_student(request):
        return redirect('/dashboard')
    if get_logged_tutor(request):
        return redirect('/tutor/availability')
    # The avaiable slots that nobody has booked yet
    today_slots = Slot.objects.filter(date=date.today()).exclude(bookings__status='booked')[:3]

    context={
        'grades': GRADE_CHOICES,
        'today_slots': today_slots,
        'tab': request.GET.get('tab', 'family'),
    }
    return render(request, 'index.html', context)

def student_register(request):
    if request.method !='POST':
        return redirect('/')
    errors=Student.objects.register_validator(request.POST)
    if errors:
        for message in errors.values():
            messages.error(request, message, extra_tags='family_register')
        return redirect ('/?tab=family')
    student=Student.objects.create(
        parent_name=request.POST['parent_name'].strip(),
        student_name=request.POST['student_name'].strip(),
        grade=request.POST['grade'],
        phone=request.POST['phone'],
        email=request.POST['email'].lower(),
        password=hash_password(request.POST['password']),
    )
    request.session.flush()
    request.session['student_id']=student.id
    return redirect('/dashboard')

def student_login(request):
    if request.method !='POST':
        return redirect('/')
    student=Student.objects.filter(email=request.POST['email'].lower()).first()
    if student and check_password(request.POST['password'], student.password):
        request.session.flush()
        request.session['student_id']=student.id
        return redirect('/dashboard')
    messages.error(request,"Invalid email or password", extra_tags='family_login')
    return redirect('/?tab=family')

def tutor_register(request):
    if request.method !='POST':
        return redirect('/')
    errors=Tutor.objects.register_validator(request.POST)
    if errors:
        for message in errors.values():
            messages.error(request, message, extra_tags='tutor_register')
        return redirect('/?tab=tutor')
    tutor=Tutor.objects.create(
        full_name=request.POST['full_name'].strip(),
        subjects=request.POST['subjects'].strip(),
        grades=request.POST['grades'].strip(),
        bio=request.POST['bio'].strip(),
        price=request.POST['price'],
        email=request.POST['email'].lower(),
        password=hash_password(request.POST['password']),
    )
    request.session.flush()
    request.session['tutor_id']=tutor.id
    return redirect('/tutor/availability')

def tutor_login(request):
    if request.method !='POST':
        return redirect('/')
    tutor=Tutor.objects.filter(email=request.POST['email'].lower()).first()
    if tutor and check_password(request.POST['password'], tutor.password):
        request.session.flush()
        request.session['tutor_id'] = tutor.id
        return redirect('/tutor/availability')
    messages.error(request, "Invalid email or password.", extra_tags='tutor_login')
    return redirect('/?tab=tutor')

def logout(request):
    request.session.flush()
    return redirect('/')

#about us page 
def about(request):
    context={
        'student': get_logged_student(request),
        'tutor': get_logged_tutor(request),
    }
    return render(request, 'about.html', context)

#dashboard
def student_dashboard(request):
    student=get_logged_student(request)
    if not student:
        return redirect('/')
    return render(request,'dashboard.html', {'student': student})

def tutor_availability(request):
    tutor = get_logged_tutor(request)
    if not tutor:
        return redirect('/')
    return render(request, 'tutor_availability.html', {'tutor': tutor})