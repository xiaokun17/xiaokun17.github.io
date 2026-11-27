# Adapted from http://movb.de/jekyll-details-support.html
module Jekyll
  module Tags
    class DetailsTag < Liquid::Block
      def render(context)
        converter = context.registers[:site].find_converter_instance(Jekyll::Converters::Markdown)
        caption = converter.convert(@markup.strip).strip.sub(/\A<p>/, '').sub(%r{</p>\z}, '')
        body = converter.convert(super(context))
        "<details><summary>#{caption}</summary>#{body}</details>"
      end
    end
  end
end

Liquid::Template.register_tag('details', Jekyll::Tags::DetailsTag)
