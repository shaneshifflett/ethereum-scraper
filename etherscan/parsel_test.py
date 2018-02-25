import requests
from parsel import Selector
url = 'https://etherscan.io/address/0x75f9379833800f397ead23dc2317daa456a4bedb#code'
text = requests.get(url).text
selector = Selector(text=text)
print(selector.css('#editor::text').extract())