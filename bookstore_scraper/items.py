# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class BookItem(scrapy.Item):
        url = scrapy.Field()
        title = scrapy.Field()
        upc = scrapy.Field()
        price = scrapy.Field()
        instock = scrapy.Field()
        stock = scrapy.Field()
        book_descripion = scrapy.Field()
        rating = scrapy.Field()
        image = scrapy.Field()
        number_of_reviews = scrapy.Field()
        breadcrumb = scrapy.Field()
        scraped_at = scrapy.Field()
        