// static/js/sidebar.js
document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.querySelector('.sidebar');
    const toggle  = document.querySelector('.sidebar-toggle');
    toggle.addEventListener('click', () => {
      sidebar.classList.toggle('collapsed');
    });
  });
  