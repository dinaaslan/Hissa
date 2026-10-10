from django.db import models
from datetime import date, datetime, timedelta
import re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
PHONE_REGEX = re.compile(r'^[0-9+ ]{9,15}$')

GRADE_CHOICES = [str(number) for number in range(1, 12)]

# This is for session cancellation: it determines how many hours before a session a family can still cancel it
CANCEL_LIMIT_HOURS = 24

class StudentManager(models.Manager):
    def register_validator(self, post_data):
        errors = {}
        if len(post_data['parent_name'].strip()) < 4:
            errors['parent_name'] = "Parent name must be at least 4 characters."
        if len(post_data['student_name'].strip()) < 4:
            errors['student_name'] = "Student name must be at least 4 characters."
        if post_data['grade'] not in GRADE_CHOICES:
            errors['grade'] = "Please choose a grade."
        if not PHONE_REGEX.match(post_data['phone']):
            errors['phone'] = "Phone number is not valid."
        if not EMAIL_REGEX.match(post_data['email']):
            errors['email'] = "Email is not valid."
        elif Student.objects.filter(email=post_data['email'].lower()).exists():
            errors['email'] = "This email is already registered."
        if len(post_data['password']) < 8:
            errors['password'] = "Password must be at least 8 characters."
        if post_data['password'] != post_data['confirm_password']:
            errors['confirm_password'] = "Passwords do not match."
        return errors


class TutorManager(models.Manager):
    def register_validator(self, post_data):
        errors = {}
        if len(post_data['full_name'].strip()) < 2:
            errors['full_name'] = "Full name must be at least 2 characters."
        if len(post_data['subjects'].strip()) < 2:
            errors['subjects'] = "Please enter the subjects you teach."
        if len(post_data['grades'].strip()) < 1:
            errors['grades'] = "Please enter the grade levels you teach."
        if len(post_data['bio'].strip()) < 10:
            errors['bio'] = "Bio must be at least 10 characters."
        try:
            price = float(post_data['price'])
            if price <= 0:
                errors['price'] = "Price must be more than 0."
        except ValueError:
            errors['price'] = "Price must be a number."
        if not EMAIL_REGEX.match(post_data['email']):
            errors['email'] = "Email is not valid."
        elif Tutor.objects.filter(email=post_data['email'].lower()).exists():
            errors['email'] = "This email is already registered."
        if len(post_data['password']) < 8:
            errors['password'] = "Password must be at least 8 characters."
        if post_data['password'] != post_data['confirm_password']:
            errors['confirm_password'] = "Passwords do not match."
        return errors

class SlotManager(models.Manager):
    def slot_validator(self, post_data, slot_id=None):
        errors={}
        try:
            slot_date=datetime.strptime(post_data['date'],'%Y-%m-%d').date()
            start = datetime.strptime(post_data['start'], '%H:%M').time()
            end = datetime.strptime(post_data['end'], '%H:%M').time()
        except ValueError:
            errors['date'] = "Please fill in the date, start and end time."
            return errors
        if slot_date<date.today():
            errors['date']="The date cannot be in the past"
        if end <= start:
            errors['end']="End time must be after start time"
            return errors
        #for handling overlapping slots 
        overlapping=Slot.objects.filter(
            tutor=tutor,
            date=slot_date,
            start_time__lt=end,
            end_time__gt=start,
        )
        if slot_id:
            overlapping=overlapping.exclude(id=slot_id)
        if overlapping.exists():
            errors['overlap']="This time overlaps an existing slot"
        return errors


class Student(models.Model):
    parent_name = models.CharField(max_length=100)
    student_name = models.CharField(max_length=100)
    grade = models.CharField(max_length=2)
    phone = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = StudentManager()

    def __str__(self):
        return f"{self.student_name} ({self.parent_name})"

class Tutor(models.Model):
    full_name = models.CharField(max_length=100)
    subjects = models.CharField(max_length=200)  
    grades = models.CharField(max_length=100)  
    bio = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = TutorManager()

    def __str__(self):
        return self.full_name

class Slot(models.Model):
    tutor=models.ForeignKey(Tutor, related_name='slots', on_delete=models.CASCADE)
    date=models.DateField()
    start_time=models.TimeField()
    end_time=models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects=SlotManager()

    class Meta: 
        ordering=['date', 'start_time']
    def active_booking(self):
        return self.bookings.filter(status='booked').first()
    def is_booked(self):
        return self.bookings.filter(status='booked').exists()
    
    def __str__(self):
        return f"{self.tutor} {self.date} {self.start_time}-{self.end_time}"

class Booking(models.Model):
    STATUS_CHOICES = [('booked', 'Booked'), ('cancelled', 'Cancelled')]
    slot=models.ForeignKey(Slot, related_name='bookings', on_delete=models.CASCADE)
    student=models.ForeignKey(Student, related_name='bookings', on_delete=models.CASCADE)
    status=models.CharField(max_length=10, choices=STATUS_CHOICES, default='booked')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def can_cancel(self):
        session_start=datetime.combine(self.slot.date, self.slot.start_time)
        return session_start - datetime.now() > timedelta(hours=CANCEL_LIMIT_HOURS)
    
    def __str__(self):
        return f"{self.student} with {self.slot}"



    