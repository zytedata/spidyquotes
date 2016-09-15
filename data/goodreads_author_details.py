# -*- coding: utf-8 -*-
import json
import scrapy
from w3lib.url import urljoin


class GoodreadsAuthorDetailsSpider(scrapy.Spider):
    name = "goodreads_author_details"
    allowed_domains = ["goodreads.com"]
    # download_delay = 0.5

    def start_requests(self):
        with open("quotes-100.jl") as f:
            for line in f:
                quote = json.loads(line)
                yield scrapy.Request(
                    urljoin(
                        'http://www.goodreads.com',
                        quote.get('author', {}).get('goodreads_link')
                    )
                )

    def parse(self, response):
        self.log('visiting {}'.format(response.url))
        item = {}
        item['name'] = response.xpath('//h1[@class="authorName"]/span/text()').extract_first()
        item['born_in'] = response.xpath(
            'normalize-space(//div[@class="dataTitle"][1]/following-sibling::text()[1])'
        ).extract_first()
        item['born_at'] = response.xpath('normalize-space(//div[@class="dataItem" and @itemprop="birthDate"]/text())').extract_first()
        item['description'] = ' '.join(response.xpath('string(//div[@class="aboutAuthorInfo"]/span[1])').extract())
        full_description = ' '.join(response.xpath('string(//div[@class="aboutAuthorInfo"]/span[2])').extract())
        if len(full_description) > len(item["description"]):
            item['description'] = full_description
        yield item
