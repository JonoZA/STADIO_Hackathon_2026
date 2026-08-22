const infoButtons = document.querySelectorAll(".more-info-button");

infoButtons.forEach(button => {

    button.addEventListener("click", function() {

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

// RADIO BUTTONS

const radioButtons = document.querySelectorAll(
    'input[type="radio"][name="application"]'
);

radioButtons.forEach(radio => {

    radio.addEventListener("click", function() {

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