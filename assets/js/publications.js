document.addEventListener('DOMContentLoaded', function () {
  var searchInput = document.getElementById('publication-search-input');
  var yearFromInput = document.getElementById('publication-year-from');
  var yearToInput = document.getElementById('publication-year-to');
  var clearButton = document.getElementById('publication-clear');
  var emptyState = document.getElementById('publication-empty');
  var totalCount = document.getElementById('publication-total');
  var entries = Array.prototype.slice.call(document.querySelectorAll('.publication-entry'));
  var yearSections = Array.prototype.slice.call(document.querySelectorAll('.publication-year'));

  if (totalCount) totalCount.textContent = entries.length;
  if (!searchInput || !yearFromInput || !yearToInput || !clearButton || !emptyState) return;

  function applyFilters() {
    var query = searchInput.value.trim().toLowerCase();
    var fromYear = parseInt(yearFromInput.value, 10);
    var toYear = parseInt(yearToInput.value, 10);
    var hasFromYear = Number.isFinite(fromYear);
    var hasToYear = Number.isFinite(toYear);
    var visibleCount = 0;

    entries.forEach(function (entry) {
      var matchesQuery = !query || (entry.getAttribute('data-publication-search') || '').toLowerCase().indexOf(query) !== -1;
      var entryYear = parseInt(entry.getAttribute('data-publication-year'), 10);
      var matchesFromYear = !hasFromYear || (Number.isFinite(entryYear) && entryYear >= fromYear);
      var matchesToYear = !hasToYear || (Number.isFinite(entryYear) && entryYear <= toYear);
      var visible = matchesQuery && matchesFromYear && matchesToYear;
      entry.hidden = !visible;
      var publicationItem = entry.closest('li');
      if (publicationItem) publicationItem.hidden = !visible;
      if (visible) visibleCount += 1;
    });

    yearSections.forEach(function (section) {
      section.hidden = !section.querySelector('.publication-entry:not([hidden])');
    });

    emptyState.hidden = visibleCount !== 0;
    if (totalCount) totalCount.textContent = visibleCount;
  }

  searchInput.addEventListener('input', applyFilters);
  yearFromInput.addEventListener('input', applyFilters);
  yearToInput.addEventListener('input', applyFilters);
  clearButton.addEventListener('click', function () {
    searchInput.value = '';
    yearFromInput.value = '2015';
    yearToInput.value = '2026';
    applyFilters();
    searchInput.focus();
  });

  applyFilters();
});
