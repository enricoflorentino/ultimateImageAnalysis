function sendBack(input) {
    console.log(input);
    
}


$("#submitthis").submit(function(event) {
    // event.preventDefault();
    console.log(event);
    var dataa = {"name":"NAME"}
    $.ajax({
        url: '/uploaded',
        // url: $(this).attr('action'),
        type: 'POST',
        dataType : 'json',
    
        // data: new FormData($('submitthis')[0]),
        contentType: "application/json; charset=utf-8",
        data : JSON.stringify(dataa),
        cache: false,
        // processData: false,
        crossDomain: true,
        success: function(data) {
            console.log('Success!');
        },
    });
});