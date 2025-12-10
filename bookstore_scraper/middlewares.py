from scrapy import signals
import logging
import random

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import requests

class BookstoreScraperSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    async def process_start(self, start):
        # Called with an async iterator over the spider start() method or the
        # maching method of an earlier spider middleware.
        async for item_or_request in start:
            yield item_or_request

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class BookstoreScraperDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


# a new middleware to rotate proxies 

logger = logging.getLogger(__name__)

class ValidatingProxyMiddleware:
    def __init__(self, proxy_list, test_url="https://example.com",test_timeout=2):
        self.original_proxies = list(proxy_list)
        self.proxies = list(proxy_list)
        self.test_url = test_url
        self.test_timeout = test_timeout
        logger.info(f"ValidatingProxyMiddleware started: {len(self.proxies)} proxies")

    @classmethod
    def from_crawler(cls, crawler):
        proxy_list = crawler.settings.getlist("PROXY_LIST",[])
        middleware = cls(proxy_list)
        # so when the spider opens we launch the middleware validation
        crawler.signals.connect(middleware.spider_opened, signal=signals.spider_opened)
        return middleware
    
    def process_request(self, request, spider):
        if not self.proxies:
            logger.warning("failed to load proxies list of proxies is possibly empty")
            return
        
        proxy = random.choice(self.proxies)
        request.meta['proxy'] = f"http://{proxy}"
        request.meta.setdefault('proxy_retry', 0)
        logger.info(f'Testing proxy {proxy} for {request.url}')
    
    # letting normal responses pass through
    def process_response(self, request, response, spider):
        return response
    
    # handling the case where the request fails due to the proxy not working
    def process_exception(self, request, exception, spider):
        proxy = request.meta.get('proxy')
        if proxy:
            proxy_address = proxy.replace("http://","")
            retry_count = request.meta.get('proxy_retry',0)
            if retry_count <= 2 :
                logger.warning(f"Proxy {proxy_address} failed with exception {exception}. Retrying ({retry_count+1}/2)")
                new_req = request.copy()
                new_req.meta['proxy_retry'] = retry_count + 1
                return new_req
            else:
                logger.debug(f"Proxy {proxy_address} removed from list after 2 failed attempts.")
                if proxy_address in self.proxies:
                    self.proxies.remove(proxy_address)
        return None

    # call to test proxiest at the start (upfront)
    def spider_opened(self, spider):
        valid = []
        # go throuw every proxy given 
        for proxy in self.original_proxies:
            try:
                response = requests.get(self.test_url, proxies={"http":f"http://{proxy}","https":f"http://{proxy}"}, timeout=self.test_timeout)
                if response.status_code == 200:
                    valid.append(proxy)
                    logger.info(f"Proxy {proxy} is valid.")
                else:
                    logger.warning(f"Proxy {proxy} returned status code {response.status_code}.")
            except Exception as e:
                logger.warning(f"Proxy {proxy} failed validation with exception: {e}")
        spider.proxies = valid
        logger.info(f"Validation complete. {len(self.proxies)} valid proxies found.")


class ProxyRotationMiddleware:

    
    # send request throw a proxy 
    def process_request(self, request, spider):
        if spider.proxies :
            proxy = random.choice(spider.proxies)
            request.meta['proxy'] = proxy
            logger.info(f'Using proxy {proxy} for {request.url}')
        else:
            logger.warning("ProxyRotationMiddleware: No proxies in use")
    
    def process_response(self, request, response, spider):
        return response

class HeaderRoatationMiddleware:
    
    def __init__(self, user_agents):
        self.user_agents = user_agents or [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',

        ]

        logger.deug(f"HeaderRoatationMiddleware {len(self.user_agents)} user agents.")

    @classmethod
    def from_crawler(cls, crawler):
        user_agents = crawler.settings.getlist("USER_AGENTS",[])
        return cls(user_agents)
    
    def process_request(self, request, spider):
        user_agent = random.choice(self.user_agents)
        request.headers['User-Agent'] = user_agent
        request.headers['Accept-Language'] = 'en-US,en;q=0.9'
        request.headers['Accept-Encoding'] = 'gzip, deflate, br'
        request.headers['Connection'] = 'keep-alive'
        request.headers['Upgrade-Insecure-Requests'] = '1'
        logger.info(f'HeaderRoatationMiddleware: Using User-Agent {user_agent}')
        # for modern antibot measures
        request.headers['sec-ch-ua'] = '"Not_A Brand";v="8", "Chromium";v="120"'
        request.headers['sec-ch-ua-mobile'] = '?0'
        request.headers['sec-ch-ua-platform'] = '"Windows"'
        request.headers['Sec-Fetch-Dest'] = 'document'
        request.headers['Sec-Fetch-Mode'] = 'navigate'
        request.headers['Sec-Fetch-Site'] = 'none'
        request.headers['Sec-Fetch-User'] = '?1'


    
