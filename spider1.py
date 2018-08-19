# // 生产者和消费者模式，
# 生产者： 将所需的数据爬取到，消费者，将数据写入csv 文件中
#
from lxml import etree
import requests
from queue import Queue
import threading
import csv


class BSSpider(threading.Thread):

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
    }

    def __init__(self,page_queue,info_queue,*args,**kwargs):
        super(BSSpider, self).__init__(*args,**kwargs)
        self.page_queue = page_queue
        self.info_queue = info_queue
        self.domain = "http://www.budejie.com"

    def run(self):
        while True:
            if self.page_queue.empty():
                break
            url = self.page_queue.get()
            resp = requests.get(url, headers=self.headers)
            text = resp.text
            html = etree.HTML(text)
            detail_urls = html.xpath("//div[@class='j-r-list-c-img']//a/@href")
            full_url = ""
            for per_url in detail_urls:
                full_url = self.domain + per_url

            img_infos = html.xpath("//div[@class='j-r-list-c-img']//img")
            for each in img_infos:
                title = each.get('title').strip()
                img_url = each.get('data-original')
                # 数据入队列
                self.info_queue.put((title,full_url,img_url))
                # print(title,full_url,img_url)
                # print(self.info_queue.qsize())
            print('完成一页的爬取！')

class BSWrite(threading.Thread):
    def __init__(self,info_queue,writer,gLock,*args,**kwargs):
        super(BSWrite, self).__init__(*args,**kwargs)
        self.info_queue = info_queue
        self.writer = writer
        self.gLock = gLock
    # 保存数据要动点脑袋
    # 创建好writer 和 Lock 对象
    def run(self):
        while True:
            try:
                infos = self.info_queue.get(timeout=40)
                title, full_url, img_url = infos
                self.gLock.acquire()
                self.writer.writerow((title, full_url, img_url))
                self.gLock.release()
                print('保存一条')
            except:
                break


def main():
    page_queue = Queue(10)
    info_queue = Queue(500)

    gLock = threading.Lock()

    fp = open('infos.csv',"w",encoding="utf-8",newline="")
    writer = csv.writer(fp)

    writer.writerow(['title','full_url','img_url'])

    for i in range(1,11):
        url = "http://www.budejie.com/%s" % i
        page_queue.put(url)


    for i in range(5):
        b = BSSpider(page_queue,info_queue)
        b.start()

    for i in range(5):
        t = BSWrite(info_queue,writer,gLock)
        t.start()
# 文件用excel 打开乱码，因此进行测试
def text():
    with open('infos.csv',"r",encoding="utf-8") as fp:
        reader = csv.reader(fp)
        next(reader)
        for x in reader:
            print(x)

if __name__ == '__main__':
    # main()
    text()
