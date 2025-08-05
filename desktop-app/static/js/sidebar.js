// sidebar.js - Hover-triggered sidebar navigation title update for all pages
function updatePageTitle(link) {
  const pageTitle = link.getAttribute('data-page-title');
  const titleEl = document.querySelector('.page-title');
  if (titleEl) {
    titleEl.textContent = pageTitle || '';
  }
}

document.addEventListener('DOMContentLoaded', function() {
  const sidebarLinks = document.querySelectorAll('.sidebar .nav-link');

  sidebarLinks.forEach(function(link) {
    link.addEventListener('mouseenter', function() {
      updatePageTitle(this);
    });
    link.addEventListener('mouseleave', function() {
      updatePageTitle({ getAttribute: () => '' });
    });
  });
});
