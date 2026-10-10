const familyTab = document.getElementById("family_tab");
const tutorTab = document.getElementById("tutor_tab");
const familyForms = document.getElementById("family_forms");
const tutorForms = document.getElementById("tutor_forms");

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