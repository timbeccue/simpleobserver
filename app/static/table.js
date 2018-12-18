
/*
$(document).ready(function(){
    var table = $('#targets-table').DataTable({
        processing: true,
        serverSide: true,
        deferRender: true,
        //paging: false,
        compact: true,
        responsive: true,
        scrollY: "calc(75vh - 300px)",
        //scroller: true,
        scroller: { loadingIndicator: true},
        select: true,
        stateSave: true,
        ajax: "/tablelookup",
        oSearch: { "sSearch": "M" }
    });

    // Respond to row click
    $('#targets-table').on("click", 'tr', function() {
        var ra = table.row(this).data()[3];
        var de = table.row(this).data()[4];
        SkyMap.update_pointer(ra, de);
        UI.target_clicked(ra, de);
    } );
});
*/

$(document).ready(function(){


    var table = $('#targets-table').DataTable({
        processing: false,
        searching: false,
        serverSide: true,
        deferRender: true,
        //paging: false,
        compact: true,
        //responsive: true,
        scrollY: "calc(20vh)",
        //scroller: true,
        scroller: { loadingIndicator: true },
        select: true,
        stateSave: false, // gets out of sync with filters
        ajax: "/tablelookup",
        columnDefs: [{
            targets: [3, 4],
            render: $.fn.dataTable.render.number(',', '.', 2)
        },{
            targets: [5],
            width: "130px"
        }]
        //oSearch: { "sSearch": "M" },
    });


    // Respond to row click
    $('#targets-table tbody').on("click", 'tr', function() {
        var ra = table.row(this).data()[3];
        var de = table.row(this).data()[4];
        UI.target_clicked(ra, de);
        SkyMap.update_pointer(ra, de);
    } );

    table.draw();


    $(function() {
        $('#filter_form').children().on('change', submit_filter);
    });


function submit_filter(e) {
    e.preventDefault();
    var form = $('#filter_form');
    $.ajax({
        type: form.attr('method'),
        url: form.attr('action'),
        data: form.serialize(),
        success: function(data) {

            var filter = Object.assign({}, SkyMap.default_filter); // deep clone of default blank filter
            filter.dso_types = data.visible_dsos;
            filter.star_types = data.visible_stars;
            filter.dso_magnitudes = data.dso_magnitudes;
            filter.stellar_magnitudes = data.stellar_magnitudes;

            SkyMap.update_chart(filter);
            Celestial.redraw();
            table.draw();
        },
        error: function(data) {
            console.log('failed to apply filter to table');
        }
    });
}
});