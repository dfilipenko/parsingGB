HH_NAVIGATION_SELECTORS = {
    "parse_item": '//div[@class="vacancy-serp"]'
    '/div[contains(@data-qa, "vacancy-serp__vacancy")]'
    '//a[contains(@data-qa, "vacancy-title")]/@href',
    "parse": '//a[contains(@data-qa, "pager-next")]/@href',
}

HH_ITEM_SELECTORS = {
    "title": "//h1/text()",
    "salary": '//p[contains(@class,"vacancy-salary")]//text()',
}

SJ_NAVIGATION_SELECTORS = {
    "parse_item": '//div[contains(@class, "f-test-search-result-item")]'
                  '//span[contains(@class, "f-test-text-company-item-salary")]'
                  '/preceding-sibling::div/a/@href',
    "parse": '//a[contains(@class, "f-test-button-dalshe")]/@href'}

SJ_ITEM_SELECTORS = {
    "title": "//h1//text()",
    "salary": '//div[contains(@class, "f-test-address")]//following-sibling::span/span[1]//text()',
}
# complex way
ITEM_ACTIONS = {
    "title": lambda response: response.xpath(HH_ITEM_SELECTORS["title"]).get(),
    "salary": lambda response: response.xpath(HH_ITEM_SELECTORS["salary"]).getall(),
}
