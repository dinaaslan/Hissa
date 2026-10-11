const familyTab = document.getElementById("family_tab");
const tutorTab = document.getElementById("tutor_tab");
const familyForms = document.getElementById("family_forms");
const tutorForms = document.getElementById("tutor_forms");

if (familyTab && tutorTab) {
    familyTab.addEventListener("click", function () {
        familyTab.classList.add("active");
        tutorTab.classList.remove("active");
        familyForms.classList.remove("hidden");
        tutorForms.classList.add("hidden");
    });

    tutorTab.addEventListener("click", function () {
        tutorTab.classList.add("active");
        familyTab.classList.remove("active");
        tutorForms.classList.remove("hidden");
        familyForms.classList.add("hidden");
    });
}

//availability
var slotForm = document.getElementById('slot_form');
var formHeading = document.getElementById('form_heading');
var formButton = document.getElementById('form_button');
var cancelEdit = document.getElementById('cancel_edit');
var repeatRow = document.getElementById('repeat_row');

var selectedText = document.getElementById('selected_text');
var editButton = document.getElementById('edit_button');
var deleteButton = document.getElementById('delete_button');
var deleteForm = document.getElementById('delete_form');

var selectedSlot = null;
if (slotForm) {

// Clicking a slot selects it
var slots = document.querySelectorAll('.slot-open, .slot-booked');
for (var i = 0; i < slots.length; i++) {
    slots[i].addEventListener('click', function () {
        // Remove the highlight from the previous slot
        if (selectedSlot) {
            selectedSlot.classList.remove('slot-selected');
        }
        selectedSlot = this;
        selectedSlot.classList.add('slot-selected');

        if (this.dataset.booked === 'yes') {
            selectedText.innerHTML = '<strong>Selected:</strong> ' + this.dataset.label + ' (booked by ' + this.dataset.student + ')';
            editButton.disabled = true;
            deleteButton.disabled = true;
        } else {
            selectedText.innerHTML = '<strong>Selected:</strong> ' + this.dataset.label + ' (open)';
            editButton.disabled = false;
            deleteButton.disabled = false;
            deleteForm.action = '/tutor/slots/' + this.dataset.id + '/delete';
        }
    });
}

// Edit: fill the form with the slot's values and send it to the edit route
editButton.addEventListener('click', function () {
    if (!selectedSlot) {
        return;
    }
    slotForm.action = '/tutor/slots/' + selectedSlot.dataset.id + '/edit';
    document.getElementById('slot_date').value = selectedSlot.dataset.date;
    document.getElementById('slot_start').value = selectedSlot.dataset.start;
    document.getElementById('slot_end').value = selectedSlot.dataset.end;
    formHeading.textContent = 'Edit open hours';
    formButton.textContent = 'Save changes';
    repeatRow.classList.add('hidden');
    cancelEdit.classList.remove('hidden');
    slotForm.scrollIntoView({ behavior: 'smooth' });
});

// Cancel editing: put the form back to "Add"
cancelEdit.addEventListener('click', function () {
    slotForm.action = '/tutor/slots/add';
    slotForm.reset();
    formHeading.textContent = 'Add open hours';
    formButton.textContent = 'Add slot';
    repeatRow.classList.remove('hidden');
    cancelEdit.classList.add('hidden');
});

// Ask before deleting
deleteForm.addEventListener('submit', function (event) {
    if (!confirm('Delete this open hour?')) {
        event.preventDefault();
    }
});
}