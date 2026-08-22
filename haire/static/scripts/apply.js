document.addEventListener('DOMContentLoaded', function () {

    const cards = document.querySelectorAll('.card');
    const pageWrapper = document.querySelector('.page-wrapper');
    const loader = document.getElementById('application-loader');

    let stageEnded = false;
    let submitting = false;


    cards.forEach((card) => {

        const header = card.querySelector('.card-header');
        const form = card.querySelector('form');


        /* ==========================================
           CARD EXPANSION
           ========================================== */

        if (header) {

            header.addEventListener('click', () => {

                if (stageEnded || submitting) return;

                card.classList.toggle('expanded');

            });

        }


        /* ==========================================
           FORM
           ========================================== */

        if (form) {

            form.addEventListener('click', (e) => {
                e.stopPropagation();
            });


            form.addEventListener('submit', async (e) => {

                e.preventDefault();


                /* Prevent double submission */

                if (stageEnded || submitting) return;

                submitting = true;


                /* ==========================================
                   GET ELEMENTS
                   ========================================== */

                const submitBtn = form.querySelector('.submit-btn');

                const originalText = submitBtn.innerHTML;


                /* ==========================================
                   DISABLE BUTTON
                   ========================================== */

                submitBtn.disabled = true;

                submitBtn.innerHTML = 'Submitting...';


                /* ==========================================
                   PREPARE FORM DATA
                   ========================================== */

                const formData = new FormData(form);

                const jobTitle =
                    card.querySelector('.card-header h2').innerText;

                formData.append('job_title', jobTitle);


                /* ==========================================
                   START PAGE EXIT ANIMATION
                   ========================================== */

                document.body.classList.add('is-submitting');

                pageWrapper.classList.add('submitting');


                /*
                 * Give the page a moment to fade away
                 * before showing the loader.
                 */

                await new Promise(resolve => {
                    setTimeout(resolve, 500);
                });


                /* ==========================================
                   SHOW LOADING SCREEN
                   ========================================== */

                loader.classList.add('active');


                try {

                    /* ==========================================
                       SUBMIT APPLICATION
                       ========================================== */

                    const response = await fetch('/apply', {

                        method: 'POST',

                        body: formData

                    });


                    const result = await response.json();


                    /* ==========================================
                       SUCCESS
                       ========================================== */

                    if (response.ok) {

                        /*
                         * Small delay allows the loading
                         * animation to be seen before
                         * redirecting.
                         */

                        await new Promise(resolve => {
                            setTimeout(resolve, 1800);
                        });


                        window.location.href = '/success';

                        return;

                    }


                    /* ==========================================
                       SERVER ERROR
                       ========================================== */

                    throw new Error(
                        result.error || 'Failed to submit application'
                    );


                } catch (error) {

                    console.error(
                        'Submission error:',
                        error
                    );


                    /* Hide loader */

                    loader.classList.remove('active');

                    pageWrapper.classList.remove('submitting');

                    document.body.classList.remove('is-submitting');


                    /* Restore button */

                    submitBtn.innerHTML = originalText;

                    submitBtn.disabled = false;


                    submitting = false;


                    alert(
                        error.message ||
                        'An error occurred while submitting your application.'
                    );

                }

            });

        }

    });

});