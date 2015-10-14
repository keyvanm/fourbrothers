
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
});


