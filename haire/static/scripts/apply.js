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

      form.addEventListener('submit', (e) => {
        e.preventDefault();
        if (stageEnded) return;
        stageEnded = true;

        if (stageEnd) {
          stageEnd.classList.remove('hidden');
        }
        if (main) {
          main.classList.add('ended');
        }
      });
    }
  });
});
