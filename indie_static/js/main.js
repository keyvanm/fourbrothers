
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

    $("#grat").change( function(){
        var gratuity = $("#grat option:selected").text();
        var grat_clean_value = $("#grat").val();
        var total_before_tax = $("#total-before-tax").text();
        total_before_tax = Number(total_before_tax).toFixed(2);
        var total_gratuity = total_before_tax*(grat_clean_value/100);
        total_gratuity = Number(total_gratuity).toFixed(2);
        console.log(total_gratuity);
        var total = Number(total_gratuity) + Number(total_before_tax * 1.13);
        console.log(total);
        total = Number(total).toFixed(2);
        $("#grat-perc").html(gratuity);
        $("#grat-amount").html(total_gratuity);
        $("#total").html(total);
        var total_no_dec = total.replace(".", "")
        var total_desc = "$" + total
        $(".stripe-button").attr("data-amount", total_no_dec).attr("data-description", total_desc);
    });

    //$(".stripe-button-el").click(function () {
    //
    //});
});


