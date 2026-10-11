---
layout: page
permalink: /publications/
title: Publications
description: Complete and selected publications on physics-based simulation, fluid dynamics, differentiable rendering, virtual reality, and human-computer interaction.
nav: true
nav_order: 1
---

<div class="publications publications-page">
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

  {% assign publication_cutoff = site.publication_year_cutoff | default: 2019 %}
  {% assign publication_batch_size = site.publication_year_batch_size | default: 5 %}
  {%- for y in site.data.publication_years %}
    <details class="publication-year{% if y <= publication_cutoff %} publication-year-older{% endif %}"
      data-publication-year="{{ y }}"
      {% if y > publication_cutoff %}open{% else %}hidden{% endif %}>
      <summary class="year">{{ y }}</summary>
      {% bibliography -f papers -q @*[year={{y}},visible!=false]* %}
    </details>
  {% endfor %}

  <div id="publication-years-controls" class="publication-years-controls"
    data-year-cutoff="{{ publication_cutoff }}" data-batch-size="{{ publication_batch_size }}" hidden>
    <button id="publication-years-more" class="publication-years-toggle" type="button">
      <i class="fas fa-chevron-down" aria-hidden="true"></i>
      <span>More years</span>
    </button>
    <button id="publication-years-less" class="publication-years-toggle" type="button" hidden>
      <i class="fas fa-chevron-up" aria-hidden="true"></i>
      <span>Show fewer years</span>
    </button>
  </div>
</div>

<script defer src="{{ '/assets/js/publications.js' | relative_url }}"></script>
