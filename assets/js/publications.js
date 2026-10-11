document.addEventListener('DOMContentLoaded', function () {
  var searchInput = document.getElementById('publication-search-input');
  var clearButton = document.getElementById('publication-clear');
  var emptyState = document.getElementById('publication-empty');
  var yearsControls = document.getElementById('publication-years-controls');
  var moreYearsButton = document.getElementById('publication-years-more');
  var fewerYearsButton = document.getElementById('publication-years-less');
  var entries = Array.prototype.slice.call(document.querySelectorAll('.publication-entry'));
  var yearSections = Array.prototype.slice.call(document.querySelectorAll('.publication-year'));
  var olderSections = Array.prototype.slice.call(document.querySelectorAll('.publication-year-older'));
  var expandedBatches = [];
  var isSearching = false;
  var searchOpenStates = [];

  if (!searchInput || !clearButton || !emptyState) return;

  var batchSize = yearsControls ? parseInt(yearsControls.getAttribute('data-batch-size'), 10) : 5;
  if (!Number.isFinite(batchSize) || batchSize < 1) batchSize = 5;
  var yearCutoff = yearsControls ? parseInt(yearsControls.getAttribute('data-year-cutoff'), 10) : 2019;
  if (!Number.isFinite(yearCutoff)) yearCutoff = 2019;

  function hasEntries(section) {
    return !!section.querySelector('.publication-entry');
  }

  olderSections = olderSections.filter(hasEntries).sort(function (a, b) {
    return yearOf(b) - yearOf(a);
  });

  function yearOf(section) {
    return parseInt(section.getAttribute('data-publication-year'), 10);
  }

  function expandedSections() {
    return expandedBatches.reduce(function (all, batch) {
      return all.concat(batch.sections);
    }, []);
  }

  // Anchor five-calendar-year windows to the cutoff, skipping entirely empty windows.
  function nextBatch() {
    var remaining = olderSections.slice(expandedSections().length);
    if (!remaining.length) return null;
    var upperYear = yearCutoff - Math.floor((yearCutoff - yearOf(remaining[0])) / batchSize) * batchSize;
    var lowerYear = Math.max(upperYear - batchSize + 1, yearOf(remaining[remaining.length - 1]));
    return {
      upperYear: upperYear,
      lowerYear: lowerYear,
      sections: remaining.filter(function (section) {
        return yearOf(section) >= lowerYear && yearOf(section) <= upperYear;
      })
    };
  }

  function batchLabel(batch) {
    return batch.upperYear === batch.lowerYear ? String(batch.upperYear) : batch.upperYear + '\u2013' + batch.lowerYear;
  }

  function updateYearsControls() {
    if (!yearsControls) return;
    var expandedCount = expandedSections().length;
    yearsControls.hidden = olderSections.length === 0 || isSearching;
    if (moreYearsButton) moreYearsButton.hidden = expandedCount >= olderSections.length;
    if (fewerYearsButton) fewerYearsButton.hidden = expandedCount === 0;

    if (moreYearsButton && expandedCount < olderSections.length) {
      moreYearsButton.querySelector('span').textContent = 'More years (' + batchLabel(nextBatch()) + ')';
    }
    if (fewerYearsButton && expandedBatches.length) {
      var lastBatch = expandedBatches[expandedBatches.length - 1];
      fewerYearsButton.querySelector('span').textContent = 'Show fewer years (' + batchLabel(lastBatch) + ')';
    }
  }

  function revealNextBatch() {
    var batch = nextBatch();
    if (!batch) return;
    batch.sections.forEach(function (section) {
      section.hidden = false;
      section.open = true;
    });
    expandedBatches.push(batch);
    updateYearsControls();
    if (moreYearsButton.hidden && fewerYearsButton) fewerYearsButton.focus({ preventScroll: true });
  }

  function hideLastBatch() {
    var batch = expandedBatches.pop();
    if (!batch) return;
    batch.sections.forEach(function (section) {
      section.open = false;
      section.hidden = true;
    });
    updateYearsControls();
    if (fewerYearsButton.hidden && moreYearsButton) moreYearsButton.focus({ preventScroll: true });
  }

  function restoreYearVisibility() {
    var revealed = expandedSections();
    yearSections.forEach(function (section) {
      var visible = !section.classList.contains('publication-year-older') || revealed.indexOf(section) !== -1;
      var hasVisibleEntries = !!section.querySelector('.publication-entry:not([hidden])');
      section.hidden = !(visible && hasVisibleEntries);
    });
  }

  var acronyms = {
    ai: 'AI', eeg: 'EEG', gan: 'GAN', gans: 'GANs', hci: 'HCI',
    iisph: 'IISPH', llm: 'LLM', llms: 'LLMs', mpm: 'MPM', rgb: 'RGB',
    sph: 'SPH', tvcg: 'TVCG', vr: 'VR', xr: 'XR', '3d': '3D'
  };

  function titleCaseKeyword(value) {
    return value.split(/(\s+|-|\/)/).map(function (part) {
      var normalized = part.toLowerCase();
      if (acronyms[normalized]) return acronyms[normalized];
      if (/^\s+$/.test(part) || part === '-' || part === '/') return part;
      if (!part) return part;
      return part.charAt(0).toUpperCase() + part.slice(1).toLowerCase();
    }).join('');
  }

  document.querySelectorAll('.publication-keywords span').forEach(function (keyword) {
    keyword.textContent = titleCaseKeyword(keyword.textContent.trim());
  });

  function applyFilters() {
    var query = searchInput.value.trim().toLowerCase();
    if (query && !isSearching) {
      searchOpenStates = yearSections.map(function (section) { return section.open; });
    } else if (!query && isSearching) {
      yearSections.forEach(function (section, index) { section.open = searchOpenStates[index]; });
    }
    isSearching = !!query;
    var visibleCount = 0;

    entries.forEach(function (entry) {
      var matchesQuery = !query || (entry.getAttribute('data-publication-search') || '').toLowerCase().indexOf(query) !== -1;
      var visible = matchesQuery;
      entry.hidden = !visible;
      var publicationItem = entry.closest('li');
      if (publicationItem) publicationItem.hidden = !visible;
      if (visible) visibleCount += 1;
    });

    yearSections.forEach(function (section) {
      var hasVisibleEntries = !!section.querySelector('.publication-entry:not([hidden])');
      if (query) {
        section.hidden = !hasVisibleEntries;
        if (hasVisibleEntries) section.open = true;
      }
    });

    if (!query) restoreYearVisibility();
    updateYearsControls();

    emptyState.hidden = visibleCount !== 0;
  }

  searchInput.addEventListener('input', applyFilters);
  if (moreYearsButton) moreYearsButton.addEventListener('click', revealNextBatch);
  if (fewerYearsButton) fewerYearsButton.addEventListener('click', hideLastBatch);
  clearButton.addEventListener('click', function () {
    searchInput.value = '';
    applyFilters();
    searchInput.focus();
  });

  applyFilters();
});
