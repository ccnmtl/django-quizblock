quizblock.getCookie = function(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(
                    cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
};

quizblock.getCsrfToken = function() {
    return quizblock.getCookie('csrftoken');
};

/**
 * @param {array} $list - The list of elements to save. Expected to be an
 * array of jQuery elements, e.g. $('#answers li').
 *
 * @param {string} url - The url to POST to.
 *
 * @param {string} urlopt - String to prepend to the url option
 */
quizblock.saveOrder = function($list, url, urlopt) {
    var me = this;
    var worktodo = 0;

    url += '?';
    $list.each(function(index, element) {
        worktodo = 1;
        var id = $(element).attr('id').split('-')[1];
        url += urlopt + index + '=' + id + ';';
    });

    if (worktodo === 1) {
        quizblock.$.ajax({
            type: 'POST',
            url: url,
            beforeSend: function(xhr) {
                xhr.setRequestHeader('X-CSRFToken', me.getCsrfToken());
            }
        });
    }
};
