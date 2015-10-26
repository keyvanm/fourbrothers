
$(document).ready(function animationHover(element, animation){
    elementOne = $("i.fa-users");
    elementOne.hover(
        function() {

            elementOne.addClass('animated tada');        
        },
        function(){
                elementOne.removeClass('animated tada');       
        });
    elementTwo = $("i.fa-calendar");
    elementTwo.hover(
        function() {

            elementTwo.addClass('animated bounce');        
        },
        function(){
          
                elementTwo.removeClass('animated bounce');         
        });
    elementThree = $("i.fa-trophy");
    elementThree.hover(
        function() {

            elementThree.addClass('animated rubberBand');        
        },
        function(){
                elementThree.removeClass('animated rubberBand');      
        });

    $("#id_gratuity").change( function(){
        var gratuity = $("#id_gratuity option:selected").text();
        var grat_clean_value = $("#id_gratuity").val();
        var total_before_tax = $("#total-before-tax").text();
        total_before_tax = Number(total_before_tax).toFixed(2);
        var total_gratuity = total_before_tax*(grat_clean_value/100);
        total_gratuity = Number(total_gratuity).toFixed(2);
        //console.log(total_gratuity);
        var total = Number(total_gratuity) + Number(total_before_tax * 1.13);
        //console.log(total);
        total = Number(total).toFixed(2);
        $("#grat-perc").html(gratuity);
        $("#grat-amount").html(total_gratuity);
        $("#total").html(total);
        var total_no_dec = total.replace(".", "")
        var total_desc = "$" + total
        $(".stripe-button").data("amount", total_no_dec).data("description", total_desc);
    });

    $("#id_services input").click(function(event) {
        var checked_service = $(event.target).parent().text();
        var service_cost = checked_service.split("$")[1].replace(/[^\d.]/g, '');
        console.log("this is the cost: " + service_cost);
        var current_cost = $(".live-cart").data("amount");
        var new_cost;
        if ($(event.target).prop("checked")) {
            new_cost = Number(current_cost) + Number(service_cost);
        } else {
            new_cost = Number(current_cost) - Number(service_cost);
        }
        $(".live-cart").data("amount", new_cost);
        $(".live-cart h3").html("$" + new_cost);
    });

    if (Number($("#total-before-tax").text()) < 10) {
        $("#id_loyalty").prop('disabled', true);
    }

    //$("#id_loyalty").keyup(function() {
    //    if(Number($("#id_loyalty").val()) < 0 || $("#id_loyalty").val() == "-") {
    //        $("#id_loyalty").val("");
    //    }
    //});

    $(".cancel-btn").click(function(event) {
        if (confirm('Are you sure?')) {
            return
        } else {
            event.preventDefault();
        }
    });
});


