

// AJAX form submission (works for any form with data-autosubmit in the form tag).
(function($) {
    $.fn.auto_submit = function() {
        $(this).submit(function(event) {
            event.preventDefault();
            var form = $(this);
            $.ajax({
                type: form.attr('method'),
                url: form.attr('action'),
                data: form.serialize()
            }).done(function(data) {
                if (data.requested) {
                    form.find('input:text').val('');
                    var log = $('#cmd-log');
                    var sent_cmd = data.requested;
                    var processed_cmd = JSON.stringify(data.processed);
                    if (data.live == false) {
                        is_command_live = '<span style="color: red;"> offline </span>';
                    } else {
                        is_command_live = '<span style="color: #83ff33;"> online </span>';
                    }
                    log.find('tbody').prepend( '<tr><td>'+sent_cmd+'</td><td>'+processed_cmd+'</td><td>'+is_command_live+'</td></tr>');
                }
            }).fail(function(data) {
                console.log("failure");
            });
        });
        return this;
    }
})(jQuery);

$(function() {
    $('form[data-autosubmit]').auto_submit();
});



(function($) {
    $.fn.console_submit = function() {
        $(this).submit(function(event) {
            event.preventDefault();
            var form = $(this);
            $.ajax({
                type: form.attr('method'),
                url: form.attr('action'),
                data: form.serialize()
            }).done(function(data) {
                if (data.requested) {
                    form.find('input:text').val('');
                    var log = $('#cmd-log');
                    var sent_cmd = data.requested;
                    var processed_cmd = JSON.stringify(data.processed);
                    if (data.live == false) {
                        is_command_live = '<span style="color: red;"> offline </span>';
                    } else {
                        is_command_live = '<span style="color: #83ff33;"> online </span>';
                    }
                    log.find('tbody').prepend( '<tr><td>'+sent_cmd+'</td><td>'+processed_cmd+'</td><td>'+is_command_live+'</td></tr>');
                }
            }).fail(function(data) {
                console.log("failure");
            });
        });
        return this;
    }
})(jQuery)

$(function() {
    $('form[data-consolesubmit]').console_submit();
});

$(function() {
    $('.button-command').click( click_command);
    $('.toggle-flip').change(click_command);
})

function click_command(e) {
    e.preventDefault();
    $.ajax({
        type: 'POST',
        url: '/command',
        data: {
            category: $(this).data('category'),
            command: $(this).val(),
            checked: $(this).is(':checked') || false
        },
        success: function(data) {
            if (data.requested) {
                var log = $('#cmd-log');
                var sent_cmd = data.requested;
                var processed_cmd = JSON.stringify(data.processed);
                if (data.live == false) {
                    is_command_live = '<span style="color: red;"> offline </span>';
                } else {
                    is_command_live = '<span style="color: #83ff33;"> online </span>';
                }
                log.find('tbody').prepend( '<tr><td>'+sent_cmd+'</td><td>'+processed_cmd+'</td><td>'+is_command_live+'</td></tr>');
            }
        },
        error: function(data) {
            console.log('error');
        }
    });
};

$('.login-form').click(function(e) {
    e.preventDefault()
    $.ajax({
        type: 'POST',
        url: $(this).data('route'),
        data: $('#login').serialize(),
        success: function(data) {
            console.log('login success: ',data.success);
        },
        error: function(data) {
            console.log('login failure');
        }
    });
});
