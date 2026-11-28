require 'jekyll/scholar'

module Jekyll
  class YearBibliographyTag < Scholar::BibliographyTag
    def entries
      in_press, published = super.partition { |entry| entry[:note].to_s.strip.casecmp?('In press') }
      in_press + published
    end
  end
end

Liquid::Template.register_tag('year_bibliography', Jekyll::YearBibliographyTag)
