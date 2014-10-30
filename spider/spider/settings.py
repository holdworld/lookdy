# -*- coding: utf-8 -*-

# Scrapy settings for spider project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'spider'

SPIDER_MODULES = ['spider.spiders']
NEWSPIDER_MODULE = 'spider.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'spider (+http://www.yourdomain.com)'

#random delay [1,2] second down
DOWNLOAD_DELAY = 2
RANDOMIZE_DOWNLOAD_DELAY = True

DOWNLOADER_MIDDLEWARES = {
	'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware':None,
	'spider.fake_agent.FakeAgent':400
}