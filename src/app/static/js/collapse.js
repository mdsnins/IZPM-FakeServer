$(function(){
    var $toggle = $('[data-toggle=collapse]');
    $toggle.each(function() {
      var $self = $(this);
      var $target = $self.data('target') ? $($self.data('target')): $self.next('.collapse');
      if ($target.hasClass('show')) {
        $target.show();
        $self.addClass('open').removeClass('close');
      } else {
        $target.hide();
        $self.addClass('close').removeClass('open');
      }
      $self.on('click', function(){
        $self.toggleClass('open').toggleClass('close');
        $target.slideToggle();
      });
    });
  
      var swiper = new Swiper('.swiper-container', {
        autoHeight: true,
        pagination: {
          el: '.swiper-pagination',
          type: 'bullets',
        },
        navigation: {
          nextEl: '.swiper-button-next',
        },
      });
  });