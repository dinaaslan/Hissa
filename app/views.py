from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import date, datetime, timedelta
from datetime import date
import bcrypt
from .models import Student, Tutor, Slot, GRADE_CHOICES, Booking

REPEAT_WEEKS=5

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


#TUTOR AVAILABILITY FEATURE
def get_week_start(day):
    days_since_saturday=(day.weekday()-5)%7 
    return day-timedelta(days=days_since_saturday)
def week_offset_of(day):
    return(get_week_start(day)-get_week_start(date.today())).days//7


def tutor_availability(request):
    tutor = get_logged_tutor(request)
    if not tutor:
        return redirect('/')
    try:
        week=int(request.GET.get('week', 0))
    except ValueError:
        week=0
        #week=1 shows next week and week=-1 shows olast week
    week_start=get_week_start(date.today())+timedelta(weeks=week)
    week_days=[week_start+timedelta(days=number) for number in range(6)]
    week_slots=tutor.slots.filter(date__gte=week_days[0], date__lte=week_days[-1])

    #one row for each start time and one column for each day 
    start_times=sorted(set(slot.start_time for slot in week_slots))
    rows=[]
    for start_time in start_times:
        cells=[]
        for day in week_days:
            cell=None 
            for slot in week_slots:
                if slot.date==day and slot.start_time==start_time:
                    cell=slot
            cells.append(cell)
        rows.append({'time':start_time, 'cells':cells})
    booked_count=week_slots.filter(bookings__status='booked').count()

    #the next booked session that hasn't started yet 
    next_booking=None 
    upcoming=Booking.objects.filter(slot__tutor=tutor, status='booked', slot__date__gte=date.today()).order_by('slot__date', 'slot__start_time')
    for booking in upcoming:
        if datetime.combine(booking.slot.date, booking.slot.start_time) > datetime.now():
            next_booking=booking 
            break

    context={
        'tutor': tutor,
        'week': week,
        'week_days': week_days,
        'rows': rows,
        'open_count': week_slots.count()-booked_count,
        'booked_count': booked_count,
        'next_booking': next_booking,
    }
    return render(request, 'tutor_availability.html', context)

def add_slot(request):
    tutor=get_logged_tutor(request)
    if not tutor:
        return redirect('/')
    if request.method !='POST':
        return redirect('/tutor/availability')
    errors=Slot.objects.slot_validator(request.POST, tutor)
    if errors:
        for message in errors.values():
            messages.error(request,message)
        return redirect('/tutor/availability')
    slot_date=datetime.strptime(request.POST['date'], '%Y-%m-%d').date()
    Slot.objects.create(
        tutor=tutor,
        date=slot_date,
        start_time=request.POST['start'],
        end_time=request.POST['end'],
    )
    added= 1
    #for overlapping slots 
    if'repeat' in request.POST:
        for week_number in range(1, REPEAT_WEEKS):
            next_date=slot_date+timedelta(weeks=week_number)
            next_data={'date': next_data.strftime('%Y-%m-%d'), 'start': request.POST['start'], 'end': request.POST['end']}
            if not Slot.objects.slot_validator(next_data,tutor):
                Slot.objects.create(tutor=tutor, date=next_date, start_time=request.POST['start'], end_time=request.POST['end'])
                added += 1
    if added ==1:
        messages.success(request,"Open Hour Added")
    else:
        messages.success(request,f"{added} open hours added.")
    return redirect(f'/tutor/availability?week={week_offset_of(slot_date)}')

#this function returns the slot only if it belongs to this tutor and nobody booked it
def get_tutor_open_slot(request, tutor, slot_id):
    slot=Slot.objects.filter(id=slot_id, tutor=tutor).first()
    if not slot:
        messages.error(request, "Slot not found")
        return None 
    if slot.is_booked():
        messages.error(request,"Booked slots are locked and cannot be changed")
        return None
    return slot

def edit_slot(request, slot_id):
    tutor=get_logged_tutor(request)
    if not tutor:
        return redirect('/')
    if request.method !='POST':
        return redirect ('/tutor/availability')
    slot = get_tutor_open_slot(request, tutor, slot_id)
    if not slot:
        return redirect('/tutor/availability')
    errors = Slot.objects.slot_validator(request.POST, tutor, slot_id=slot.id)
    if errors:
        for message in errors.values():
            messages.error(request,message)
        return redirect (f'/tutor/availability?week={week_offset_of(slot.date)}')
    slot.date=datetime.strptime(request.POST['date'], '%Y-%m-%d').date()
    slot.start_time=request.POST['start']
    slot.end_time=request.POST['end']
    slot.save()
    messages.success(request,"Open hour updated")
    return redirect(f'/tutor/availability?week={week_offset_of(slot.date)}')

def delete_slot(request,slot_id):
    tutor=get_logged_tutor(request)
    if not tutor:
        return redirect('/')
    if request.method !='POST':
        return redirect('/tutor/availability')
    slot = get_tutor_open_slot(request, tutor, slot_id)
    if not slot:
        return redirect('/tutor/availability')
    week=week_offset_of(slot.date)
    slot.delete()
    messages.sucess(request,"Open hour deleted")
    return redirect(f'/tutor/availability?week={week}')

