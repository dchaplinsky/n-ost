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

        "dom": '<"top"flp<"clear">>rt<"bottom"ip<"clear">>',

        initComplete: function () {
            var self = this;

            $('#registry_search').on('keyup', function() {
                self.api().search($(this).val()).draw();
            });

            this.api().columns().every( function () {
                var column = this;
                if (column.index() == 0 || column.index() == 1) {
                    var select = $('<select style="max-width: 100%"><option value=""></option></select>')
                        .appendTo( $(column.header()) )
                        .on('click', function(e) {
                            e.stopPropagation();
                        })
                        .on('change', function () {
                            var val = $.fn.dataTable.util.escapeRegex(
                                $(this).val()
                            );
     
                            column
                                .search(val ? '^' + val + '$': '', true, false)
                                .draw();
                        });
                    
                    var top_countries = [
                        "armenia", "azerbaijan", "belarus", "georgia", "moldova", "russia", "ukraine",
                        "армения", "азербайджан", "беларусь", "грузия", "молдова", "россия", "украина",
                    ];

                    var options = column.data().unique().sort(function(a, b) {
                        var ind_1 = top_countries.indexOf(a.toLowerCase()),
                            ind_2 = top_countries.indexOf(b.toLowerCase());

                        // First sort by elite set
                        if (ind_1 != -1) {
                            if (ind_2 != -1) {
                                return ind_1 - ind_2;
                            } else {
                                return -1;
                            }
                        }

                        if (ind_2 != -1) {
                            return 1;
                        }

                        // If both elements aren't from elite set let's use standard sort
                        if (a > b) {
                            return 1;
                        } else if (a == b) {
                            return 0;
                        } else {
                            return -1;
                        }
                    });

                    options.each( function ( d, j ) {
                        select.append( '<option value="'+d+'">'+d+'</option>' )
                    });

                    var chsn = select.chosen({
                        "allow_single_deselect": true
                    });

                    select.siblings(".chosen-container").on('click', function(e) {
                        e.stopPropagation();
                    });
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
                                .search('^' + values.join("|") + '$', true, false)
                                .draw();
                        });
                    } );
                }                
            } );
        }
    } );
} );