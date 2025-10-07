# -*- coding: utf-8 -*-
"""
Scrapy settings for RAG Knowledge System

For simplicity, this file contains only settings considered important or
commonly used. You can find more settings consulting the documentation:

    https://docs.scrapy.org/en/latest/topics/settings.html
"""

import os
from dotenv import load_dotenv

load_dotenv()

BOT_NAME = 'rag_knowledge_scraper'

SPIDER_MODULES = ['src.scraping.spiders']
NEWSPIDER_MODULE = 'src.scraping.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure a delay for requests for the same website (default: 0)
DOWNLOAD_DELAY = float(os.getenv('SCRAPY_DELAY', 1))

# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 8
CONCURRENT_REQUESTS_PER_IP = 4

# Disable cookies (enabled by default)
COOKIES_ENABLED = True

# Disable Telnet Console (enabled by default)
TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': os.getenv('SCRAPY_USER_AGENT', 'RAG-Knowledge-Bot 1.0')
}

# Enable or disable spider middlewares
SPIDER_MIDDLEWARES = {
    'src.scraping.middlewares.CustomSpiderMiddleware': 543,
}

# Enable or disable downloader middlewares
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'src.scraping.middlewares.RotateUserAgentMiddleware': 400,
    'src.scraping.middlewares.ProxyMiddleware': 410,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': 550,
    'src.scraping.middlewares.CustomRetryMiddleware': 551,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 750,
}

# Enable or disable extensions
EXTENSIONS = {
    'scrapy.extensions.telnet.TelnetConsole': None,
    'src.scraping.extensions.StatsExtension': 500,
}

# Configure item pipelines
ITEM_PIPELINES = {
    'src.scraping.pipelines.ValidationPipeline': 300,
    'src.scraping.pipelines.DuplicatesPipeline': 400,
    'src.scraping.pipelines.CleaningPipeline': 500,
    'src.scraping.pipelines.DatabasePipeline': 600,
    'src.scraping.pipelines.FileExportPipeline': 700,
}

# Enable autothrottling
AUTOTHROTTLE_ENABLED = os.getenv('SCRAPY_AUTOTHROTTLE_ENABLED', 'true').lower() == 'true'
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 60
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
AUTOTHROTTLE_DEBUG = False

# HTTP caching
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 3600
HTTPCACHE_DIR = 'httpcache'
HTTPCACHE_IGNORE_HTTP_CODES = [503, 504, 505, 500, 403, 404, 408, 429]

# Retry settings
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]

# Concurrent requests
CONCURRENT_REQUESTS = int(os.getenv('SCRAPY_CONCURRENT_REQUESTS', 16))

# Download timeout
DOWNLOAD_TIMEOUT = 180

# Enable and configure HTTP2
DOWNLOAD_HANDLERS = {
    "http": "scrapy.core.downloader.handlers.http.HTTPDownloadHandler",
    "https": "scrapy.core.downloader.handlers.http.HTTPSDownloadHandler",
}

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.path.join(os.getenv('LOGS_DIR', './logs'), 'scrapy.log')

# Request fingerprinting
REQUEST_FINGERPRINTER_IMPLEMENTATION = '2.7'

# Twisted reactor
TWISTED_REACTOR = 'twisted.internet.asyncioreactor.AsyncioSelectorReactor'

# Feed exports
FEED_EXPORT_ENCODING = 'utf-8'

# Memory usage extension
MEMUSAGE_ENABLED = True
MEMUSAGE_LIMIT_MB = 2048
MEMUSAGE_WARNING_MB = 1024

# Closespider settings
CLOSESPIDER_TIMEOUT = 3600  # 1 hour
CLOSESPIDER_ITEMCOUNT = 10000
CLOSESPIDER_PAGECOUNT = 50000
CLOSESPIDER_ERRORCOUNT = 100

# DNS settings
DNSCACHE_ENABLED = True
DNSCACHE_SIZE = 10000
DNS_TIMEOUT = 60

# Media pipeline settings
MEDIA_ALLOW_REDIRECTS = True
IMAGES_STORE = os.path.join(os.getenv('DATA_DIRECTORY', './data'), 'images')
FILES_STORE = os.path.join(os.getenv('DATA_DIRECTORY', './data'), 'files')

# Custom settings for different environments
if os.getenv('ENVIRONMENT') == 'production':
    # Production settings
    CONCURRENT_REQUESTS = 32
    CONCURRENT_REQUESTS_PER_DOMAIN = 16
    DOWNLOAD_DELAY = 0.5
    AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0
    
elif os.getenv('ENVIRONMENT') == 'development':
    # Development settings
    CONCURRENT_REQUESTS = 8
    CONCURRENT_REQUESTS_PER_DOMAIN = 4
    DOWNLOAD_DELAY = 2
    AUTOTHROTTLE_DEBUG = True