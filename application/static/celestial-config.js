




// NO LONGER USED - see skymap.js










/* D3-Celestial sky map
   Copyright 2015 Olaf Frohn https://github.com/ofrohn, see LICENSE

   Edit configuration to your liking and display in browser.
   Data files in folder data for stars and DSOs, number indicates limit magnitude,
   or roll your own with the format template in templ.json
*/

var config = {
  width: 0,     // Default width, 0 = full parent width; height is determined by projection
  projection: "stereographic",  // Map projection used: airy, aitoff, armadillo, august, azimuthalEqualArea, azimuthalEquidistant, baker, berghaus, boggs, bonne, bromley, collignon, craig, craster, cylindricalEqualArea, cylindricalStereographic, eckert1, eckert2, eckert3, eckert4, eckert5, eckert6, eisenlohr, equirectangular, fahey, foucaut, ginzburg4, ginzburg5, ginzburg6, ginzburg8, ginzburg9, gringorten, hammer, hatano, healpix, hill, homolosine, kavrayskiy7, lagrange, larrivee, laskowski, loximuthal, mercator, miller, mollweide, mtFlatPolarParabolic, mtFlatPolarQuartic, mtFlatPolarSinusoidal, naturalEarth, nellHammer, orthographic, patterson, polyconic, rectangularPolyconic, robinson, sinusoidal, stereographic, times, twoPointEquidistant, vanDerGrinten, vanDerGrinten2, vanDerGrinten3, vanDerGrinten4, wagner4, wagner6, wagner7, wiechel, winkel3
  transform: "equatorial", // Coordinate transformation: equatorial (default), ecliptic, galactic, supergalactic
  center: [hour2degree(lmst),lat,0],       // Initial center coordinates in equatorial transformation [hours, degrees, degrees],
                      // otherwise [degrees, degrees, degrees], 3rd parameter is orientation, null = default center
  follow: "center",   // on which coordinates to center the map, default: zenith, if location enabled, otherwise center

  orientationfixed: true,  // Keep orientation angle the same as center[2]
  geopos: [lat, lon],    // optional initial geographic position [lat,lon] in degrees, overrides center

  background: { fill: "#090909", stroke: " #090909", opacity: 1 }, // Background style
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
    limit: 5,      // Show only stars brighter than limit magnitude
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
    data: 'stars.8.json' // Data source for stellar data
    //data: 'stars.8.json' // Alternative deeper data source for stellar data
  },
  dsos: {
    show: true,    // Show Deep Space Objects
    limit: 20,      // Show only DSOs brighter than limit magnitude
    names: true,   // Show DSO names
    desig: false,   // Show short DSO names
    namelimit: 20,  // Show only names for DSOs brighter than namelimit
    namestyle: { fill: "#cccccc", font: "9px Helvetica, Arial, serif", align: "left", baseline: "top" },
    size: 9,    // Optional seperate scale size for DSOs, null = stars.size
    exponent: 1.7, // Scale exponent for DSO size, larger = more non-linear
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

Celestial.display(config);
