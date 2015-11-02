from scrapy.spiders.crawl import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor


class GoodReadsQuotesSpider(CrawlSpider):
    name = 'goodreads-quotes'

    custom_settings = {
        'DEPTH_LIMIT': 40,
        'DOWNLOAD_DELAY': 0.5,
    }

    rules = (
        Rule(LinkExtractor(restrict_css='a.next_page'),
             follow=True,
             callback='parse_quotes'),
    )

    start_urls = ['https://www.goodreads.com/quotes']

    def parse_quotes(self, response):
        for quote in response.css('div.quote'):
            yield self.extract_quote(quote)

    def extract_quote(self, quote):
        def first(sel):
            return sel.extract_first() if sel else None
        return {
            'text': first(quote.css('.quoteText').xpath('normalize-space(./text())')),  # NOQA
            'author':  {
                'name': first(quote.css('.quoteText > a::text')),
                'goodreads_link': first(quote.css('.quoteText > a::attr("href")')),  # NOQA
            },
            'tags': quote.css('.quoteFooter').xpath('.//a[contains(@href, "tag")]/text()').extract(),  # NOQA
        }
