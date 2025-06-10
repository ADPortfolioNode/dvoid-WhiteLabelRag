/**
 * style-guide-navigation.js
 * Handles the style guide navigation interaction
 */

document.addEventListener('DOMContentLoaded', function() {
  // Get all section elements
  const sections = document.querySelectorAll('.example-section');
  
  // Get all navigation links
  const navLinks = document.querySelectorAll('.style-guide-nav .nav-link');
  
  // Function to highlight active nav item based on scroll position
  function setActiveNavItem() {
    let currentActiveSection = '';
    
    sections.forEach(section => {
      const sectionTop = section.offsetTop;
      const sectionHeight = section.clientHeight;
      
      if (window.scrollY >= (sectionTop - 100)) {
        currentActiveSection = section.getAttribute('id');
      }
    });
    
    navLinks.forEach(link => {
      link.classList.remove('active');
      const href = link.getAttribute('href').substring(1);
      
      if (href === currentActiveSection) {
        link.classList.add('active');
      }
    });
  }
  
  // Add smooth scrolling to nav links
  navLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      e.preventDefault();
      
      const targetId = this.getAttribute('href').substring(1);
      const targetSection = document.getElementById(targetId);
      
      window.scrollTo({
        top: targetSection.offsetTop - 50,
        behavior: 'smooth'
      });
      
      // Update URL hash without scrolling
      history.pushState(null, null, '#' + targetId);
      
      // Set active state
      navLinks.forEach(navLink => navLink.classList.remove('active'));
      this.classList.add('active');
    });
  });
  
  // Listen for scroll events to update active nav item
  window.addEventListener('scroll', setActiveNavItem);
  
  // Initialize active nav item
  setActiveNavItem();
});
