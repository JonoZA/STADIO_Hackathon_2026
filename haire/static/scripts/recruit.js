document.addEventListener("DOMContentLoaded", function () {
    // 1. INFO BUTTON TOGGLE
    const infoButtons = document.querySelectorAll(".more-info-button");

    infoButtons.forEach(button => {
        button.addEventListener("click", function () {
            const information = this.nextElementSibling;
            const isShown = information.classList.toggle("show");

            if (isShown) {
                this.textContent = "View Less Info";
                this.setAttribute("aria-expanded", "true");
            } else {
                this.textContent = "View More Info";
                this.setAttribute("aria-expanded", "false");
            }
        });
    });

    // 2. RADIO BUTTON DESELECT / TOGGLE LOGIC
    const radioButtons = document.querySelectorAll('input[type="radio"][name="application"]');

    radioButtons.forEach(radio => {
        radio.addEventListener("click", function () {
            if (this.dataset.wasChecked === "true") {
                this.checked = false;
                this.dataset.wasChecked = "false";
            } else {
                radioButtons.forEach(otherRadio => {
                    otherRadio.dataset.wasChecked = "false";
                });
                this.dataset.wasChecked = "true";
            }
        });
    });

    // 3. CLEAR BUTTON LOGIC
    const clearBtn = document.getElementById("clear-button");
    if (clearBtn) {
        clearBtn.addEventListener("click", function () {
            radioButtons.forEach(radio => {
                radio.checked = false;
                radio.dataset.wasChecked = "false";
            });
        });
    }

    // 4. APPROVAL MODAL LOGIC
    const approveBtn = document.getElementById("approve-button");
    const modalOverlay = document.getElementById("approval-modal");
    const modalCloseX = document.getElementById("modal-close-x");
    const modalCancelBtn = document.getElementById("modal-cancel-btn");
    const modalConfirmBtn = document.getElementById("modal-confirm-btn");
    const modalDoneBtn = document.getElementById("modal-done-btn");
    const modalStep1 = document.getElementById("modal-step-1");
    const modalStep2 = document.getElementById("modal-step-2");

    function openModal() {
        if (modalStep1 && modalStep2) {
            modalStep1.style.display = "block";
            modalStep2.style.display = "none";
        }
        if (modalOverlay) {
            modalOverlay.classList.add("active");
            modalOverlay.setAttribute("aria-hidden", "false");
        }
    }

    function closeModal() {
        if (modalOverlay) {
            modalOverlay.classList.remove("active");
            modalOverlay.setAttribute("aria-hidden", "true");
        }
    }

    if (approveBtn) {
        approveBtn.addEventListener("click", function () {
            const selected = document.querySelector('input[type="radio"][name="application"]:checked');
            if (!selected) {
                alert("Please select a candidate to approve first.");
                return;
            }
            openModal();
        });
    }

    if (modalConfirmBtn) {
        modalConfirmBtn.addEventListener("click", function () {
            if (modalStep1 && modalStep2) {
                modalStep1.style.display = "none";
                modalStep2.style.display = "block";
            }
        });
    }

    if (modalCancelBtn) modalCancelBtn.addEventListener("click", closeModal);
    if (modalCloseX) modalCloseX.addEventListener("click", closeModal);
    if (modalDoneBtn) modalDoneBtn.addEventListener("click", closeModal);

    if (modalOverlay) {
        modalOverlay.addEventListener("click", function (e) {
            if (e.target === modalOverlay) {
                closeModal();
            }
        });
    }
});