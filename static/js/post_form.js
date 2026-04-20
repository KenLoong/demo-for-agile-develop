/**
 * post_form.js – Create / Edit post form client-side validation
 *
 * Validates title length and description presence before the form is
 * submitted, displaying Bootstrap-style inline error messages.
 * Server-side validation (Flask-WTF) remains the authoritative check.
 */

(function () {
    'use strict';

    var form = document.getElementById('post-form');
    if (!form) { return; }

    var titleField = document.getElementById('post-title');
    var descField  = document.getElementById('post-description');
    var titleErr   = document.getElementById('post-title-err');
    var descErr    = document.getElementById('post-desc-err');

    function clearErrors() {
        [titleField, descField].forEach(function (el) {
            if (el) { el.classList.remove('is-invalid'); }
        });
        [titleErr, descErr].forEach(function (el) {
            if (el) {
                el.textContent = '';
                el.classList.add('d-none');
            }
        });
    }

    function showError(field, errEl, msg) {
        if (field)  { field.classList.add('is-invalid'); }
        if (errEl)  {
            errEl.textContent = msg;
            errEl.classList.remove('d-none');
        }
    }

    form.addEventListener('submit', function (ev) {
        clearErrors();
        var valid = true;

        var title = titleField ? titleField.value.trim() : '';
        if (!title) {
            showError(titleField, titleErr, 'Title is required.');
            valid = false;
        } else if (title.length > 100) {
            showError(titleField, titleErr, 'Title must be at most 100 characters.');
            valid = false;
        }

        var desc = descField ? descField.value.trim() : '';
        if (!desc) {
            showError(descField, descErr, 'Description is required.');
            valid = false;
        }

        if (!valid) { ev.preventDefault(); }
    });
}());
