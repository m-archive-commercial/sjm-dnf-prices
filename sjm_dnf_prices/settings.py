# Scrapy settings for sjm_dnf_prices project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import pathlib
from os.path import abspath

SETTINGS_PATH = pathlib.Path(abspath(__file__))
PROJECT_DIR = SETTINGS_PATH.parent
DATA_DIR = PROJECT_DIR / 'data'
DATA_SOURCE_DIR = DATA_DIR / "source"

BOT_NAME = 'sjm_dnf_prices'

SPIDER_MODULES = ['sjm_dnf_prices.spiders']
NEWSPIDER_MODULE = 'sjm_dnf_prices.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# The download delay setting will honor only one of:
CONCURRENT_REQUESTS = 1
# CONCURRENT_REQUESTS_PER_DOMAIN = 1
# CONCURRENT_REQUESTS_PER_IP = 1
DOWNLOAD_DELAY = 5 + 1

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs

# 在headers中设置cookie时，要把这里的cookie给设置False， see: https://zhuanlan.zhihu.com/p/337212121
# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    'Accept'         : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en',
    # dnf.session.id 是 price 爬取的必要参数
    'Cookie'         : 'dnf.session.id=37f00fd41fc94ccfbcb358cd0d4d4f84;'
}

RETRY_ENABLED = False


# ref: https://doc.scrapy.org/en/latest/topics/spider-middleware.html?highlight=allowed_http#httperror-allowed-codes
HTTPERROR_ALLOWED_CODES = [500]

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'sjm_dnf_prices.middlewares.SjmDnfPricesSpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
# DOWNLOADER_MIDDLEWARES = {
#    'sjm_dnf_prices.middlewares.SjmDnfPricesDownloaderMiddleware': 543,
# }

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure itemInPrice pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
MONGO_URI = "localhost"
MONGO_DATABASE = "sjm_dnf_prices"

ITEM_PIPELINES = {
    'sjm_dnf_prices.pipelines.MongoPipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
