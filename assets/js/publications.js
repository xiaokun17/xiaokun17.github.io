document.addEventListener('DOMContentLoaded', function () {
  var searchInput = document.getElementById('publication-search-input');
  var areaFilter = document.getElementById('publication-area-filter');
  var clearButton = document.getElementById('publication-clear');
  var emptyState = document.getElementById('publication-empty');
  var totalCount = document.getElementById('publication-total');
  var entries = Array.prototype.slice.call(document.querySelectorAll('.publication-entry'));
  var yearSections = Array.prototype.slice.call(document.querySelectorAll('.publication-year'));

  if (totalCount) totalCount.textContent = entries.length;
  if (!searchInput || !areaFilter || !clearButton || !emptyState) return;

  function applyFilters() {
    var query = searchInput.value.trim().toLowerCase();
    var area = areaFilter.value;
    var visibleCount = 0;

    entries.forEach(function (entry) {
      var matchesQuery = !query || (entry.getAttribute('data-publication-search') || '').toLowerCase().indexOf(query) !== -1;
      var matchesArea = area === 'all' || entry.getAttribute('data-publication-area') === area;
      var visible = matchesQuery && matchesArea;
      entry.hidden = !visible;
      var publicationItem = entry.closest('li');
      if (publicationItem) publicationItem.hidden = !visible;
      if (visible) visibleCount += 1;
    });

    yearSections.forEach(function (section) {
      section.hidden = !section.querySelector('.publication-entry:not([hidden])');
    });

    emptyState.hidden = visibleCount !== 0;
  }

  searchInput.addEventListener('input', applyFilters);
  areaFilter.addEventListener('change', applyFilters);
  clearButton.addEventListener('click', function () {
    searchInput.value = '';
    areaFilter.value = 'all';
    applyFilters();
    searchInput.focus();
  });

  applyFilters();
});
