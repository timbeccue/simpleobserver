
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
                arrows(this);
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
    function arrows(head) {
        if (head.nextElementSibling.getAttribute('data-collapsed') === 'true') {
            head.querySelector('span').innerHTML = '&#9660;';
        }
        else {
            setTimeout(function(){
                head.querySelector('span').innerHTML = '&#9658;';
            }, 300);
        }
    }

    /* tabs */
    $(document).ready(function(){
        $('li.tab').click(function(){
            var tab_id = $(this).data('tab');
            var tabtype = $(this).data('tabtype');

            $('.'+tabtype+'-tab').removeClass('current');
            $('.'+tabtype+'-content').removeClass('current');

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

    function target_clicked(ra, de) {
        state.ra_selected = ra;
        state.de_selected = de;
        $('#target-search').val(ra.toFixed(2)+', '+de.toFixed(2));
        aladin.gotoRaDec(ra*15, de); // ra is converted from hours to degrees. 
    }

    window.onbeforeunload = function() {
        window.scrollTo(0,0);
    }


    public.target_clicked = target_clicked;
    return public;
}

var UI = newUI();
