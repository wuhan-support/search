from scrapy import Item, Field


class NewsItem(Item):
  date = Field()
  src = Field()
  title = Field()
  link = Field()
  pass
