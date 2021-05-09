$(function(){
    const checkbox_selector = 'input[type=checkbox]';
    $('#sent_btn').addClass('disabled');
    $('body').delegate(checkbox_selector, 'click', function() {
      var length, checked_length;
  
      length = $(checkbox_selector).length;
      checked_length = $(checkbox_selector + ':checked').length;
  
      if (length === checked_length) {
        $('#sent_btn').removeClass('disabled');
      } else {
        $('#sent_btn').addClass('disabled');
      }
    });
  });