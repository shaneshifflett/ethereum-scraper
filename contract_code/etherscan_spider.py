import scrapy

NEXT_BUTTON_TEXT = '"Next"'


class EtherscanContractSpider(scrapy.Spider):
    name = "contracts"
    start_urls = [
        'https://etherscan.io/contractsVerified',
    ]
    custom_settings = {
        # specifies exported fields and order
        'FEED_EXPORT_FIELDS': ['address', 'bytecode'],
        # Retry many times since proxies often fail
        'RETRY_TIMES': 10,
        # Retry on most error codes since proxies fail for different reasons
        'RETRY_HTTP_CODES': [500, 503, 504, 400, 403, 404, 408],

        'DOWNLOAD_DELAY': 3,

        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.contrib.downloadermiddleware.retry.RetryMiddleware': 200
        }
    }

    def parse(self, contracts_verified_response):
        for address_node in contracts_verified_response.css('.address-tag'):
            address = address_node.css('::text').extract_first()
            yield contracts_verified_response.follow("/address/%s#code" % address, self.parse_contract)

        next_page = contracts_verified_response.xpath(
            '//a[contains(., %s)][not(@disabled="disabled")]' % NEXT_BUTTON_TEXT)
        if next_page is not None:
            yield contracts_verified_response.follow(next_page.css('::attr(href)').extract_first(), self.parse)

    def parse_contract(self, contract_response):
        address = contract_response.css('#mainaddress::text').extract_first()
        bytecode = contract_response.css('#verifiedbytecode2::text').extract_first()
        yield {
            'address': address,
            'bytecode': bytecode
        }
