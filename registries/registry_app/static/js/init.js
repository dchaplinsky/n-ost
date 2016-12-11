$(document).ready(function() {
    $('#registry').DataTable( {
        lengthChange: false,
        pageLength: 30,
        initComplete: function () {
            this.api().columns().every( function () {
                var column = this;
                if (column.index() > 4)
                    return;

                var select = $('<select style="max-width: 100px"><option value=""></option></select>')
                    .appendTo( $(column.header()) )
                    .on( 'click', function(e) {
                        e.stopPropagation();
                    })
                    .on( 'change', function () {
                        var val = $.fn.dataTable.util.escapeRegex(
                            $(this).val()
                        );
 
                        column
                            .search( val ? '^'+val+'$' : '', true, false )
                            .draw();
                    } );
 
                column.data().unique().sort().each( function ( d, j ) {
                    select.append( '<option value="'+d+'">'+d+'</option>' )
                } );
            } );
        }
    } );
} );