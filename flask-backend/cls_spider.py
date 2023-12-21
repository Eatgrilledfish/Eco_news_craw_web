import requests
import queue
import re
from lxml import etree
import threading
import fake_user_agent as fake_user_agent
import useful_functions
import logging
from datetime import datetime
import pymysql

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Use a fake user agent
headers = fake_user_agent.useragent_random()

# Crawling thread
class MyThread(threading.Thread):
    processed_count = 0
    def __init__(self, url, shutdown_event):
        super(MyThread, self).__init__()
        self.url = url
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
                self.process_url(self.url)
                break  # 如果process_url执行完毕，则跳出循环
            except Exception as e:
                logger.error(f"An error occurred in the thread: {e}")
                break  # 如果发生异常，也跳出循环



    def process_url(self, url):
        try:
            item = {}
            logger.info(f'Fetching {url}')
            response = requests.get(url, headers=headers, timeout=10)

            html = etree.HTML(response.text)
            results = html.xpath('//div[contains(@class,"telegraph-list")]')
            # for i in keyword:
            #     keyword = i.xpath('.//a[contains(@class,"label-item")]//text()')
            #     print('this is keyword', keyword)
            # Find all anchor tags with the 'label-item' class
            for result in results:
                item['url'] = 'https://www.cls.cn/telegraph'
                text_content = result.xpath('.//div[contains(@class,"telegraph-content-box")]//text()')
                if len(text_content) < 3 and len(text_content) != 0:
                    # 假设text_content[0]是 "21:25:27"
                    time_str = text_content[0]
                    # 获取当前日期
                    current_date = datetime.now().date()
                    # 将日期和时间拼接成一个字符串
                    publish_time = '{} {}'.format(current_date, time_str)
                    item['publish_time'] = publish_time
                    item['title'] = 'None'
                    item['content'] = text_content[1]
                elif len(text_content) == 0:
                    pass
                else:
                    # 假设text_content[0]是 "21:25:27"
                    time_str = text_content[0]
                    # 获取当前日期
                    current_date = datetime.now().date()
                    # 将日期和时间拼接成一个字符串
                    publish_time = '{} {}'.format(current_date, time_str)
                    item['publish_time'] = publish_time
                    item['title'] = re.sub(r'[&#8203;``【oaicite:1】``&#8203;]', '', text_content[1])
                    content = text_content[2]
                    content = re.sub(r'\s+', ' ', content)
                    content = re.sub(r'　+', ' ', content)
                    item['content'] = content
                keyword = result.xpath('.//a[contains(@class,"label-item")]//text()')
                item['key_word'] = keyword
                item['key_word'] = ', '.join(item['key_word'])
                item['source'] = '财联社电报'

                self.save(item)
            self.shutdown_event.set()

            # Print the response text to check if the URLs are correct
        except requests.RequestException as e:
            logger.error(f"Request failed for {url}: {e}")

    def save(self, item):
        try:
            # Check if the title already exists in the database
            check_title_sql = "SELECT COUNT(*) FROM news_eco WHERE publish_time = %s"
            self.cursor.execute(check_title_sql, (item['publish_time'],))
            if self.cursor.fetchone()[0] == 0:
                # If the title does not exist, insert the new record
                self.cursor.execute(self.sql, [item['title'], item['publish_time'], item['content'], item['url'], item['key_word'], item['source']])
                self.cnn.commit()
                logger.info(f"Inserted new record with publish_time: {item['publish_time']}")
            else:
                # If the title exists, log that the record already exists
                logger.info(f"Record with publish_time: {item['publish_time']} already exists in the database.")
        except pymysql.MySQLError as e:
            logger.error(f"Failed to save data: {e}")


# Crawler run program
def run():
    shutdown_event = threading.Event()  # Event to signal when threads should close
    url = 'https://www.cls.cn/telegraph'
    thread = MyThread(url, shutdown_event)
    thread.start()
    thread.join()


if __name__ == "__main__":
    run()
