// static/js/gallery.js
'use strict';

const preview      = document.getElementById('preview');
const previewBox   = document.querySelector('#preview .preview-box');
let mediaList = [];
let currentIndex = 0;

function populateMediaList() {
  mediaList = Array.from(document.querySelectorAll('img.clickable[data-full]'))
    .map(el => ({
      src: el.dataset.full,
      type: el.dataset.type || 'image'
    }));
}

function openPreviewAt(index) {
  currentIndex = (index + mediaList.length) % mediaList.length;
  showPreview();
  preview.style.display = 'flex';
}

function showPreview() {
  previewBox.innerHTML = '';
  const { src, type } = mediaList[currentIndex];
  let content;
  if (type === 'video') {
    content = document.createElement('video');
    content.src = src;
    content.controls = true;
    content.autoplay = true;
    content.playsInline = true;
  } else {
    content = document.createElement('img');
    content.src = src;
    content.alt = '';
  }
  content.className = 'preview-content';
  previewBox.appendChild(content);
}

function navigate(offset) {
  openPreviewAt(currentIndex + offset);
}

function closePreview() {
  preview.style.display = 'none';
  previewBox.innerHTML = '';
}

function handleError(imgElement) {
  const fallbackUrl = imgElement.dataset.full;
  const filename = fallbackUrl.split('/').pop();
  const link = document.createElement('a');
  link.href = fallbackUrl;
  link.textContent = filename;
  link.target = '_blank';
  imgElement.parentNode.replaceChild(link, imgElement);
}

document.addEventListener('DOMContentLoaded', () => {
  populateMediaList();
  document.querySelectorAll('img.clickable[data-full]').forEach((img, idx) => {
    img.addEventListener('click', () => openPreviewAt(idx));
  });
});

document.addEventListener('keydown', (e) => {
  if (preview.style.display === 'flex') {
    if (e.key === 'Escape') {
      closePreview();
    } else if (e.key === 'ArrowRight') {
      navigate(1);
    } else if (e.key === 'ArrowLeft') {
      navigate(-1);
    }
  }
});
