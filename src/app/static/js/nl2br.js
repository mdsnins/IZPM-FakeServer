$(function(){
    $('.nl2br').each(function() {
      $(this).html($(this).html().replace(/\r?\n/g,'<br>'));
    });
  });