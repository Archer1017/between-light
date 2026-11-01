(() => {
  'use strict';
  const menu = document.querySelector('.menu-toggle');
  const nav = document.querySelector('#primary-nav');
  function closeMenu() {
    nav.classList.remove('is-open');
    menu.setAttribute('aria-expanded', 'false');
    menu.setAttribute('aria-label', 'Open navigation menu');
  }
  menu.addEventListener('click', () => {
    const open = menu.getAttribute('aria-expanded') !== 'true';
    menu.setAttribute('aria-expanded', String(open));
    menu.setAttribute('aria-label', open ? 'Close navigation menu' : 'Open navigation menu');
    nav.classList.toggle('is-open', open);
  });
  nav.addEventListener('click', (event) => {
    if (event.target.closest('a')) closeMenu();
  });
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && menu.getAttribute('aria-expanded') === 'true') {
      closeMenu();
      menu.focus();
    }
  });
  document.addEventListener('click', (event) => {
    if (!event.target.closest('.site-header')) closeMenu();
  });
  matchMedia('(min-width: 768px)').addEventListener('change', closeMenu);

  const dialog = document.querySelector('.lightbox');
  if (dialog && typeof dialog.showModal === 'function') {
    const photos = [...document.querySelectorAll('[data-photo]')];
    const image = dialog.querySelector('#lightbox-image');
    const title = dialog.querySelector('#lightbox-title');
    const note = dialog.querySelector('#lightbox-note');
    const counter = dialog.querySelector('#lightbox-counter');
    let selected = 0;
    let opener = null;
    function showPhoto(index) {
      selected = (index + photos.length) % photos.length;
      const photo = photos[selected];
      image.src = photo.href;
      image.alt = photo.querySelector('img').alt;
      title.textContent = photo.dataset.title;
      note.textContent = photo.dataset.note;
      counter.textContent = `${String(selected + 1).padStart(2, '0')} / ${String(photos.length).padStart(2, '0')}`;
    }
    photos.forEach((photo, index) => {
      photo.addEventListener('click', (event) => {
        if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
        event.preventDefault();
        opener = photo;
        showPhoto(index);
        dialog.showModal();
        document.body.classList.add('modal-open');
      });
    });
    dialog.querySelector('.lightbox-close').addEventListener('click', () => dialog.close());
    dialog.querySelector('.lightbox-prev').addEventListener('click', () => showPhoto(selected - 1));
    dialog.querySelector('.lightbox-next').addEventListener('click', () => showPhoto(selected + 1));
    dialog.addEventListener('keydown', (event) => {
      if (event.key === 'ArrowRight') { event.preventDefault(); showPhoto(selected + 1); }
      if (event.key === 'ArrowLeft') { event.preventDefault(); showPhoto(selected - 1); }
    });
    dialog.addEventListener('click', (event) => {
      const rect = dialog.getBoundingClientRect();
      if (event.target === dialog && (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom)) dialog.close();
    });
    dialog.addEventListener('close', () => {
      document.body.classList.remove('modal-open');
      opener?.focus();
    });
  }

  const copyButton = document.querySelector('[data-copy-email]');
  if (copyButton) {
    let toastTimer;
    copyButton.addEventListener('click', async () => {
      const toast = document.querySelector('.toast');
      try {
        await navigator.clipboard.writeText(copyButton.dataset.copyEmail);
        toast.textContent = 'Email address copied';
      } catch {
        toast.textContent = 'Copy unavailable. Please select and copy the email address manually.';
      }
      toast.classList.add('visible');
      clearTimeout(toastTimer);
      toastTimer = setTimeout(() => toast.classList.remove('visible'), 3200);
    });
  }
})();
