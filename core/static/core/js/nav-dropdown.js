document.addEventListener('DOMContentLoaded', function () {
  var toggle = document.querySelector('.nav-dropdown-toggle');
  if (!toggle) {
    return;
  }

  var menu = toggle.nextElementSibling;
  if (!menu) {
    return;
  }

  toggle.addEventListener('click', function (event) {
    event.preventDefault();
    var open = menu.classList.toggle('open');
    toggle.setAttribute('aria-expanded', String(open));
  });

  document.addEventListener('click', function (event) {
    if (!event.target.closest('.nav-dropdown')) {
      menu.classList.remove('open');
      toggle.setAttribute('aria-expanded', 'false');
    }
  });
});
