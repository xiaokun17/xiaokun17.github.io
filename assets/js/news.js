document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.news[data-news-batch-size]').forEach(function (news) {
    var items = Array.prototype.slice.call(news.querySelectorAll('.news-list > li'));
    var controls = news.querySelector('.news-controls');
    var moreButton = news.querySelector('.news-more');
    var lessButton = news.querySelector('.news-less');
    if (!controls || !moreButton || !lessButton) return;

    var batchSize = parseInt(news.getAttribute('data-news-batch-size'), 10);
    if (!Number.isFinite(batchSize) || batchSize < 1) batchSize = 5;
    // Store each revealed boundary so a partial final batch also collapses correctly.
    var boundaries = [Math.min(batchSize, items.length)];

    function render() {
      var visibleCount = boundaries[boundaries.length - 1];
      items.forEach(function (item, index) {
        item.hidden = index >= visibleCount;
        item.classList.toggle('is-last-visible', index === visibleCount - 1);
      });
      controls.hidden = items.length <= batchSize;
      moreButton.hidden = visibleCount >= items.length;
      lessButton.hidden = boundaries.length === 1;
    }

    moreButton.addEventListener('click', function () {
      var visibleCount = boundaries[boundaries.length - 1];
      if (visibleCount >= items.length) return;
      boundaries.push(Math.min(visibleCount + batchSize, items.length));
      render();
      if (moreButton.hidden) lessButton.focus({ preventScroll: true });
    });

    lessButton.addEventListener('click', function () {
      if (boundaries.length === 1) return;
      boundaries.pop();
      render();
      if (lessButton.hidden) moreButton.focus({ preventScroll: true });
    });

    render();
  });
});
