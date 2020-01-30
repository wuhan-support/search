from scrapy import Spider
from scrapy.http import Response, Request
from src.items import NewsItem
from datetime import date
import re

p1 = re.compile('"(.*)"')


class NewsSpider(Spider):
  name = 'news'

  def __init__(self, time=None, *args, **kwargs):
    super(NewsSpider, self).__init__(*args, **kwargs)
    if time == None:
      month = '%0.2d' % date.today().month
      day = '%0.2d' % date.today().day
    else:
      month = time[0:2]
      day = time[2:4]
    self.start_urls = [
        'http://paper.people.com.cn/rmrb/html/2020-%s/%s/nbs.D110000renmrb_01.htm' % (
            month, day),
        'http://www.xinhuanet.com/whxw.htm',
        'http://news.cctv.com/special/jjxxfyfk/']

  def parse(self, res: Response):
    if 'rmrb' in res.url:
      base = res.url.rsplit('/', 1)[0]
      time = '-'.join(base.rsplit('/', 2)[1:3])
      yield from self.parseRMRB1(res, base, time)
    elif 'xinhua' in res.url:
      yield from self.parseXHS(res)
    elif 'cctv' in res.url:
      yield from self.parseCCTV(res)

  def parseRMRB1(self, res: Response, base, time):
    yield from self.parseRMRB2(res, base, time)
    for href in res.xpath('//a[@id="pageLink" and not(starts-with(@href,"./"))]/@href'):
      yield Request(base + '/' + href.get(), callback=self.parseRMRB2, cb_kwargs={'base': base, 'time': time})

  def parseRMRB2(self, res: Response, base, time):
    for a in res.xpath('//a[starts-with(@href,"nw")]'):
      item = NewsItem()
      item['date'] = time
      item['src'] = '人民日报'
      item['link'] = base + '/' + a.xpath('@href').get()
      title = a.xpath('div/text()').get()
      if title == None:
        title = a.xpath('script/text()').get()
        if title != None:
          title = p1.findall(title)[0]
        else:
          continue
      item['title'] = title.strip()
      yield item

  def parseXHS(self, res: Response):
    for li in res.xpath('//div[@id="hideData"]/ul/li'):
      item = NewsItem()
      item['date'] = li.xpath('span/text()').get()
      item['src'] = '新华社'
      item['link'] = li.xpath('h3/a/@href').get()
      item['title'] = li.xpath('h3/a/text()').get()
      yield item

  def parseCCTV(self,res: Response):
    for a in res.xpath('//ul[@class="ul_title_list"]/li/a'):
      item = NewsItem()
      link = a.xpath('@href').get()
      item['date'] = '-'.join(link.rsplit('/',4)[1:4])
      item['src'] = '央视新闻'
      item['link'] = link
      item['title'] = a.xpath('text()').get()
      yield item

  
