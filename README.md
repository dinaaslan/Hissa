# حصة (Hissa) - Tutoring Booking App

Hissa is a web app that helps families in Palestine find a tutor and book a lesson hour. Tutors add the hours they are free, and families can see those open hours and book one in a few clicks. After a booking, both sides get each other's WhatsApp number so they can talk directly.

The main focus of the project is **availability**: a family only sees hours that are really open, so there is no back and forth to find a time that works.

## Live Demo

Coming soon (deployed on AWS)

## Features

### For everyone
- About page that explains the app, visible whether you are logged in or not

### For families
- Register and log in (separate from tutors)
- Browse tutors and filter them by **subject** and **city**
- See how many open hours each tutor has
- Open a tutor's profile and see their week as a timetable (Saturday to Friday), and move between weeks
- Book an open hour and add a short note for the tutor
- See all my bookings and cancel a booking
- WhatsApp link to the tutor after booking

### For tutors
- Register and log in (separate from families)
- Edit my profile: subjects, grade levels, city, price per hour, bio and phone number
- Add, edit and delete open hours (slots)
- See which families booked my hours, with their WhatsApp link

### AI helper
Families can write one sentence about what they need, in English or Arabic, for example:

> "Math for my son on the weekend after 4"

The app sends this sentence to Google Gemini, which picks out the subject, the days and the time. Then the app shows the open hours that match, using **AJAX** so the page does not reload.
If the AI is not available (no API key or no internet), the app uses a simple keyword search instead, so this feature always works.

### Validation and security
- Passwords are hashed with **bcrypt**
- All forms are validated (name, email, password, phone number, price, slot times)
- A tutor can't add a slot in the past or a slot that overlaps with another one
- A slot can only be booked once, and booked slots can't be edited or deleted
- Pages check the session, so families and tutors can only see and change their own data
- CSRF protection on all forms

## Technologies

- Python 3 and Django
- SQLite
- HTML, CSS and JavaScript
- AJAX (Fetch)
- bcrypt
- Google Gemini API
- AWS EC2 for deployment

## Pages

1. **About** - the first page of the site
2. **Log in / Register** - one page with tutor and family forms
3. **Family Dashboard** - tutors list, filters, AI helper and my bookings
4. **Tutor Profile** - weekly timetable and booking form
5. **Tutor Dashboard** - profile, open hours and bookings

## Database

- **Family** - full name, email, phone, password
- **Tutor** - full name, subjects, grades, city, price, bio, email, phone, password
- **Slot** - an open hour that belongs to a tutor (date, start time, end time, subject, booked or not)
- **Booking** - connects a family to a slot, with an optional note

A tutor has many slots, a family has many bookings, and each booking belongs to one slot.


## Screenshots

Coming soon

## Author

**Dina Aslan**
Solo project for the Full-Stack Developer program at Axsos Academy, 2026
GitHub: [dinaaslan](https://github.com/dinaaslan)