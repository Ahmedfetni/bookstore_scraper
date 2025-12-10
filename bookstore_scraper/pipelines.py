# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy import signals
from scrapy import logger


class ValidationPipeline:
    def process_item(self, item, spider):
        
        if not item.get('url'):
            raise DropItem("Missing url in %s" % item)
        
        if not item.get('title'):
            raise DropItem("Missing title in %s" % item)
        
        return item
    
class DataBasePipeline:

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
     
    def open_spider(self, spider):
        import sqlite3
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
        logger.info(f"Database ready: {self.db_path}")

    def close_spider(self, spider):
        if self.conn:
            self.conn.close()
            logger.info("📊 Database closed")