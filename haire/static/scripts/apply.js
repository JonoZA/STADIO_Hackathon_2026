document.addEventListener('DOMContentLoaded', function () {
  const cards = document.querySelectorAll('.card');
  const main = document.querySelector('.mainListings');
  const stageEnd = document.getElementById('stage-end');
  let stageEnded = false;

  cards.forEach((card) => {
    const header = card.querySelector('.card-header');
    const form = card.querySelector('form');

    if (header) {
      header.addEventListener('click', () => {
        if (stageEnded) return;
        card.classList.toggle('expanded');
      });
    }

    if (form) {
      form.addEventListener('click', (e) => e.stopPropagation());

      form.addEventListener('submit', async (e) => {
        e.preventDefault();
        if (stageEnded) return;
        
        const submitBtn = form.querySelector('.submit-btn');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Submitting...';
        submitBtn.disabled = true;

        try {
          const formData = new FormData(form);
          const jobTitle = card.querySelector('.card-header h2').innerText;
          formData.append('job_title', jobTitle);

          const response = await fetch('/apply', {
            method: 'POST',
            body: formData
          });

          const result = await response.json();

          if (response.ok) {
            window.location.href = '/success';
          } else {
            alert('Error: ' + (result.error || 'Failed to submit'));
          }
        } catch (error) {
          console.error('Submission error:', error);
          alert('An error occurred while submitting.');
        } finally {
          submitBtn.textContent = originalText;
          submitBtn.disabled = false;
        }
      });
    }
  });
});
