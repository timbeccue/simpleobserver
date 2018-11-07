
// Create a global state variable recieved from flask server
var state = {};
var state_mnt1 = {};
var state_foc1 = {};
var state_rot1 = {};

$(document).ready( function() {

    var old_source = new EventSource('/status/old/1');
    var mnt1_source = new EventSource('/status/mnt/1');
    var foc1_source = new EventSource('/status/foc/1');
    var rot1_source = new EventSource('/status/rot/1');

    old_source.onmessage = function(event){
        $.extend(state, JSON.parse(event.data));
        $('#state-dome').text(state.dome);
        //$('#state-lmst').text(state.lmst);
    };
    mnt1_source.onmessage = function(event){
        $.extend(state_mnt1, JSON.parse(event.data));
        var telescope_action;
        if (state_mnt1.mnt1_connected == 'no') {
            telescope_action = 'disconnected';
        }
        else if (state_mnt1.mnt1_connected == 'yes'){
            telescope_action = 'parked';
        }
        else if (state_mnt1.slewing == 'yes') {
            telescope_action = 'slewing';
        }
        else if (state_mnt1.tracking == 'yes') {
            telescope_action = 'tracking';
        }
        else telescope_action = 'unknown';

        $('#state-ra').text(parseFloat(state_mnt1.ra).toFixed(2));
        $('#state-de').text(parseFloat(state_mnt1.dec).toFixed(2));
        $('#state-telescope').text(telescope_action);
        $('#state-alt').text(parseFloat(state_mnt1.alt).toFixed(3));
        $('#state-lmst').text(parseFloat(state_mnt1.tel_time).toFixed(3));
    };
    foc1_source.onmessage = function(event){
        $.extend(state_foc1, JSON.parse(event.data));
    };
    rot1_source.onmessage = function(event){
        $.extend(state_rot1, JSON.parse(event.data));
    };
});
