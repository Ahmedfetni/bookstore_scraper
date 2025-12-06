import scrapy
import re
from scrapy.http import Request
from bookstore_scraper.items import BookItem 

class BookSpider(scrapy.Spider):
    name = 'books'
    allowed_dimains = ['books.toscrape.com'] 
    start_urls = ["https://books.toscrape.com/"]

    # adi parse function khdmtha ghir tjib url t3  ktab 
    def parse(self, response):
        books = response.css('article.product_pod') # adi to get the book cause they have class name product_pod
        for book in books:
            book_url = book.css('h3 a::attr(href)').get()

            if book_url:

                # adi beh troh l book page pdp
                yield response.follow(book_url, callback=self.parse_book_detail)
        # hna bch ntb3o la pagination 
        next_page = response.css('li.next a::attr(href)').get() # TODO hna n9dro nkhdmo b url pr ex      https://books.toscrape.com/catalogue/page-{nombre de page}.html
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        
    def parse_book_detail(self, response):
        url = response.url
        title = response.css('div.product_main h1::text').get()
        # adi tjbed text f td li mor th faha tzxr UPC  
        upc = response.xpath("//th[text()='UPC']/following-sibling::td/text()").get()
        price = response.css('p.price_color::text').get()
        if price:
            price = float(price[1::])
        stock = None
        instock_string =  response.css('p.instock::text').getall()
        instock_string =   instock_string[1].strip()
        instock = "In stock" in instock_string
        if instock:
            stock = re.search(r"\d+", instock_string)
        book_descripion =  response.css('div#product_description + p::text').get()
        rating_map = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5
        }
        # nhwso p class t3ha star-rating w mapouha dict text to int 
        rating_stars = response.css("p.star-rating::attr(class)").get()
        if rating_stars:
            rating = rating_map.get(rating_stars,0)
        image = response.css('div#product_gallery div.item img::attr(src)').get()
        if image:
            image = response.urljoin(image) # full url de l image
        number_of_reviews = response.xpath("//th[text()='Number of reviews']/following-sibling::td/text()").get()
        breadcrumb = response.css('ul.breadcrumb li::text').getall() # last element
        if breadcrumb:
            breadcrumb = response.css('ul.breadcrumb li a::text').getall() + breadcrumb[-1:-1] # first elements + slice
        # item building 
        item = BookItem()
        item['url'] = url
        item['title'] = title
        item['upc'] = upc 
        item['price'] = price 
        item['instock'] = instock
        item['stock']=  stock
        item['rating'] = rating
        item['book_descripion'] = book_descripion
        item['image'] = image
        item['number_of_reviews'] = number_of_reviews
        item['breadcrumb'] = breadcrumb
        yield item