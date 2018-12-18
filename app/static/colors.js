/* jshint esversion: 6 */
/* Defines site-wide, color themes that can be selected by the user. */


const root = document.documentElement;
const color_buttons = ''; // document.querySelectorAll('.color-button');


//color_buttons.forEach((btn) => {
    //btn.addEventListener('click', handleThemeUpdate);
//});

$('#scroll-6').click(handleThemeUpdate);

function handleThemeUpdate(e) {
    console.log(e.target.getAttribute('data-color'));
    switch(e.target.getAttribute('data-color')) {
        case 'dark': 
            root.style.setProperty('--bg', '#222');
            root.style.setProperty('--bg-text', '#ccc');
            break;
        case 'red': 
            root.style.setProperty('--bg', '#050000');
            root.style.setProperty('--bg-text', '#a33');
            SkyMap.toggle_night_colors('red');
            break;
        case 'toggle': 
            SkyMap.toggle_night_colors();
            break;
    }
}
