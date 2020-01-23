import asyncio
import aiohttp
from bs4 import BeautifulSoup
import re

#异步网页爬虫,aiohttp方式

class AsnycGrabWeb:
    max_threads=20      #并发度
    max_level=2         #深度
    proxy="http://127.0.0.1:1080"

    root_urls={}
    loop=None
    con_count=0
    already_urls={}
    def __init__(self, url_list,root_url=None,level=0,loop=None):
        if AsnycGrabWeb.loop==None:
            AsnycGrabWeb.loop=loop
        self.urls = url_list
        self.root_url=root_url
        self.level=level
        if root_url==None:
            self.level=0
            for x in url_list:
                AsnycGrabWeb.root_urls[x]=0
        self.results = {}
        self.max_threads = AsnycGrabWeb.max_threads

    async def get_body(self, url):
        #加连接数限制
        while AsnycGrabWeb.con_count>280:
            await asyncio.sleep(1, loop=AsnycGrabWeb.loop)
        try:
            AsnycGrabWeb.con_count = AsnycGrabWeb.con_count + 1
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=30,proxy=AsnycGrabWeb.proxy) as response:
                    assert response.status == 200
                    html = await response.read()
                    return response.url, html
        finally:
            AsnycGrabWeb.con_count=AsnycGrabWeb.con_count-1


    async def get_results(self, inputurl):
        try:

            url, html = await self.get_body(inputurl)
            soup = BeautifulSoup(html, 'html.parser')

            urls = soup.findAll(name='a')
            suburls=[]
            for u in urls:
                nurl=u.get('href',"")
                if re.match(r'^https?:/{2}\w.+$', nurl):
                    #print(nurl)
                    if nurl not in AsnycGrabWeb.already_urls.keys():
                        suburls.append(nurl)
                        AsnycGrabWeb.already_urls[nurl]=1
            title = soup.find('title').get_text()
            if title:
                print(self.root_url, title, self.level)
            if len(suburls)>0:
                sub_async_example=AsnycGrabWeb(suburls,root_url = inputurl if self.root_url==None else self.root_url,level=self.level+1)
                sub_async_example.eventloop()

        except Exception as e:
            print(e)



    async def handle_tasks(self, task_id, work_queue):
        while not work_queue.empty():
            current_url = await work_queue.get()
            try:
                task_status = await self.get_results(current_url)
            except Exception as e:
                print(e)

    def eventloop(self):
        if self.level>=AsnycGrabWeb.max_level:
            return
        q = asyncio.Queue()
        [q.put_nowait(url) for url in self.urls]
        tasks = [self.handle_tasks(task_id, q, ) for task_id in range(self.max_threads)]
        AsnycGrabWeb.loop.create_task(asyncio.wait(tasks))
        if self.root_url != None:
            if AsnycGrabWeb.root_urls[str(self.root_url)]<self.level:
                AsnycGrabWeb.root_urls[str(self.root_url)]=self.level

    @staticmethod
    async def isallok():
        while True:
            await asyncio.sleep(5,loop=AsnycGrabWeb.loop)
            if len(AsnycGrabWeb.root_urls)>0:
                #print(min(AsnycGrabWeb.root_urls.values()))
                print(AsnycGrabWeb.con_count)
                print(AsnycGrabWeb.root_urls)
                if min(AsnycGrabWeb.root_urls.values())>=AsnycGrabWeb.max_level-1:
                    if AsnycGrabWeb.con_count==0:
                        break

if __name__ == '__main__':

    loop = asyncio.get_event_loop()

    async_example = AsnycGrabWeb(['https://baidu.com','https://126.com'],loop=loop)
    async_example.eventloop()

    loop.run_until_complete(AsnycGrabWeb.isallok())

    print(async_example.results)