const infoButtons = document.querySelectorAll(".more-info-button");

infoButtons.forEach(button => {

    button.addEventListener("click", function() {

        const information = this.nextElementSibling;

        information.classList.toggle("show");

    });

});