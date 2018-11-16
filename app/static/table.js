
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
