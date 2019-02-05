
// Gets a look up table every 5 minutes. Ra and Dec (both deg) rounded to the nearest degree
// correspond to a unique altitude. Originally designed to be used by datatables to calculate
// an altitude column on the fly, but I don't think it works well enough to use. The column is
// not sortable, and there's no simple way to only show targets with positive altitude.
/* 
var altitude_lut = new EventSource('/get_altitude_lut');
altitude_lut.onmessage = function(event){
    var sse_contents = tryParseJSON(event.data);
    altitude_lut = sse_contents;
    console.log(altitude_lut);
};
*/

function newTable() {

    var table = $('#targets-table').DataTable({
        processing: false,
        searching: false,
        serverSide: true,
        deferRender: false,
        pagingType: "simple",
        compact: true,
        responsive: {
            details: {
                display: $.fn.dataTable.Responsive.display.childRowImmediate,
                type: ""
            }
        },
        scrollY: "calc(20vh)",
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
        }/*,{
            targets: [6],
            render: function (data, type, row) {
                var index = ~~row[3]*180*15 + ~~(90+row[4]); // should double check this logic before using!
                return altitude_lut[index]; 
            }
        }*/]
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
        if(e){e.preventDefault();}
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


    data = [];
    data.table = table;
    data.submit_filter = submit_filter;
    data.draw = table.draw;
    return data;
}

var Table = newTable();

