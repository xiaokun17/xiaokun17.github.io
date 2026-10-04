---
layout: page
permalink: /publications/
title: Publications
description: Complete and selected publications on physics-based simulation, fluid dynamics, differentiable rendering, virtual reality, and human-computer interaction.
years: [2026, 2025, 2024, 2023, 2022, 2021, 2020, 2019, 2018, 2017, 2016, 2015, 2014]
nav: true
nav_order: 1
---

<div class="publications publications-page">
  <div class="publication-overview" aria-label="Publication overview">
    <span><strong id="publication-total">59</strong> publications</span>
    <label class="publication-year-range" for="publication-year-from">
      <span class="sr-only">Publication year range</span>
      <input id="publication-year-from" type="number" inputmode="numeric" min="1900" max="2100" step="1" value="2015" aria-label="Publication start year">
      <span aria-hidden="true">–</span>
      <input id="publication-year-to" type="number" inputmode="numeric" min="1900" max="2100" step="1" value="2026" aria-label="Publication end year">
    </label>
  </div>

  <div class="publication-tools">
    <label class="publication-search" for="publication-search-input">
      <i class="fas fa-search" aria-hidden="true"></i>
      <input id="publication-search-input" type="search" placeholder="Search title, author, venue, year, or keyword" autocomplete="off">
    </label>
    <button class="publication-clear" id="publication-clear" type="button" aria-label="Clear publication filters" title="Clear filters">
      <i class="fas fa-times" aria-hidden="true"></i>
    </button>
  </div>

  <div id="publication-empty" class="publication-empty" hidden>No publications match the current filters.</div>

  {%- for y in page.years %}
    <section class="publication-year" data-publication-year="{{ y }}">
      <h2 class="year">{{ y }}</h2>
      {% bibliography -f papers -q @*[year={{y}},visible!=false]* %}
    </section>
  {% endfor %}
</div>

<script defer src="{{ '/assets/js/publications.js' | relative_url }}"></script>
