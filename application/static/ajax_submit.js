

/*

all commands issued to the observatory should include a class="form-command" or "button-command". 
This should be either in a form (if there is a form), or the button that is clicked. 

A single function should be called when an object with the class "send-command" is clicked.
This function should make an ajax call and respond appropriately on success or failure. 

*/




function sendcommand(url, formdata) {
    $.ajax({
        type: 'POST', 
        url: url, 
        data: formdata 
    }).done(function(data) {

        console.log("Command recieved.");
        console.log(data);
    
        // Popup confirming the status of the requested command. 
        // Optional action button (eg. 'UNDO') in popup_data's commented lines.
        var notification = document.querySelector('.mdl-js-snackbar');
        var popup_data = {
            //actionHandler: function(event) {},
            //actionText: 'Undo',
            //timeout: 10000,
            message: data.response
            //message: "Command recieved."
        };
        notification.MaterialSnackbar.showSnackbar(popup_data);    
    }).fail(function(data) {

        console.log("Command failed.");
        
        // Popup confirming the (failed) status of the requested command.
        var notification = document.querySelector('.mdl-js-snackbar');
        notification.MaterialSnackbar.showSnackbar({ message: "Command failed." });    
    });
}

$(function() {
    $('.form-command').submit(function(e) {
        e.preventDefault();
        var form = $(this);
        var url = form.attr('action');
        var formdata = form.serialize();
        sendcommand(url, formdata);
    });
});
$(function() {
    $('.button-command').click(function(e) {
        e.preventDefault();
        var button = $(this);
        var url = '/command/'+button.data('msg');
        var formdata = { command: $(this).val() };
        sendcommand(url, formdata);
    });
});



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
                $('.validation_error').remove()
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
                if (data.errors) {
                    var error_value;
                    for (var error_name in data.errors) {
                        error_value = data.errors[error_name];
                        $('#'+error_name).after('<p class="validation_error" style="color: red;">'+error_value);
                        console.log(error_name, error_value);
                    }
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
    };
})(jQuery);

$(function() {
    $('form[data-consolesubmit]').console_submit();
});

$(function() {
    //$('.button-command').click( click_command);
    $('.toggle-flip').change(click_command);
});

function click_command(e) {
    e.preventDefault();
    $.ajax({
        type: 'POST',
        url: '/command/'+$(this).data('msg'),
        data: {
            command: $(this).val()
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
}


/* Login Form */
$('.login-form').click(function(e) {
    e.preventDefault();
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
