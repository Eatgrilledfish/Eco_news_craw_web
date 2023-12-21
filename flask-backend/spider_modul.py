import requests
import queue
import re
from lxml import etree
import threading
import fake_user_agent as fake_user_agent
import useful_functions
import logging
import pymysql

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Use a fake user agent
headers = fake_user_agent.useragent_random()

# Crawling thread
class MyThread(threading.Thread):
    processed_count = 0
    def __init__(self, url_queue, shutdown_event):
        super(MyThread, self).__init__()
        self.urls = []
        self.url_queue = url_queue
        self.shutdown_event = shutdown_event
        # 连接Mysql数据库
        self.cnn = pymysql.connect(host='127.0.0.1', user='eco_user', password='root', port=3306, database='news_with_keyword',
                                   charset='utf8')
        self.cursor = self.cnn.cursor()
        self.sql = 'INSERT INTO news_eco(title, publish_time, content, url, key_word, source) values(%s, %s, %s, %s, %s, %s)'
        
        # 获取已爬取的url数据并写入列表，用于判断
        self.fetch_existing_urls()

    def fetch_existing_urls(self):
        try:
            sql = 'SELECT url FROM news_eco'
            self.cursor.execute(sql)
            self.urls = [url[0] for url in self.cursor.fetchall()]
        except pymysql.MySQLError as e:
            logger.error(f"Database error: {e}")

    def run(self):
        while not self.shutdown_event.is_set():
            try:
                self.spider()
                break
            except Exception as e:
                logger.error(f"An error occurred in the thread: {e}")
                break

    def spider(self):
        while not self.url_queue.empty() and not self.shutdown_event.is_set():
            url = self.url_queue.get()
            if self.check_url(url):
                self.process_url(url)
                # Increment the processed count
                MyThread.processed_count += 1
                # Check if we have reached 100 URLs processed
                if MyThread.processed_count >= 10:
                    logger.info('Reached 10 URLs, shutting down.')
                    self.shutdown_event.set()
                    break

    def process_url(self, url):
        try:
            item = {}
            logger.info(f'Fetching {url}')
            response = requests.get(url, headers=headers, timeout=10)
            response.encoding = "utf-8"
            html = etree.HTML(response.text)
            results = html.xpath('//ul/li[contains(@class,"left left-main")]')
            for result in results:
                item['url'] = url
                item['title'] = result.xpath('./h3/text()')[0]
                item['publish_time'] = result.xpath('./div[contains(@class,"time")]/span[1]/text()')[0]
                content = result.xpath('./div[contains(@class,"content")]/p/text()')
                content = ''.join(content)
                content = re.sub('\s', '', content)
                item['content'] = content
                key_word = result.xpath("//div[@class='key-word fix mt15']/a/text()")
                key_word = ",".join(key_word)
                if not key_word:
                    key_word = useful_functions.get_keyword_from_content(content)
                item['key_word'] = key_word
                item['souce'] = '中国观察者网'
            self.save(item)
            self.shutdown_event.set()

            # Print the response text to check if the URLs are correct
        except requests.RequestException as e:
            logger.error(f"Request failed for {url}: {e}")

    def save(self, item):
        try:
            self.cursor.execute(self.sql, [item['title'],  item['publish_time'], item['content'], item['url'], item['key_word'], item['souce']])
            self.cnn.commit()
        except pymysql.MySQLError as e:
            logger.error(f"Failed to save data: {e}")

    def check_url(self, url):
        # 查看数据库中是否存在当前爬取的url，如果存在则放弃爬取
        if url in self.urls:
            logger.info(f'{url}已存在')
            return False
        else:
            self.urls.append(url)
            return True

# Add extracted URLs to the queue
def add_urls(urls, queue):
    for url in urls:
        if "#comment" not in url and "economy" in url:
            full_url = 'https://www.guancha.cn' + url
            queue.put(full_url)
            print(f"Added URL: {full_url}")  # Print each URL added to the queue

# Extract URLs from the economy section
def get_url(queue):
    url = 'https://www.guancha.cn/economy'
    response = requests.get(url, headers=headers).text
    html = etree.HTML(response)
    # Extract URLs and print them to verify
    article_urls = html.xpath("//div[@class='main content-main']//a/@href")
    add_urls(article_urls, queue)

# Crawler run program
def run():
    shutdown_event = threading.Event()  # Event to signal when threads should close
    url_queue = queue.Queue()
    get_url(url_queue)  # Changed to just call get_url

    threads = []
    for i in range(1):  # Reduced number of threads for simplicity
        thread = MyThread(url_queue, shutdown_event)
        threads.append(thread)
        thread.start()

        for thread in threads:
            thread.join()  # Wait for all threads to finish

if __name__ == "__main__":
    run()
