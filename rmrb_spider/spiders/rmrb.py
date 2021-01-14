import scrapy
from scrapy import signals
from scrapy import Request


class RmrbSpider(scrapy.Spider):
    name = "rmrb"
    allowed_domains = ["weibo.cn"]

    # 要爬取的微博账号
    start_urls = ["https://weibo.cn/2803301701/profile?page=1"]

    # 这里替换成登陆 https://weibo.cn 后的自己的Cookie
    # 打开调试模式能看到，或者网上查下获取Cookie的方法
    cookies = {
        "_T_WM": "93522076797",
        "MLOGIN": "0",
        "M_WEIBOCN_PARAMS": "luicode%3D10000011%26lfid%3D1076032803301701",
        "SUB": "_2A25y-oQpDeRhGeBO6lYT8CjFyziIHXVuBCxhrDV6PUJbkdAKLU_wkW1NSiEckgVENn4Fvllph2SEtrla5Z6ScuF4",
        "SCF": "ArUky73dtNj3qR7hHEVDiJ3pX4yXs19Z7b_VG-qRCaMPR7eAzOYmOfveNKeWkwtn6o_hzZmk5an4t4OCh-d726M.",
        "SSOLoginState": "1610544239",
    }

    # 最多爬取的微博的页数
    max_tweet_pages = 5

    # 对于每条微博，爬取的最大的热门评论页数
    max_comment_pages = 5

    def start_requests(self):
        for url in self.start_urls:
            yield Request(
                url,
                cookies=self.cookies,
                callback=self.parse_tweet_page,
            )

    def parse_tweet_page(self, response):
        first_page_comment_urls = response.css(
            ".c a.cc:nth-last-child(3)::attr(href)"
        ).extract()
        for url in first_page_comment_urls:

            # https://weibo.cn/comment/JD27s6duu?uid=2803301701&rl=1#cmtfrm
            print("First comment page url: ", url)

            # JD27s6duu
            tweet_id = url.split("comment/")[1].split("?uid")[0]

            # https://weibo.cn/comment/hot/JD27s6duu
            tweet_hot_comments_url = "https://weibo.cn/comment/hot/" + tweet_id

            yield Request(
                tweet_hot_comments_url,
                cookies=self.cookies,
                callback=self.parse_comment_page,
            )

        elements = response.css(
            ".pa div:nth-child(1) a:nth-child(1)::attr(href)"
        ).extract()

        # 如果有下一页
        if elements:
            # /2803301701/profile?page=2
            next_tweet_page_url = elements[0]

            # 2
            page_num = int(next_tweet_page_url.split("page=")[1])

            if page_num <= self.max_tweet_pages:
                print("Next tweet page url: ", next_tweet_page_url)
                yield Request(
                    "https://weibo.cn"
                    + next_tweet_page_url,  # https://weibo.cn/2803301701/profile?page=2
                    cookies=self.cookies,
                    callback=self.parse_tweet_page,
                )

    def parse_comment_page(self, response):
        comment_contents = response.css(".c .ctt::text").extract()
        for content in comment_contents:
            yield {"url": response.urljoin(""), "content": content}

        elements = response.css(
            ".pa div:nth-child(1) a:nth-child(1)::attr(href)"
        ).extract()  # TODO 判断是否还有下一页

        # 如果有下一页
        if elements:
            # /comment/hot/JD27s6duu?page=2
            next_page_comment_url = elements[0]

            # 2
            page_num = int(next_page_comment_url.split("page=")[1])

            if page_num <= self.max_comment_pages:
                yield Request(
                    "https://weibo.cn"
                    + next_page_comment_url,  # https://weibo.cn/comment/hot/JD27s6duu?page=2
                    cookies=self.cookies,
                    callback=self.parse_comment_page,
                )
