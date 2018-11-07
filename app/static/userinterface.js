
function newUI() {

    var public = [];

    /* expandable modules */
    function collapseSection(element) {
        var sectionHeight = element.scrollHeight+8;
        var elementTransition = element.style.transition;
        element.style.transition = '';
        
        requestAnimationFrame(function() {
            element.style.height = sectionHeight + 'px';
            element.style.transition  = elementTransition;
            requestAnimationFrame(function() {
                element.style.height = 0 + 'px';
            });
        });

        element.setAttribute('data-collapsed', 'true');
    }
    function expandSection(element) {
        var sectionHeight = element.scrollHeight;
        element.style.height = sectionHeight + 'px';
        element.addEventListener('transitionend', function(e)
        {
            element.removeEventListener('transitionend', arguments.callee);
            element.style.height = null;
        });
        element.setAttribute('data-collapsed', 'false');
    }
    // Expand/collapse module if user clicks on the header bar.
    var modules = document.querySelectorAll('.module-head');
    for (var i=0, j=modules.length; i<j; i++) {
        modules[i].addEventListener('click', function(e) {
            // prevent action if user clicks on form elements in header bar
            var noRedirect = '.head-inputs *';
            if (!e.target.matches(noRedirect)) {
                var section = this.nextElementSibling; 
                var isCollapsed = section.getAttribute('data-collapsed') === 'true';
                if(isCollapsed) {
                    expandSection(section);
                    section.setAttribute('data-collapsed', 'false');
                } else {
                    collapseSection(section);
                }
            }
        })
    }

    /* tabs */
    $(document).ready(function(){
        $('ul.views-tabs li').click(function(){
            var tab_id = $(this).attr('data-tab');

            $('ul.views-tabs li').removeClass('current');
            $('.views-content').removeClass('current');

            $(this).addClass('current');
            $('#'+tab_id).addClass('current');
        });
    });

    /* scroll icons */
    $('.scroll-button').each(function () {
        var target = $(this).data("id");
        $(this).click(function () {
            var module_fromtop = document.getElementById('module'+target).offsetTop;
            var div_fromtop = $('.controls').offset().top;
            var module_from_div = module_fromtop - div_fromtop - 20;
            $('.controls').animate({
                scrollTop: module_from_div

            }, 800,"swing");
        });
    });

    /* slider bar for table magnitude filter */
    var magfilterslider = document.getElementById('mag-filter-slider');
    noUiSlider.create(magfilterslider, {
        start: [4, 18], 
        connect: true,
        direction: 'rtl',
        orientation: 'vertical',
        //tooltips: [true, true],
        range: {
            'min': -1,
            'max': 20,
        }
    });
    magfilterslider.style.height = '100px';

    function target_clicked(ra, de) {
        state.ra_selected = ra;
        state.de_selected = de;
        
        $('#target-search').val(ra.toFixed(2)+', '+de.toFixed(2));
    } 

    window.onbeforeunload = function() {
        window.scrollTo(0,0);
    }


    public.target_clicked = target_clicked;
    return public;
}

var UI= newUI();