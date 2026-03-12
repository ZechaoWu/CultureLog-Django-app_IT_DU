function getReviewCsrfToken() {
  var tokenInput = document.querySelector('#review-form input[name="csrfmiddlewaretoken"]');
  return tokenInput ? tokenInput.value : '';
}

function normalizeErrors(errors) {
  if (!errors || typeof errors !== 'object') {
    return 'Please check your input and try again.';
  }

  var messages = [];
  Object.keys(errors).forEach(function (field) {
    var fieldErrors = errors[field];
    if (Array.isArray(fieldErrors)) {
      fieldErrors.forEach(function (msg) {
        messages.push(String(msg));
      });
    }
  });

  return messages.length > 0 ? messages.join(' ') : 'Please check your input and try again.';
}

document.addEventListener('DOMContentLoaded', function () {
  var form = document.getElementById('review-form');
  if (!form) {
    return;
  }

  var submitBtn = document.getElementById('review-submit-btn');
  var cancelBtn = document.getElementById('review-cancel-btn');
  var errorBox = document.getElementById('review-form-errors');
  var reviewList = document.getElementById('reviews-list');
  var reviewCount = document.getElementById('reviews-count');

  if (cancelBtn) {
    cancelBtn.addEventListener('click', function () {
      form.reset();
      if (errorBox) {
        errorBox.hidden = true;
        errorBox.textContent = '';
      }
    });
  }

  form.addEventListener('submit', async function (event) {
    event.preventDefault();

    if (errorBox) {
      errorBox.hidden = true;
      errorBox.textContent = '';
    }

    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.textContent = 'Submitting...';
    }

    try {
      var response = await fetch(form.dataset.asyncUrl || window.location.pathname, {
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          Accept: 'application/json',
          'X-CSRFToken': getReviewCsrfToken(),
        },
        credentials: 'same-origin',
        body: new FormData(form),
      });

      var payload = await response.json();

      if (response.status === 401 && payload.login_url) {
        window.location.href = payload.login_url;
        return;
      }

      if (!response.ok || !payload.ok) {
        if (errorBox) {
          errorBox.hidden = false;
          errorBox.textContent = normalizeErrors(payload.errors || payload.error);
        }
        return;
      }

      if (payload.review_html && reviewList) {
        var wrapper = document.createElement('div');
        wrapper.innerHTML = payload.review_html;
        var newReviewNode = wrapper.firstElementChild;
        if (newReviewNode) {
          reviewList.insertBefore(newReviewNode, reviewList.children[1] || null);
        }
      }

      if (typeof payload.review_count === 'number' && reviewCount) {
        reviewCount.textContent = String(payload.review_count);
      }

      form.reset();
    } catch (error) {
      if (errorBox) {
        errorBox.hidden = false;
        errorBox.textContent = 'Network error. Please try again.';
      }
    } finally {
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Submit Review';
      }
    }
  });
});
