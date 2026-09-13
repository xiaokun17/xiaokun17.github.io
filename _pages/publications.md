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
    <span><strong id="publication-total">70</strong> publications</span>
    <span>2014–2026</span>
    <span>Research areas: placeholder labels</span>
  </div>

  <div class="publication-tools">
    <label class="publication-search" for="publication-search-input">
      <i class="fas fa-search" aria-hidden="true"></i>
      <input id="publication-search-input" type="search" placeholder="Search title, author, venue, year, or keyword" autocomplete="off">
    </label>
    <label class="publication-filter" for="publication-area-filter">
      <span>Research area</span>
      <select id="publication-area-filter">
        <option value="all">All areas</option>
        <option value="Fluid Simulation">Fluid Simulation</option>
        <option value="Deformable Materials">Deformable Materials</option>
        <option value="VR / HCI">VR / HCI</option>
        <option value="Rendering">Rendering</option>
        <option value="Research area placeholder">Research area placeholder</option>
      </select>
    </label>
    <button class="publication-clear" id="publication-clear" type="button" aria-label="Clear publication filters" title="Clear filters">
      <i class="fas fa-times" aria-hidden="true"></i>
    </button>
  </div>

  <p class="publication-placeholder-note">Topic labels and additional resource links are placeholders for this layout preview and can be replaced in the BibTeX records.</p>

  <div id="publication-empty" class="publication-empty" hidden>No publications match the current filters.</div>

  {%- for y in page.years %}
    <section class="publication-year" data-publication-year="{{ y }}">
      <h2 class="year">{{ y }}</h2>
      {% bibliography -f papers -q @*[year={{y}},visible!=false]* %}
    </section>
  {% endfor %}
</div>

<script defer src="{{ '/assets/js/publications.js' | relative_url }}"></script>
