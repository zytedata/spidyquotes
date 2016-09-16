from scrapy.spiders.crawl import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import scrapy


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
    trusted_authors = []
    start_urls = ['https://www.goodreads.com/quotes']

    def parse_quotes(self, response):
        for quote in response.css('div.quote'):
            item = self.extract_quote(quote)
            if item.get('author', {}).get('name') in self.trusted_authors:
                yield item
            else:
                yield scrapy.Request(
                    response.urljoin(item.get('author', {}).get('goodreads_link')),
                    callback=self.parse_author,
                    meta={'item': item}
                )

    def extract_quote(self, quote):
        def first(sel):
            return sel.extract_first() if sel else None
        return {
            'text': first(quote.css('.quoteText').xpath('normalize-space(./text())')),  # NOQA
            'author': {
                'name': first(quote.css('.quoteText > a::text')),
                'goodreads_link': first(quote.css('.quoteText > a::attr("href")')),  # NOQA
            },
            'tags': quote.css('.quoteFooter').xpath('.//a[contains(@href, "tag")]/text()').extract(),  # NOQA
        }

    def parse_author(self, response):
        item = response.meta.get('item')
        born_in = response.xpath(
            'normalize-space(//div[@class="dataTitle"][1]/following-sibling::text()[1])'
        ).extract_first()
        born_at = response.xpath(
            'normalize-space(//div[@class="dataItem" and @itemprop="birthDate"]/text())'
        ).extract_first()
        description = ' '.join(response.xpath('string(//div[@class="aboutAuthorInfo"]/span[2])').extract())
        if born_in and born_at and description:
            self.trusted_authors.append(item.get('author', {}).get('name'))
            yield item
