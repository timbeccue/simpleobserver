
/* Useful general functions */

function newUtilities() {
    util = [];
    function siderealTime() {
        /* Local Sidereal Time with reference to J2000
        *
        * Equations courtesy of www.stargazing.net/kepler/altaz.html 
        * and www.aberdeenastro.org.uk/sidereal_time.htm

        *  LST = 100.46 + 0.985647 * d + lon + 15*UT
        *
        *       d    is the days from J2000, including the fraction of a day
        *       UT   is the universal time in decimal hours
        *       lon is your longitude in decimal degrees, East positive.
        */

        var lmst, lon;
        var today_date;
        var epoch_date;
        var today_time;
        var epoch_time;
        var milli_since_epoch;
        var d, h, m, s;
        var UT;

        if (typeof(state) === 'undefined') {
            lon = parseFloat(document.getElementById('static-state').dataset.lon);
        } else {
            lon = parseFloat(state.lon);
        }

        // Calculate days since J2000
        today_date = new Date();
        epoch_date = new Date(2000,00,01,12,00,00);
        
        today_time = today_date.getTime();
        epoch_time = epoch_date.getTime();

        milli_since_epoch = today_time-epoch_time;
        d = milli_since_epoch/86400000;

        // Calculate UT: universal time in decimal hours
        h = today_date.getUTCHours();
        m = today_date.getUTCMinutes();
        s = today_date.getUTCSeconds();
        UT = h + m/60 + s/3600;

        // Local Sidereal Time:
        lmst = ((100.46 + 0.985647*d + lon + 15*UT) % 360) / 15;

        return lmst;
    }
    function hour2degree(ra) {
        return ra > 12? (ra - 24) * 15 : ra * 15;
    }
    function xydistance(a,b) {
        var x1,x2,y1,y2;
        x1 = a[0];
        x2 = b[0];
        y1 = a[1];
        y2 = b[1];
        return Math.sqrt(Math.pow((x2-x1), 2) + Math.pow((y2-y1), 2));
    }
    util.siderealTime = siderealTime;
    util.hour2degree = hour2degree;
    util.xydistance = xydistance;
    return util;
}

var Utilities = newUtilities();



