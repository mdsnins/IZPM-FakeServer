// タップイベント
function tapImage() {
    var $image = $(this);
    var id = $image.data('id');
    var isFavorite = $image.closest('.select-image-area').attr('data-favorite');
    var imageUrl = encodeURIComponent($image.attr('src'));
    var str = 'akb48-mail://photo?id=' + id + '&is_favorite=' + isFavorite + '&image_url=' + imageUrl;
    location.href = str;
  }
  // お気に入り登録/削除の描画更新
  function updatePhoto(id) {
    // 同じ画像が複数あるかもしれないので
    var $images = $('img[data-id=' + id + ']');
    $images.each(function() {
      var $image = $(this);
      var favorite = $image.closest('.select-image-area').attr('data-favorite');
      // 反転
      favorite = favorite == 'true' ? 'false' : 'true';
      $image.closest('.select-image-area').attr('data-favorite', favorite);
    });
  }
  // ロードイベント
  $(function(){
    var $images = $('.js-select-images');
    $images.each(function() {
      var image = this;
      // タップイベント登録
      image.addEventListener('click', tapImage, false);
    });
  });