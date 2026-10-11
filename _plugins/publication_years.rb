require 'bibtex'

module Jekyll
  class PublicationYearsGenerator < Generator
    safe true

    def generate(site)
      bibliography = BibTeX.open(site.in_source_dir('_bibliography', 'papers.bib'))
      site.data['publication_years'] = bibliography.query('@*[visible!=false]*')
        .map { |entry| entry[:year].to_s.strip }
        .select { |year| year.match?(/\A\d{4}\z/) }
        .map(&:to_i).uniq.sort.reverse
    end
  end
end
