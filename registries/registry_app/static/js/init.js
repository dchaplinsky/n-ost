$(document).ready(function() {
    function escapeRegExp(str) {
      return str.replace(/[\-\[\]\/\{\}\(\)\*\+\?\.\\\^\$\|]/g, "\\$&");
    }

    $('#registry').DataTable( {
        lengthChange: false,
        pageLength: 30,
        "columnDefs": [
            {
                "width": "100",
                "targets": [3, 4]
            },
            {
                "width": "30%",
                "targets": 2
            },
            {
                "orderable": false,
                "targets": 5
            },
        ],
        initComplete: function () {
            var self = this;

            $('#registry_search').on('keyup', function() {
                self.api().search($(this).val()).draw();
            });

            this.api().columns().every( function () {
                var column = this;
                if (column.index() == 0 || column.index() == 1) {
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
                                .search(val ? '^' + val + '$': '', true, false)
                                .draw();
                        } );
     
                    column.data().unique().sort().each( function ( d, j ) {
                        select.append( '<option value="'+d+'">'+d+'</option>' )
                    } );
                }

                if (column.index() == 3 || column.index() == 4) {
                    column.data().unique().sort().each(function (d, j) {
                        var colname = 'col-' + column.index(),
                            option = $(
                            '<label style="display: block; line-height: 15px"><input type="checkbox" value="' + d +
                                '" name="' + colname + '" checked> ' + d + 
                            '</label>'
                        );

                        option.appendTo($(column.header()));

                        option.on("click", function(e) {
                            e.stopPropagation();
                        });

                        option.find("input").on("change", function(e) {
                            var values = $.map(
                                $("input[name=" + colname + "]").serializeArray(),
                                function(val, i) {
                                    return escapeRegExp(val.value);
                                }
                            );

                            column
                                .search(values.length ? '^' + values.join("|") + '$': '', true, false)
                                .draw();
                        });
                    } );
                }                
            } );
        }
    } );
} );