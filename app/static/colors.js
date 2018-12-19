/* jshint esversion: 6 */
/* Defines site-wide, color themes that can be selected by the user. */


const root = document.documentElement;
const color_buttons = ''; // document.querySelectorAll('.color-button');


//color_buttons.forEach((btn) => {
    //btn.addEventListener('click', handleThemeUpdate);
//});

//var night_colors = document.getElementById("night-colors");
//night_colors.addEventListener("click", handleThemeUpdate); 

var night_colors = $('#night-colors');
night_colors.click(function() {
    if (night_colors.data('currentcolors') == "red") {
        console.log('red');
        night_colors.removeData('currentcolors');
        night_colors.removeData('currentcolors');
        night_colors.data('currentcolors', 'default');
        handleThemeUpdate("default");
    } else if (night_colors.data('currentcolors') == "default") {
        console.log('default');
        night_colors.removeData('currentcolors');
        night_colors.data('currentcolors', "red");
        handleThemeUpdate("red");
    }
});

$('#night-colors').click(handleThemeUpdate);
$('#scroll-6').click(handleThemeUpdate);

function handleThemeUpdate(theme) {
    console.log(theme);
    switch(theme) {
        case 'default': 
            root.style.setProperty('--background', '');
            root.style.setProperty('--text', '');
            root.style.setProperty('--options-color', '');
            root.style.setProperty('--menu1', '');
            root.style.setProperty('--menu2', '');
            root.style.setProperty('--menu3', '');
            root.style.setProperty('--menuborder', '');
            root.style.setProperty('--inputs', '');
            SkyMap.toggle_night_colors('default');
            break;
        case 'red': 
            root.style.setProperty('--background', '#050000');
            root.style.setProperty('--text', '#c21807');
            root.style.setProperty('--options-color', '#100808');
            root.style.setProperty('--menu1', '#000');
            root.style.setProperty('--menu2', '#000');
            root.style.setProperty('--menu3', '#000');
            root.style.setProperty('--menuborder', '#222');
            root.style.setProperty('--inputs', '#420d09');
            SkyMap.toggle_night_colors('red');
            break;
        case 'toggle': 
            console.log('in style toggle');
            root.style.setProperty('--background', '#050000');
            root.style.setProperty('--text', '#c21807');
            root.style.setProperty('--options-color', '#100808');
            root.style.setProperty('--menu1', '#000');
            root.style.setProperty('--menu2', '#000');
            root.style.setProperty('--menu3', '#000');
            root.style.setProperty('--menuborder', '#222');

            SkyMap.toggle_night_colors();
            break;
    }
}
