
// Create a global state variable recieved from flask server
var state = {};
var state_mnt1 = {};
var state_foc1 = {};
var state_rot1 = {};
var state_wx = {};

$(document).ready( function() {

    var old_source = new EventSource('/status/old/1');
    var mnt1_source = new EventSource('/status/mnt/1');
    var foc1_source = new EventSource('/status/foc/1');
    var rot1_source = new EventSource('/status/rot/1');
    var wx_source = new EventSource('/status/wx/1');

    old_source.onmessage = function(event){
        var sse_contents = tryParseJSON(event.data);
        if (sse_contents) {
            $.extend(state, sse_contents);
            $('#state-dome').text(state.dome);
        }
    };
    mnt1_source.onmessage = function(event){
        var sse_contents = tryParseJSON(event.data);
        if (sse_contents) {
            $.extend(state_mnt1, sse_contents);
            var telescope_action = 'unknown';
            if (state_mnt1.mnt1_connected == 'no') {
                telescope_action = 'disconnected';
            }
            if (state_mnt1.mnt1_connected == 'yes'){
                telescope_action = 'connected';
            }
            if (state_mnt1.parked == 'no') {
                telescope_action = 'unparked';
            }
            if (state_mnt1.parked == 'yes') {
                telescope_action = 'parked';
            }
            if (state_mnt1.tracking == 'yes') {
                telescope_action = 'tracking';
            }
            if (state_mnt1.slewing == 'yes') {
                telescope_action = 'slewing';
            }

            $('#state-ra').text(parseFloat(state_mnt1.ra).toFixed(2));
            $('#state-de').text(parseFloat(state_mnt1.dec).toFixed(2));
            $('#state-telescope').text(telescope_action);
            $('#state-alt').text(parseFloat(state_mnt1.alt).toFixed(3)+'\u00B0');
            $('#state-az').text(parseFloat(state_mnt1.az).toFixed(3)+'\u00B0');
            $('#state-enclosure').text(state_mnt1.enclosure_status);
            $('#state-lmst').text(parseFloat(state_mnt1.tel_sid_time).toFixed(3));
        }
    };
    foc1_source.onmessage = function(event){
        var sse_contents = tryParseJSON(event.data);
        if (sse_contents) {
            $.extend(state_foc1, sse_contents);
        }
    };
    rot1_source.onmessage = function(event){
        var sse_contents = tryParseJSON(event.data);
        if (sse_contents) {
            $.extend(state_rot1, sse_contents);
        }
    };
    wx_source.onmessage = function(event){
        var sse_contents = tryParseJSON(event.data);
        if (sse_contents) {
            $.extend(state_wx, sse_contents);
            var table = $('#weather-table')
            table.find('tr').remove();
            for (var key in state_wx) {
                var obj = state_wx[key]
                table.prepend('<tr><th>'+key+'</th><td>'+obj+'</td></tr>');
            }
        }
    };
});

function tryParseJSON (jsonString){
    try {
        var o = JSON.parse(jsonString);

        // Handle non-exception-throwing cases:
        // Neither JSON.parse(false) or JSON.parse(1234) throw errors, hence the type-checking,
        // but... JSON.parse(null) returns null, and typeof null === "object",
        // so we must check for that, too. Thankfully, null is falsey, so this suffices:
        if (o && typeof o === "object") {
            return o;
        }
    }
    catch (e) { }

    return false;
};
