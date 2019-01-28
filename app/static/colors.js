/* jshint esversion: 6 */
/* Defines site-wide, color themes that can be selected by the user. Implements red night mode option. */


const root = document.documentElement;
const color_buttons = '';

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
            root.style.setProperty('--background', '#222');
            root.style.setProperty('--text', '#ccc');
            root.style.setProperty('--formtext', '#111');
            root.style.setProperty('--options-color', '#181818');
            root.style.setProperty('--menu1', '#0e003c');
            root.style.setProperty('--menu2', '#1d003c');
            root.style.setProperty('--menu3', '#2c003c');
            root.style.setProperty('--inputs', '#fff');
            root.style.setProperty('--header', '#282828');

            root.style.setProperty('--neutral-1', '#111');
            root.style.setProperty('--neutral-2', '#222');
            root.style.setProperty('--neutral-3', '#333');
            root.style.setProperty('--neutral-4', '#444');
            root.style.setProperty('--neutral-5', '#555');
            root.style.setProperty('--neutral-6', '#666');
            root.style.setProperty('--neutral-7', '#777');
            root.style.setProperty('--neutral-8', '#888');
            root.style.setProperty('--neutral-9', '#999');
            root.style.setProperty('--neutral-a', '#aaa');
            root.style.setProperty('--neutral-b', '#bbb');
            root.style.setProperty('--neutral-c', '#ccc');
            root.style.setProperty('--neutral-d', '#ddd');
            root.style.setProperty('--neutral-e', '#eee');
            root.style.setProperty('--neutral-f', '#fff');

            root.style.setProperty('--button-white', '#fafafa');
            root.style.setProperty('--button-white-hoverfocus', '#e6e6e6');
            root.style.setProperty('--button-white-text', '#222');
            root.style.setProperty('--button-success', '#5bb75b');
            root.style.setProperty('--button-success-hoverfocus', '#47a247');
            root.style.setProperty('--button-success-text', '#fafafa'); 

            document.getElementById("datatables-css").href = "static/css/datatables.css";
            SkyMap.toggle_night_colors('default');
            break;
        case 'red': 
            root.style.setProperty('--background', '#050000');
            root.style.setProperty('--text', '#c21807');
            root.style.setProperty('--formtext', '#c21807');
            root.style.setProperty('--options-color', '#100808');
            root.style.setProperty('--menu1', '#000');
            root.style.setProperty('--menu2', '#000');
            root.style.setProperty('--menu3', '#000');
            root.style.setProperty('--inputs', '#420d09');
            root.style.setProperty('--header', '#330000');

            root.style.setProperty('--neutral-1', '#040000');
            root.style.setProperty('--neutral-2', '#180000');
            root.style.setProperty('--neutral-3', '#2b0000');
            root.style.setProperty('--neutral-4', '#3f0000');
            root.style.setProperty('--neutral-5', '#530000');
            root.style.setProperty('--neutral-6', '#660000');
            root.style.setProperty('--neutral-7', '#7a0000');
            root.style.setProperty('--neutral-8', '#8d0000');
            root.style.setProperty('--neutral-9', '#a10000');
            root.style.setProperty('--neutral-a', '#b50000');
            root.style.setProperty('--neutral-b', '#c80000');
            root.style.setProperty('--neutral-c', '#dc0000');
            root.style.setProperty('--neutral-d', '#e80000');
            root.style.setProperty('--neutral-e', '#f00000');
            root.style.setProperty('--neutral-f', '#ff0000');

            root.style.setProperty('--button-white', '#a22');
            root.style.setProperty('--button-white-hoverfocus', '#c33');
            root.style.setProperty('--button-white-text', '#200');
            root.style.setProperty('--button-success', '#d0312a');
            root.style.setProperty('--button-success-hoverfocus', '#e8312a');
            root.style.setProperty('--button-success-text', '#440000'); 

            document.getElementById("datatables-css").href = "static/css/datatables-red.css";
            Table.draw();
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
