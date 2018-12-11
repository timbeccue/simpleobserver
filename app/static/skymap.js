

var click_margin_px = 3;
var radius_nearby = 10; // for right click on map


function newSkyMap() {

    var data = [];

    // p is for selected location, t is for telescope location.
    function initializePointer(pointers) {
        crosshair_style = {
            width: 1,
            stroke:"#e74c3c"
        }
        var pointers = {
            "type":"FeatureCollection",
            "features":[
                {"type":"Feature",
                "id":"pointers",
                "properties": {},
                "geometry": {
                    "type":"Point"
                },
                "style": {
                    "stroke-width":"0.5",
                    "stroke":"#e74c3c"
                }}
            ]
        };
        //Celestial.clear();
        Celestial.add({type:"Point", callback: function(error, json) {
            if (error) return console.warn(error);
            var pointer_data = Celestial.getData(pointers, config.transform);
            Celestial.container.selectAll(".pointers")
                .data(pointer_data.features)
                .enter().append("path")
                .attr("class", "point")
            Celestial.redraw();
        }, redraw: function() {
            Celestial.container.selectAll(".point").each(function(d) {
                Celestial.setStyle(crosshair_style);
                var p_coords = ([Utilities.hour2degree(state.ra_selected), state.de_selected]);
                var t_coords = ([Utilities.hour2degree(state_mnt1.ra), state_mnt1.dec]);
                // Limit selectable regions to coordinates on the map with Celestial.clip().
                if (Celestial.clip(p_coords)) {
                    Celestial.Canvas.symbol()
                    .type("marker")
                    .size(420)
                    .position(Celestial.mapProjection(p_coords))(Celestial.context);
                }
                Celestial.Canvas.symbol()
                    .type("cross-circle")
                    .size(220)
                    .position(Celestial.mapProjection(t_coords))(Celestial.context);
                Celestial.context.stroke();
            });
        } });
    }

    function filterChart() {
        return true;
    }

    function updateChart(sky_object_data) {
        var pointStyle = {
            stroke: "rgba(255,0,204, 1)",
            fill: "rgba(255,0,204,0.5)",
            width: 3,
            stroke:"#ff00cc",
            fill:"#fff"
        }
        crosshair_style = {
            width: 1,
            stroke:"#e74c3c"
        }
        var custom_obj = {
               "type":"FeatureCollection",
               "features":[
                  {"type": "Feature",
                   "id":"item1",
                   "properties": {
                       "name":"obj1",
                       "mag": 2,
                       "dim": 30
                   }, "geometry":{
                       "type":"Point",
                       "coordinates": [150, 85]
                   }               },
                  {"type": "Feature",
                   "id":"item2",
                   "properties": {
                       "name":"obj2",
                       "mag": 1,
                       "dim": 40
                   }, "geometry":{
                       "type": "Point",
                       "coordinates": [50, 75]
               }
            }
            ]
        }
        //Celestial.clear();
        Celestial.add({type:"json", file:"/static/mapdata/custom_objects.json", callback: function(error,json) {
            if (error) {return console.warn(error);}

            var sky_objects = Celestial.getData(json, config.transform);

            Celestial.container.selectAll(".custom_objects")
                .data(sky_objects.features)
                .enter().append("path")
                .attr("class", "custom_obj")
            Celestial.redraw();
        }, redraw: function() {
            Celestial.container.selectAll(".custom_obj").each(function (d) {
                if (Celestial.clip(d.geometry.coordinates) && filterChart()) {
                //if (true) {
                    var pt = Celestial.mapProjection(d.geometry.coordinates),
                        type = d.properties.type;
                    //Celestial.context.fillStyle = "#fff";
                    Celestial.setStyle(pointStyle);
                    Celestial.map(d)
                    Celestial.context.beginPath();
                    Celestial.context.arc(pt[0], pt[1], 5, 0, 2 * Math.PI);
                    Celestial.context.closePath();
                    //Celestial.context.fill();
                    Celestial.context.stroke();
                }
            });
        }});
    }

    function mapresize() {
        let width = $('#view-size-helper').width();
        let height = $('#view-size-helper').height();
        let dim = width < height ? width:height;
        let marginleft = 0, margintop = 0;
        if (width < height) {
            margintop = (height - width) / 2;
        } else {
            marginleft = (width - height) / 2;
        }
        // map resize takes a single dimention (width) and creates a square canvas
        $('#celestial-map').css({"margin-left": ""+marginleft.toString() + "px"});
        $('#celestial-map').css({"margin-top": ""+margintop.toString() + "px"});
        Celestial.resize({ width: dim });
    }

    /* NOTE: lat-lon temporary fix with hardcoded value. Get these from state. */
    var lat = 34;//$('#static-state').data('lat');
    var lon = -119;//$('#static-state').data('lon');

    var config = {
        width: 0,     // Default width, 0 = full parent width; height is determined by projection
        projection: "stereographic",  // Map projection used: airy, aitoff, armadillo, august, azimuthalEqualArea, azimuthalEquidistant, baker, berghaus, boggs, bonne, bromley, collignon, craig, craster, cylindricalEqualArea, cylindricalStereographic, eckert1, eckert2, eckert3, eckert4, eckert5, eckert6, eisenlohr, equirectangular, fahey, foucaut, ginzburg4, ginzburg5, ginzburg6, ginzburg8, ginzburg9, gringorten, hammer, hatano, healpix, hill, homolosine, kavrayskiy7, lagrange, larrivee, laskowski, loximuthal, mercator, miller, mollweide, mtFlatPolarParabolic, mtFlatPolarQuartic, mtFlatPolarSinusoidal, naturalEarth, nellHammer, orthographic, patterson, polyconic, rectangularPolyconic, robinson, sinusoidal, stereographic, times, twoPointEquidistant, vanDerGrinten, vanDerGrinten2, vanDerGrinten3, vanDerGrinten4, wagner4, wagner6, wagner7, wiechel, winkel3
        transform: "equatorial", // Coordinate transformation: equatorial (default), ecliptic, galactic, supergalactic
        center: [Utilities.hour2degree(Utilities.siderealTime()), lat, 0],       // Initial center coordinates in equatorial transformation [hours, degrees, degrees],
                            // otherwise [degrees, degrees, degrees], 3rd parameter is orientation, null = default center
        follow: "center",   // on which coordinates to center the map, default: zenith, if location enabled, otherwise center

        orientationfixed: true,  // Keep orientation angle the same as center[2]
        geopos: [lat, lon],    // optional initial geographic position [lat,lon] in degrees, overrides center

        background: { fill: "#090909", stroke: " #090909", opacity: .5 }, // Background style
        adaptable: true,    // Sizes are increased with higher zoom-levels
        interactive: false, // Enable zooming and rotation with mousewheel and dragging
        form: false,        // Display settings form
        location: true,    // Display location settings
        controls: true,     // Display zoom controls
        lang: "",           // Language for names, so far only for constellations: de: german, es: spanish
                            // Default:en or empty string for english
        container: "celestial-map",   // ID of parent element, e.g. div
        datapath: "static/mapdata",  // Path/URL to data files, empty = subfolder 'data'
        stars: {
            show: true,    // Show stars
            limit: 3,      // Show only stars brighter than limit magnitude
            colors: true,  // Show stars in spectral colors, if not use "color"
            style: { fill: "#ffffff", opacity: 1 }, // Default style for stars
            names: false,   // Show star names (Bayer, Flamsteed, Variable star, Gliese, whichever applies first)
            proper: true, // Show proper name (if present)
            desig: false,  // Show all names, including Draper and Hipparcos
            namelimit: 2.5,  // Show only names for stars brighter than namelimit
            namestyle: { fill: "#ddddbb", font: "9px Georgia, Times, 'Times Roman', serif", align: "left", baseline: "top" },
            propernamestyle: { fill: "#ddddbb", font: "9px Georgia, Times, 'Times Roman', serif", align: "right", baseline: "bottom" },
            propernamelimit: 1.5,  // Show proper names for stars brighter than propernamelimit
            size: 7,       // Maximum size (radius) of star circle in pixels
            exponent: -0.28, // Scale exponent for star size, larger = more linear
            data: 'stars.6.reduced.json' // Data source for stellar data
            //data: 'stars.8.json' // Alternative deeper data source for stellar data
        },
        dsos: {
            show: true,    // Show Deep Space Objects
            limit: 9,      // Show only DSOs brighter than limit magnitude
            names: true,   // Show DSO names
            desig: false,   // Show short DSO names
            namelimit: 10,  // Show only names for DSOs brighter than namelimit
            namestyle: { fill: "#cccccc", font: "9px Helvetica, Arial, serif", align: "left", baseline: "top" },
            size:   6,    // Optional seperate scale size for DSOs, null = stars.size
            exponent: 2, // Scale exponent for DSO size, larger = more non-linear
            data: 'messier.json',  // Data source for DSOs
            //data: 'dsos.6.json'  // Alternative broader data source for DSOs
            //data: 'dsos.14.json' // Alternative deeper data source for DSOs
            symbols: {  //DSO symbol styles
            gg: {shape: "circle", fill: "#ff0000"},                                 // Galaxy cluster
            g:  {shape: "ellipse", fill: "#ff0000"},                                // Generic galaxy
            s:  {shape: "ellipse", fill: "#ff0000", opacity: 0.3},                                // Spiral galaxy
            s0: {shape: "ellipse", fill: "#ff0000", opacity: 0.3},                                // Lenticular galaxy
            sd: {shape: "ellipse", fill: "#ff0000", opacity: 0.3},                                // Dwarf galaxy
            e:  {shape: "ellipse", fill: "#ff0000", opacity: 0.3},                                // Elliptical galaxy
            i:  {shape: "ellipse", fill: "#ff0000", opacity: 0.3},                                // Irregular galaxy
            oc: {shape: "circle", fill: "#ffcc00", stroke: "#ffcc00", width: 1.0},  // Open cluster
            gc: {shape: "circle", fill: "#ff9900", opacity: 0.4},                                 // Globular cluster
            en: {shape: "square", fill: "#ff00cc"},                                 // Emission nebula
            bn: {shape: "square", fill: "#ff00cc", stroke: "#ff00cc", width: 2},    // Generic bright nebula
            sfr:{shape: "square", fill: "#cc00ff", stroke: "#cc00ff", width: 2},    // Star forming region
            rn: {shape: "square", fill: "#00ooff", opacity: 0.3},                                 // Reflection nebula
            pn: {shape: "diamond", fill: "#00cccc", opacity: 0.5},                                // Planetary nebula
            snr:{shape: "diamond", fill: "#ff00cc", opacity: 0.3},                                // Supernova remnant
            dn: {shape: "square", fill: "#999999", stroke: "#999999", width: 2},    // Dark nebula grey
            pos:{shape: "marker", fill: "#cccccc", stroke: "#cccccc", width: 1.5}   // Generic marker
            }
        },
        constellations: {
            show: false,    // Show constellations
            names: false,   // Show constellation names
            desig: false,   // Show short constellation names (3 letter designations)
            namestyle: { fill:"#cccc99", align: "center", baseline: "middle", opacity:0.8,
                            font: ["bold 14px Helvetica, Arial, sans-serif",  // Different fonts for brighter &
                                                "bold 12px Helvetica, Arial, sans-serif",  // sdarker constellations
                                                        "bold 11px Helvetica, Arial, sans-serif"]},
            lines: false,   // Show constellation lines
            linestyle: { stroke: "#cccccc", width: 1, opacity: 0.6 },
            bounds: false,  // Show constellation boundaries
            boundstyle: { stroke: "#cccc00", width: 0.5, opacity: 0.8, dash: [2, 4] }
        },
        planets: {
            show: true,
            which: ["sol", "mer", "ven", "ter", "lun", "mar", "jup", "sat", "ura", "nep"],
            // Font styles for planetary symbols
            style: { fill: "#00ccff", font: "bold 17px 'Lucida Sans Unicode', Consolas, sans-serif",
                    align: "center", baseline: "middle" },
            symbols: {  // Character and color for each symbol in 'which', simple circle \u25cf
            "sol": {symbol: "\u2609", fill: "#ffff00"},
            "mer": {symbol: "\u263f", fill: "#cccccc"},
            "ven": {symbol: "\u2640", fill: "#eeeecc"},
            "ter": {symbol: "\u2295", fill: "#00ffff"},
            "lun": {symbol: "\u25cf", fill: "#ffffff"}, // overridden by generated cresent
            "mar": {symbol: "\u2642", fill: "#ff9999"},
            "cer": {symbol: "\u26b3", fill: "#cccccc"},
            "ves": {symbol: "\u26b6", fill: "#cccccc"},
            "jup": {symbol: "\u2643", fill: "#ff9966"},
            "sat": {symbol: "\u2644", fill: "#ffcc66"},
            "ura": {symbol: "\u2645", fill: "#66ccff"},
            "nep": {symbol: "\u2646", fill: "#6666ff"},
            "plu": {symbol: "\u2647", fill: "#aaaaaa"},
            "eri": {symbol: "\u25cf", fill: "#eeeeee"}
            }
        },
        mw: {
            show: true,    // Show Milky Way as filled polygons
            style: { fill: "#ffffff", opacity: "0.15" }
        },
        lines: {
            graticule: { show: true, stroke: "#cccccc", width: 0.3, opacity: 0.8,      // Show graticule lines
                    // grid values: "outline", "center", or [lat,...] specific position
            lon: {pos: ["center"], fill: "#aaa", font: "10px Helvetica, Arial, sans-serif"},
                    // grid values: "outline", "center", or [lon,...] specific position
                lat: {pos: ["center"], fill: "#aaa", font: "10px Helvetica, Arial, sans-serif"}},
            equatorial: { show: true, stroke: "#aaaaaa", width: 1.3, opacity: 0.7 },    // Show equatorial plane
            ecliptic: { show: true, stroke: "#66cc66", width: 1.3, opacity: 0.7 },      // Show ecliptic plane
            galactic: { show: false, stroke: "#cc6666", width: 1.3, opacity: 0.7 },     // Show galactic plane
            supergalactic: { show: false, stroke: "#cc66cc", width: 1.3, opacity: 0.7 } // Show supergalactic plane
            //mars: { show: false, stroke:"#cc0000", width:1.3, opacity:.7 }
        },
        horizon: {  //Show horizon marker, if geo-position and date-time is set
            show: false,
            stroke: "#000099", // Line
            width: 1.0,
            fill: "#000000", // Area below horizon
            opacity: 0.5
        },
        daylight: {  // Show daylight marker (tbi)
            show: false,
            fill: "#fff",
            opacity: 0.4
            }
        };

    function update_pointer(ra, de) {
        initializePointer();
        Celestial.redraw();
    }

    function draw_custom_stuff() {
        updateChart();
        Celestial.redraw();
    }

    function map_click(mouse, leftorright) {

        function mouse_to_eq(mouse) {
            var eq = Celestial.mapProjection.invert(mouse);
            eq[0] = eq[0] * 24 / 360;
            if (eq[0] < 0) { eq[0] += 24; }
            return eq;
        }

        var mouse_eq = mouse_to_eq(mouse);

        if (leftorright == 'left') {
            UI.target_clicked(mouse_eq[0], mouse_eq[1]);
            update_pointer();
        }

        if (leftorright == 'right') {
            draw_custom_stuff();
            // get broad list of targets near click
            // get narrower list of targets near click
            // create list of close objects with xy coordinates
        }
    }


    function bestMatch(mouse) {
        var distance, candidate;
        var best = [Number.NEGATIVE_INFINITY,0];
        // Clear current table selection.
        table.rows().deselect();

        // Evaluate all nearby stars, looking for best match
        for (var j = 0; j < is_right_click.length; j++) {
            candidate = is_right_click[j];
            distance = Utilities.xydistance(candidate[6], mouse);
            // calculate score; keep track of best.
            var score = getScore(distance, candidate[1]);
            best = (best[0] > score ? best : [score,candidate[0]]);
        }
        if (best[1]==0) {
            console.log('no best match found');
            return;
        }
        var match = table.row('#' + best[1]).select().data();
        UI.target_clicked(match[2], match[3]);

        function getScore(distance, magnitude) {
            var a, b, c;
            a = 2;
            b = 3.5;
            c = 1.5;
            return 1 / (a *(Math.pow(magnitude+2,b)) * (Math.pow(distance, c)));
        }
    }

    /* Initialize the map */
    $('#views').ready( function() {
        initializePointer();
        updateChart();
        Celestial.display(config);
        mapresize();
        $(window).resize(function(){
            mapresize();
        });
    });

    // Periodically update map rotation.
    //setInterval(function() { Celestial.rotate({center: [Utilities.hour2degree(state_mnt1.tel_sid_time), lat, 0]}); }, 5000);

    data.bestMatch = bestMatch;
    data.update_pointer = update_pointer;
    data.map_click = map_click;
    data.config = config;
    data.updateChart = updateChart;
    return data;
}

var SkyMap = newSkyMap();
