# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy import signals
from scrapy.exceptions import DropItem
import sqlite3


class ValidationPipeline:
    def process_item(self, item, spider):
        
        if not item.get('url'):
            raise DropItem("Missing url in %s" % item)
        
        if not item.get('title'):
            raise DropItem("Missing title in %s" % item)
        item['scraped_at'] = spider.crawler.stats.get_value('start_time').isoformat()
        if not item['stock']:
            item['stock'] = 0
        
        return item
    
class DatabasePipeline:

    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = None
        self.cursor = None

    @classmethod
    def from_crawler(cls, crawler):
        db_path = crawler.settings.get("DB_PATH", "books.db")
        pipeline = cls(db_path)
        
        # setting up the signals
        crawler.signals.connect(pipeline.open_spider, signal=signals.spider_opened)
        crawler.signals.connect(pipeline.close_spider, signal=signals.spider_closed)
        
        return pipeline
    
    # handling the connection and disconnection
    def open_spider(self, spider):
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                url TEXT PRIMARY KEY,
                title TEXT,
                upc TEXT,
                price REAL,
                instock BOOLEAN,
                stock INTEGER,
                book_description TEXT,
                rating INTEGER,
                image TEXT,
                number_of_reviews INTEGER,
                breadcrumb TEXT
            )
        ''')
        self.connection.commit()
        spider.logger.info(f"Database ready: {self.db_path}")

    def close_spider(self, spider):
        if self.conn:
            self.conn.close()
            spider.logger.info("Database closed")

    def process_item(self, item, spider):
        try:
            self.cursor.execute('''
                INSERT OR REPLACE INTO books (
                    url, title, upc, price, instock, stock,
                    book_description, rating, image,
                    number_of_reviews, breadcrumb
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                item.get('url'),
                item.get('title'),
                item.get('upc'),
                item.get('price'),
                item.get('instock'),
                item.get('stock'),
                item.get('book_descripion'),
                item.get('rating'),
                item.get('image'),
                item.get('number_of_reviews'),
                item.get('breadcrumb')
            ))
            self.connection.commit()
            spider.logger.info(f"Book stored in db: {item.get('title')}")
            return item
        except Exception as e:
            if e == sqlite3.IntegrityError:
                spider.logger.warning("Item already exist in the database: %s" % item)
                return item
            else:
                raise DropItem(f"Error storing item in db: {item}")