from django.db import models
from datetime import date, datetime, timedelta
import re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
GRADES = ["Grades 1-6", "Grades 7-9", "Grades 10-12"]
CITIES = ["Bethlehem", "Hebron", "Jenin", "Jericho", "Jerusalem", "Nablus","Qalqilya", "Ramallah", "Salfit", "Tubas", "Tulkarm"]

class FamilyManager(models.Manager):
    def register_validator(self, post_data):
        errors = {}
        if len(post_data['full_name'].strip()) < 4:
            errors['full_name'] = "Full name must be at least 4 characters."
        if not EMAIL_REGEX.match(post_data['email']):
            errors['email'] = "Email is not valid."
        elif Family.objects.filter(email=post_data['email'].lower()).exists():
            errors['email'] = "Invalid email."
        if len(post_data['password']) < 8:
            errors['password'] = "Password must be at least 8 characters."
        if post_data['password'] != post_data['confirm']:
            errors['confirm'] = "Passwords do not match."
        return errors


class TutorManager(models.Manager):
    def profile_validator(self, post_data):
        errors = {}
        if len(post_data['full_name'].strip()) < 2:
            errors['full_name'] = "Full name must be at least 2 characters."
        if len(post_data['subjects'].strip()) < 2:
            errors['subjects'] = "Please enter the subjects you teach."
        if len(post_data['grades'].strip()) < 1:
            errors['grades'] = "Please enter the grade levels you teach."
        if post_data.get('city', '') not in CITIES:
            errors['city'] = "Please choose your city."
        if len(post_data['bio'].strip()) < 10:
            errors['bio'] = "Bio must be at least 10 characters."
        try:
            price = int(post_data['price'])
            if price <= 0:
                errors['price'] = "Price must be more than 0."
        except ValueError:
            errors['price'] = "Price must be a number."
        return errors
    #the register validator checks the same fields as profile validator by accessing it, that way the code is not repeated
    def register_validator(self, post_data):
        errors=self.profile_validator(post_data)
        if not EMAIL_REGEX.match(post_data['email']):
            errors['email'] = "Email is not valid."
        elif Tutor.objects.filter(email=post_data['email'].lower()).exists():
            errors['email'] = "Invalid email."
        if len(post_data['password']) < 8:
            errors['password'] = "Password must be at least 8 characters."
        if post_data['password'] != post_data['confirm']:
            errors['confirm'] = "Passwords do not match."
        return errors

class SlotManager(models.Manager):
    def slot_validator(self, postData, tutor, slot_id=None):
        errors = {}
        if postData['date'] == "" or postData['start'] == "" or postData['end'] == "":
            errors['empty'] = "Please choose a date, a start time and an end time."
            return errors  # stop here, we can't check times without them
        if postData['subject'].strip() == "":
            errors['subject'] = "Please choose a subject."

        # turn the text from the form into real date/time values
        date = datetime.strptime(postData['date'], "%Y-%m-%d").date()
        start = datetime.strptime(postData['start'], "%H:%M").time()
        end = datetime.strptime(postData['end'], "%H:%M").time()

        if end <= start:
            errors['time'] = "End time must be after start time."
        elif datetime.combine(date, start) < datetime.now():
            errors['past'] = "You can't add an hour in the past."
        else:
            # two slots overlap if one starts before the other one ends
            overlap = Slot.objects.filter(
                tutor=tutor, date=date, start_time__lt=end, end_time__gt=start).exclude(id=slot_id).exists()
            if overlap:
                errors['overlap'] = "This hour overlaps with one of your other slots."
        return errors

class Family(models.Model):
    full_name= models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = FamilyManager()

    def __str__(self):
        return self.full_name

class Tutor(models.Model):
    full_name = models.CharField(max_length=100)
    subjects = models.CharField(max_length=200)  
    grades = models.CharField(max_length=100)  
    city = models.CharField(max_length=50, default="")
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
    subject = models.CharField(max_length=100, default="")
    is_booked=models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects=SlotManager()

    def __str__(self):
        return f"{self.tutor} - {self.date} {self.start_time}"


class Booking(models.Model):
    slot=models.ForeignKey(Slot, related_name='bookings', on_delete=models.CASCADE)
    family=models.ForeignKey(Family, related_name='bookings', on_delete=models.CASCADE)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.family} booked {self.slot}"
