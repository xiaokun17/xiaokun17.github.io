---
layout: about
title: About
permalink: /
description: Xiaokun Wang is a Professor at the University of Science and Technology Beijing researching physics-based simulation, differentiable rendering, virtual reality, and human-computer interaction.

profile:
  image: WangXiaoKun.png

featured_papers: true
social: true
---

## Biography

I am a full Professor at the [School of Intelligence Science and Technology, University of Science and Technology Beijing (USTB)](https://ai.ustb.edu.cn/). I received my Ph.D. from the [School of Computer and Communication Engineering, USTB](https://scce.ustb.edu.cn/) in January 2017.

From 2017 to 2022, I held postdoctoral, lecturer, and associate professor positions at USTB. I was also a visiting scholar and postdoctoral researcher at the [Bernoulli Institute, University of Groningen](https://www.rug.nl/research/bernoulli/?lang=en), collaborating with the [Scientific Visualization and Computer Graphics group](https://www.cs.rug.nl/svcg/). From July 2021 to July 2023, I was a Marie Skłodowska-Curie Fellow at the [National Centre for Computer Animation, Bournemouth University](https://www.bournemouth.ac.uk/about/our-faculties/faculty-media-communication/national-centre-computer-animation).

## Research Interests

<ul class="interest-list">
  <li><strong>Physics-Based Modeling</strong><span>Fluids, deformations, and multiphase phenomena</span></li>
  <li><strong>Differentiable Methods</strong><span>Differentiable rendering and simulation</span></li>
  <li><strong>Virtual Reality</strong><span>Surgical simulation and immersive interaction</span></li>
  <li><strong>Human-Computer Interaction</strong><span>Motion control and haptics</span></li>
  <li><strong>Industrial Applications</strong><span>Translating simulation technologies into practice</span></li>
</ul>

## News

{% include news.html %}

<div class="section-heading-row">
  <h2>Featured Achievements</h2>
  <a href="{{ '/achievements/' | relative_url }}">View all</a>
</div>

{% assign featured_achievements = site.data.achievements | where: 'featured', true | sort: 'featured_order' %}
{% assign featured_achievements = featured_achievements | sort: 'year' | reverse %}
<ol class="honors-list">
  {% for item in featured_achievements %}
    <li><time>{{ item.year }}</time><span><strong>{{ item.title }}</strong><br><small>{{ item.organization }}</small></span></li>
  {% endfor %}
</ol>
