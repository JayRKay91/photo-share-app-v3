'use strict';

// Helper to submit hidden forms by ID
function submitForm(formId) {
  const form = document.getElementById(formId);
  if (form) {
    form.submit();
  }
}

// Open the preview overlay with image or video
function openPreview(src, isVideo = false) {
  const preview = document.getElementById('preview');
  preview.innerHTML = '';            // clear out any previous content
  preview.style.display = 'flex';    // show the overlay

  const box = document.createElement('div');
  box.className = 'preview-box';
  box.addEventListener('click', e => e.stopPropagation());  // don’t close when clicking inside box

  let content;
  if (isVideo) {
    content = document.createElement('video');
    content.src = src;
    content.controls = true;
    content.autoplay = true;
  } else {
    content = document.createElement('img');
    content.src = src;
  }
  content.className = 'preview-content';

  const closeBtn = document.createElement('button');
  closeBtn.className = 'close-btn';
  closeBtn.textContent = 'X';
  closeBtn.addEventListener('click', closePreview);

  box.appendChild(content);
  box.appendChild(closeBtn);
  preview.appendChild(box);
}

// Close the preview overlay
function closePreview() {
  const preview = document.getElementById('preview');
  preview.style.display = 'none';
  preview.innerHTML = '';
}

// Replace broken thumbnails with a download link
function handleError(imgElement) {
  const fallbackUrl = imgElement.dataset.full;
  const filename = fallbackUrl.split('/').pop();
  const link = document.createElement('a');
  link.href = fallbackUrl;
  link.textContent = filename;
  link.target = '_blank';
  imgElement.parentNode.replaceChild(link, imgElement);
}

// Attach click handlers to all thumbnails once DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('img[data-full]').forEach(img => {
    img.classList.add('clickable');
    img.addEventListener('click', () => {
      const src = img.dataset.full;
      const isVideo = img.dataset.type === 'video';
      openPreview(src, isVideo);
    });
  });
});

// Close preview on Escape key
document.addEventListener('keydown', event => {
  if (event.key === 'Escape') {
    closePreview();
  }
});
