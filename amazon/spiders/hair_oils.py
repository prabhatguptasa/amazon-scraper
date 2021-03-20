import scrapy
from scrapy.loader import ItemLoader
from amazon.items import AmazonItem


class HairOilSpider(scrapy.Spider):
    name = 'hair_oil'
    custom_settings = {
        'LOG_ENCODING': 'UTF-8',
        'LOG_FILE': f'logs/{name}.log',
        'LOG_FORMAT': '%(asctime)s [%(name)s] %(levelname)s: %(message)s',
        'LOG_DATEFORMAT': '%Y-%m-%d %H:%M:%S',
        'LOG_LEVEL': 'INFO',
        'LOG_STDOUT': True
    }

    def start_requests(self):
        urls = ['https://www.amazon.in/s?rh=n%3A3507139031&fs=true']

        i = 1
        while i < 40:
            i += 1
            urls.append(f'https://www.amazon.in/s?i=beauty&rh=n%3A3507139031&page={i}')

        for url in urls: yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        for href in response.xpath('//span[@data-component-type= "s-product-image"]//a[@class="a-link-normal s-no-outline"]/@href').getall():
            self.logger.info(href)
            yield scrapy.Request('https://www.amazon.in' + href, callback=self.parse_product)

    def parse_product(self, response):
        l = ItemLoader(item=AmazonItem(), response=response)
        row = {}
        try:
            row['Product Name'] = response.xpath('//span[@id="productTitle"]/text()').extract_first().replace('\n\n\n\n\n\n\n\n', '').strip()
        except:
            row['Product Name'] = 'NA'
        row['Product Url'] = response.url
        try:
            row['MRP'] = response.xpath('//span[@class="priceBlockStrikePriceString a-text-strike"]/text()').extract_first().strip()
        except:
            row['MRP'] = 'NA'
        try:
            row['Sale'] = response.xpath('//span[@id="priceblock_ourprice"]/text()').extract_first().strip()
        except:
            row['Sale'] = 'NA'
        try:
            row['Total Customer Reviews'] = response.xpath('//span[@id="acrCustomerReviewText"]/text()').extract_first().strip()
        except:
            row['Total Customer Reviews'] = 'NA'
        try:
            description = ''
            for des in response.xpath('//div[@id="productDescription"]//p/text()').getall():
                description = description + '\n' + des.replace('\n\n\n\n\n\n\n\n\n', '').strip()
            row['Description'] = description
        except:
            row['Description'] = 'NA'
        try:
            for feature in response.xpath('//div[@id="detailBullets_feature_div"]//ul//li'):
                if 'Customer Reviews:' not in feature.xpath('.//span[@class="a-text-bold"]/text()').extract_first():
                    if 'Best Sellers Rank' not in feature.xpath('.//span[@class="a-text-bold"]/text()').extract_first():
                        row[feature.xpath('.//span[@class="a-text-bold"]/text()').extract_first().replace(
                            '\n\n\n\n:\n\n\n', '')] = feature.xpath(
                            './/span[@class="a-text-bold"]//following::span/text()').extract_first()
        except:
            pass
        soup = BeautifulSoup(response.text, "html.parser")
        heading = "Best Sellers Rank"
        get_text = soup.find('div', attrs={'id': 'detailBullets_feature_div'}).find_next('ul').find_next('ul').text
        row[heading] = get_text.replace(heading, '').replace(':', '').strip()
        try:
            for feature_rating in response.xpath('//div[@data-hook="cr-summarization-attributes-list"]//div[@data-hook="cr-summarization-attribute"]'):
                row[feature_rating.xpath('.//span/text()').extract_first().replace('\n\n\n\n:\n\n\n', '')] = feature_rating.xpath('.//span//following::span/text()').extract_first()
        except:
            pass
        try:
            tag = ''
            for tags in response.xpath('//div[@class="cr-lighthouse-terms"]//span[@class="cr-lighthouse-term "]/text()').getall():
                tag = tag + ', ' + tags.replace(' \n        ', '').strip()

            row['Product Tags'] = tag
        except:
            row['Product Tags'] = 'NA'
        self.logger.info(row)
        l.add_value('row', row)

        yield l.load_item()
