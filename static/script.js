// ---------------- DELETE POPUP ----------------

function openDeletePopup(studentId, studentName) {

    const popup = document.getElementById("deletePopup");
    const studentNameElement =
        document.getElementById("deleteStudentName");

    const deleteForm =
        document.getElementById("deleteForm");

    if (!popup || !studentNameElement || !deleteForm) {
        return;
    }

    studentNameElement.textContent = studentName;

    deleteForm.action =
        "/delete-student/" + studentId;

    popup.classList.add("show");

    document.body.classList.add("modal-open");
}


// ---------------- CLOSE DELETE POPUP ----------------

function closeDeletePopup() {

    const popup = document.getElementById("deletePopup");

    if (!popup) {
        return;
    }

    popup.classList.remove("show");

    document.body.classList.remove("modal-open");
}


// ---------------- CLOSE POPUP WHEN CLICKING OUTSIDE ----------------

window.addEventListener("click", function(event) {

    const popup = document.getElementById("deletePopup");

    if (!popup) {
        return;
    }

    if (event.target === popup) {
        closeDeletePopup();
    }

});


// ---------------- ESC KEY ----------------

document.addEventListener("keydown", function(event) {

    if (event.key === "Escape") {
        closeDeletePopup();
    }

});
