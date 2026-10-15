// ---------- Second page of the website: Log in / Register ---------- 
// Which form is showing: role = "tutor" or "family", mode = "login" or "register"
let role="tutor";
let mode="login";

function pickRole(newRole){
    role=newRole;
    showForm();
}

function pickMode(newMode){
    mode=newMode;
    showForm();
}

function showForm(){
    //first we hide all forms, then show the one we want according to the selected role
    document.querySelectorAll(".auth-form").forEach(function(form){
        form.classList.add("hidden");
    });
    document.getElementById(role+"_"+mode).classList.remove("hidden");
    //then highlight the active buttons
    document.getElementById("role-tutor").classList.toggle("active", role === "tutor");
    document.getElementById("role-family").classList.toggle("active", role === "family");
    document.getElementById("tab-login").classList.toggle("active", mode === "login");
    document.getElementById("tab-register").classList.toggle("active", mode === "register");
    //change the bullet points on the left side of the page according to the selected role 
    document.getElementById("tutor-info").classList.toggle("hidden", role !== "tutor");
    document.getElementById("family-info").classList.toggle("hidden", role !== "family");
}

//only run this on the login page (other pages dont have these forms)
if (document.getElementById("tutor_login")) {
// the page tells us which form to open first (after an error it's the same form again)
    let start = document.body.dataset.open.split("_");   // "tutor_register" -> ["tutor", "register"]
    role = start[0];
    mode = start[1];
    showForm();
}

//Third page: family dashboard (AI helper with Ajax)
let aiForm = document.getElementById("ai-form");
if (aiForm) {
    aiForm.addEventListener("submit", function (event) {
        event.preventDefault();   // stop the normal submit (it would reload the page)
        document.getElementById("ai-results").innerHTML = "<p class='empty'>Looking for tutors...</p>";
        fetch("/find-tutors", { method: "POST", body: new FormData(aiForm) })
            .then(function (response) {
                return response.text();   // the view sends back HTML
            })
            .then(function (html) {
                document.getElementById("ai-results").innerHTML = html;   // show it on the page
            });
    });
}
// Fouth page:  Tutor profile & booking
// Clicking an open hour: mark it as "Your pick", remember its id in the form
function pickSlot(button) {
    // un-pick every open hour first
    document.querySelectorAll(".slot-open").forEach(function (other) {
        other.classList.remove("picked");
        other.textContent = "Open";
    });
    // pick the clicked one
    button.classList.add("picked");
    button.textContent = "Your pick";
    // put its id in the hidden input, so the form sends it to Django
    document.getElementById("slot_id").value = button.dataset.id;
    document.getElementById("pick-text").textContent = button.dataset.label;
    document.getElementById("confirm-btn").disabled = false;
}
// coming from the AI results: pick the hour that matched automatically
let params = new URLSearchParams(window.location.search);
let chosenSlot = params.get("slot");
if (chosenSlot) {
    let button = document.querySelector('.slot-open[data-id="' + chosenSlot + '"]');
    if (button) {
        pickSlot(button);
    }
}