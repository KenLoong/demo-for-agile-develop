/**
 * post_detail.js – Post detail page
 *
 * Handles:
 *  - "I'm interested" button → POST /interest/<id>
 *  - Like toggle button      → POST /post/<id>/like
 *  - Bookmark toggle button  → POST /post/<id>/bookmark
 *  - Comment form submit     → AJAX POST, then appends new comment to DOM
 *
 * All POST endpoints are protected by a global CSRF header set up in base.html.
 */

(function () {
    'use strict';

    /* ------------------------------------------------------------------
       Interest button
    ------------------------------------------------------------------ */
    var interestBtn = document.getElementById('interest-btn');
    if (interestBtn && !interestBtn.disabled) {
        var interestCountEl = document.getElementById('interest-count-label');

        interestBtn.addEventListener('click', function () {
            if (interestBtn.disabled) { return; }
            var url = interestBtn.getAttribute('data-url');

            $.ajax({ url: url, method: 'POST' })
                .done(function () {
                    interestBtn.disabled     = true;
                    interestBtn.textContent  = 'Request sent';
                    if (interestCountEl) {
                        var n = parseInt(interestCountEl.textContent, 10);
                        interestCountEl.textContent = isNaN(n) ? '1' : String(n + 1);
                    }
                })
                .fail(function (xhr) {
                    var msg = (xhr.responseJSON && xhr.responseJSON.message)
                        ? xhr.responseJSON.message
                        : 'Something went wrong.';
                    alert(msg);
                });
        });
    }

    /* ------------------------------------------------------------------
       Like toggle
    ------------------------------------------------------------------ */
    var likeBtn = document.getElementById('like-btn');
    if (likeBtn) {
        likeBtn.addEventListener('click', function () {
            $.ajax({ url: likeBtn.getAttribute('data-url'), method: 'POST' })
                .done(function (data) {
                    if (!data.ok) { return; }
                    likeBtn.innerHTML  = data.liked ? '♥ Liked' : '♡ Like';
                    likeBtn.setAttribute('data-liked', data.liked ? 'true' : 'false');
                    var likeCountEl = document.getElementById('like-count-label');
                    if (likeCountEl) { likeCountEl.textContent = String(data.like_count); }
                })
                .fail(function (xhr) {
                    var msg = (xhr.responseJSON && xhr.responseJSON.message)
                        ? xhr.responseJSON.message
                        : 'Could not update like.';
                    alert(msg);
                });
        });
    }

    /* ------------------------------------------------------------------
       Bookmark toggle
    ------------------------------------------------------------------ */
    var bookmarkBtn = document.getElementById('bookmark-btn');
    if (bookmarkBtn) {
        bookmarkBtn.addEventListener('click', function () {
            $.ajax({ url: bookmarkBtn.getAttribute('data-url'), method: 'POST' })
                .done(function (data) {
                    if (!data.ok) { return; }
                    bookmarkBtn.textContent = data.saved ? 'Saved' : 'Save for later';
                    bookmarkBtn.setAttribute('data-saved', data.saved ? 'true' : 'false');
                })
                .fail(function (xhr) {
                    var msg = (xhr.responseJSON && xhr.responseJSON.message)
                        ? xhr.responseJSON.message
                        : 'Could not update bookmark.';
                    alert(msg);
                });
        });
    }

    /* ------------------------------------------------------------------
       Comment form (AJAX submit + DOM append)
    ------------------------------------------------------------------ */
    var commentForm  = document.getElementById('comment-form');
    if (!commentForm) { return; }

    var commentInput = document.getElementById('comment-content');
    var commentErr   = document.getElementById('comment-client-error');
    var commentList  = document.getElementById('comment-list');
    var emptyHint    = document.getElementById('comment-empty-hint');

    function showCommentError(msg) {
        if (!commentErr) { return; }
        commentErr.textContent = msg || '';
        commentErr.classList.toggle('d-none', !msg);
        if (commentInput) { commentInput.classList.toggle('is-invalid', !!msg); }
    }

    commentForm.addEventListener('submit', function (e) {
        e.preventDefault();

        var text = commentInput ? commentInput.value.trim() : '';
        if (!text) {
            showCommentError('Please enter a comment.');
            return;
        }
        showCommentError('');

        var fd = new FormData(commentForm);
        $.ajax({
            url:         commentForm.action,
            method:      'POST',
            data:        fd,
            processData: false,
            contentType: false,
            headers:     { 'X-Requested-With': 'XMLHttpRequest' }
        })
            .done(function (data) {
                if (!data.ok) { return; }

                /* Append new comment to the list */
                if (commentList) {
                    commentList.classList.remove('d-none');
                    var li = document.createElement('li');
                    li.className = 'list-group-item py-3';
                    li.innerHTML =
                        '<div class="d-flex justify-content-between align-items-baseline gap-2 mb-1">' +
                            '<strong class="small"></strong>' +
                            '<span class="small text-muted"></span>' +
                        '</div>' +
                        '<p class="mb-0 small comment-text"></p>';
                    li.querySelector('strong').textContent           = data.username;
                    li.querySelector('.text-muted').textContent      = data.timestamp;
                    li.querySelector('.comment-text').textContent    = data.content;
                    commentList.appendChild(li);
                }

                if (emptyHint) { emptyHint.classList.add('d-none'); }
                commentInput.value = '';

                /* Update comment counts in the page header and section badge */
                if (typeof data.comment_count === 'number') {
                    var headerCount  = document.getElementById('comment-count-label');
                    var sectionCount = document.getElementById('comments-section-count');
                    if (headerCount)  { headerCount.textContent  = String(data.comment_count); }
                    if (sectionCount) { sectionCount.textContent = String(data.comment_count); }
                }
            })
            .fail(function (xhr) {
                var msg = (xhr.responseJSON && xhr.responseJSON.message)
                    ? xhr.responseJSON.message
                    : 'Could not post comment.';
                showCommentError(msg);
            });
    });
}());
