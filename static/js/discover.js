/**
 * discover.js – Home / Discovery page
 *
 * Handles:
 *  - Category pill click → AJAX filter via /api/filter
 *  - Sort-select change  → AJAX filter
 *  - Search form submit  → AJAX filter
 *  - Pager button click  → AJAX paginated fetch
 *  - Renders post cards and pagination controls from JSON response
 */

(function () {
    'use strict';

    var $grid   = $('#post-grid');
    var $pager  = $('#pager-wrap');

    var currentCategory = 'all';
    var currentQuery    = '';
    var currentSort     = $('#sort-select').val() || 'newest';
    var currentPage     = 1;

    /* ------------------------------------------------------------------
       Helpers
    ------------------------------------------------------------------ */

    /** Deterministic hue from a string (used for avatar colours). */
    function avatarHue(str) {
        var h = 0;
        for (var i = 0; i < str.length; i++) {
            h = str.charCodeAt(i) + ((h << 5) - h);
        }
        return Math.abs(h) % 360;
    }

    /** Safe HTML-escape via jQuery. */
    function esc(s) {
        return $('<div>').text(s == null ? '' : String(s)).html();
    }

    var categoryBadgeClass = {
        coding:   'primary',
        language: 'success',
        music:    'info',
        sports:   'warning',
        other:    'secondary'
    };

    /* ------------------------------------------------------------------
       Rendering
    ------------------------------------------------------------------ */

    function renderPosts(payload) {
        var items = payload.posts || [];
        if (!items.length) {
            $grid.html('<div class="col-12"><p class="text-muted mb-0" id="empty-hint">No posts match your filters.</p></div>');
            renderPager(payload);
            return;
        }

        var html = items.map(function (p) {
            var initial    = (p.author && p.author.charAt(0)) ? p.author.charAt(0).toUpperCase() : '?';
            var hue        = avatarHue(p.author || '');
            var badge      = categoryBadgeClass[p.category_slug] || 'secondary';
            var detailUrl  = '/post/' + p.id;
            var profileUrl = p.author_profile || ('/user/' + encodeURIComponent(p.author));
            var imgHtml    = p.image_url
                ? '<a href="' + esc(detailUrl) + '" class="d-block"><img src="' + esc(p.image_url) + '" class="w-100 object-fit-cover" alt="" style="height:140px"></a>'
                : '';

            return (
                '<div class="col-md-6 col-xl-4">' +
                    '<div class="card h-100 shadow-sm border-0 post-card overflow-hidden">' +
                        imgHtml +
                        '<div class="card-body d-flex flex-column">' +
                            '<div class="d-flex align-items-start gap-3 mb-2">' +
                                '<span class="avatar-circle flex-shrink-0" style="background:hsl(' + hue + ',55%,42%)">' + esc(initial) + '</span>' +
                                '<div class="min-w-0">' +
                                    '<span class="badge bg-' + badge + ' bg-opacity-75 mb-1">' + esc(p.category_label) + '</span>' +
                                    '<h2 class="h5 card-title text-truncate mb-1">' +
                                        '<a href="' + detailUrl + '" class="text-reset text-decoration-none">' + esc(p.title) + '</a>' +
                                    '</h2>' +
                                    '<p class="small text-muted mb-0">' +
                                        '<a href="' + profileUrl + '" class="text-muted">' + esc(p.author) + '</a> · ' + esc(p.timestamp) +
                                    '</p>' +
                                '</div>' +
                            '</div>' +
                            '<p class="card-text text-body-secondary small flex-grow-1 mb-1">' +
                                '<a href="' + detailUrl + '" class="text-body-secondary text-decoration-none">' + esc(p.snippet) + '</a>' +
                            '</p>' +
                            '<p class="small text-muted mb-0">' +
                                (p.comment_count != null ? p.comment_count : 0) + ' comments · ' +
                                (p.like_count    != null ? p.like_count    : 0) + ' likes' +
                            '</p>' +
                        '</div>' +
                    '</div>' +
                '</div>'
            );
        }).join('');

        $grid.html(html);
        renderPager(payload);
    }

    function renderPager(payload) {
        if (!payload.pages || payload.pages <= 1) {
            $pager.addClass('d-none');
            return;
        }
        $pager.removeClass('d-none');
        var parts = [];
        if (payload.has_prev) {
            parts.push('<li class="page-item"><button type="button" class="page-link" data-page="' + (payload.page - 1) + '">Previous</button></li>');
        }
        parts.push('<li class="page-item disabled"><span class="page-link">Page ' + payload.page + ' / ' + payload.pages + '</span></li>');
        if (payload.has_next) {
            parts.push('<li class="page-item"><button type="button" class="page-link" data-page="' + (payload.page + 1) + '">Next</button></li>');
        }
        $('#pager-list').html(parts.join(''));
    }

    /* ------------------------------------------------------------------
       Data fetching
    ------------------------------------------------------------------ */

    function syncCategoryPills() {
        $('#category-bar .category-pill').removeClass('active');
        $('#category-bar .category-pill').filter(function () {
            return $(this).data('category') === currentCategory;
        }).addClass('active');
    }

    function fetchPosts(page) {
        currentPage = page || 1;
        $grid.addClass('opacity-50');
        $.getJSON('/api/filter', {
            category: currentCategory,
            query:    currentQuery,
            sort:     currentSort,
            page:     currentPage
        })
            .done(renderPosts)
            .fail(function () {
                $grid.html('<div class="col-12"><div class="alert alert-danger">Could not load posts. Please try again.</div></div>');
            })
            .always(function () { $grid.removeClass('opacity-50'); });
    }

    /* ------------------------------------------------------------------
       Event listeners
    ------------------------------------------------------------------ */

    $('#category-bar').on('click', '.category-pill', function () {
        currentCategory = $(this).data('category');
        syncCategoryPills();
        fetchPosts(1);
    });

    $('#sort-select').on('change', function () {
        currentSort = $(this).val();
        fetchPosts(1);
    });

    $('#search-form').on('submit', function (e) {
        e.preventDefault();
        currentQuery = $('#search-input').val().trim();
        fetchPosts(1);
    });

    $('#pager-wrap').on('click', '.page-link[data-page]', function (e) {
        e.preventDefault();
        var p = $(this).data('page');
        if (p) { fetchPosts(p); }
    });

    /* Initialise active pill from server-rendered state */
    var $activePill = $('#category-bar .category-pill.active');
    if ($activePill.length) {
        currentCategory = $activePill.data('category') || 'all';
    }
    syncCategoryPills();
}());
