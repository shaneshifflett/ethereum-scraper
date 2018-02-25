import scrapy

NEXT_BUTTON_TEXT = 'Next'


class EtherscanContractSpider(scrapy.Spider):
    name = "contracts"
    start_urls = [
        'https://etherscan.io/contractsVerified'
    ]
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.contrib.downloadermiddleware.retry.RetryMiddleware': 200
        },
        'FEED_EXPORT_FIELDS': ['address', 'bytecode', 'solidity'],
        'RETRY_TIMES': 60,
        'RETRY_HTTP_CODES': [500, 503, 504, 400, 403, 404, 408],
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 5,
        'AUTOTHROTTLE_MAX_DELAY': 120,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 1,
        'AUTOTHROTTLE_DEBUG': False,
        'LOG_LEVEL': 'INFO'
    }

    def parse(self, contracts_verified_response):
        for address_node in contracts_verified_response.css('.address-tag'):
            address = address_node.css('::text').extract_first()
            yield contracts_verified_response.follow("/address/%s#code" % address, self.parse_contract)

        next_page = contracts_verified_response.xpath(
            '//a[contains(., "%s")][not(@disabled="disabled")]' % NEXT_BUTTON_TEXT)
        if next_page is not None:
            yield contracts_verified_response.follow(next_page.css('::attr(href)').extract_first(), self.parse)

    def parse_contract(self, contract_response):
        address = contract_response.css('#address::text').extract_first()
        if address is not None and "throttle" in address.lower():
            self.logger.error('Request throttled ' + contract_response.url)
            yield scrapy.Request(contract_response.url, callback=self.parse_contract, dont_filter=True)
            return

        address = contract_response.css('#mainaddress::text').extract_first()
        bytecode = contract_response.css('#verifiedbytecode2::text').extract_first()
        solidity = contract_response.css('#editor::text').extract()

        if address is None or bytecode is None or solidity is None:
            self.logger.error('Address or bytecode or Solidity code are empty "%s" "%s" "%s"'  % (address, bytecode, solidity))
            yield scrapy.Request(contract_response.url, callback=self.parse_contract, dont_filter=True)
            return

        yield {
            'address': address,
            'bytecode': bytecode,
            'solidity': solidity
        }
