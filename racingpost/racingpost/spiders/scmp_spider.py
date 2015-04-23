import scrapy

from racingpost import items


class HorseSpider(scrapy.Spider):

    name = 'scmp'

    def __init__(self, year, *args, **kwargs):
        assert len(year) == 4 and year[:2] == '20'
        super(HorseSpider, self).__init__(*args, **kwargs)
        self.year = year
        self.start_urls = [
            'http://racing.scmp.com/login.asp'
        ]

    def parse(self, response):
        return scrapy.http.FormRequest.from_response(
            response,
            formdata={'Login': 'luckyvince', 'Password': 'invader'},
            callback=self.after_login,
        )

    def after_login(self, response):
        request = None
        if 'Please enter your login and passowrd correctly' in response.body:
            self.log('Login failed', level=scrapy.log.ERROR)
        else:
            url = 'http://racing.scmp.com/Resultspro/CalendarList.asp'
            request = scrapy.http.FormRequest(
                url,
                formdata={'CurrentPeriod': self.year},
                callback=self.parse_racing_set,
            )
        return request

    def parse_racing_set(self, response):
        race_paths = response.xpath('//table//tr[@bgcolor="white"]/td[3]//a/'
            '@href').extract()
        for path in race_paths:
            url = 'http://racing.scmp.com/Resultspro/{}'.format(path)
            yield scrapy.Request(url, callback=self.parse_race)

    def parse_race(self, response):

        racename = response.xpath('(//table//table//table)[2]//td/font/b/'
            'text()').extract()[0]
        horsenames = response.xpath('(//table//table//table//table)[1]//td[3]'
            '//a/text()').extract()

        horsecodes = response.xpath('(//table//table//table//table)[1]//td[3]//text()[ not(ancestor::a) and preceding::a[contains(@onclick, "MarkYourCard")] ]').extract()
        #use horse codes to get horsehistory
        jb_comment = ''.join(response.xpath("(//font[child::b[contains(text(),'Phillip Woo')]]//text())[position()>2]").extract())


        return items.ScmpHorseItem(
            racename=racename,
            horsenames=horsenames,
            jb_comment=jb_comment,
        )

    ##URL http://racing.scmp.com/racecardpro/HorseHistory/HorseHistory{HORSECODE}.asp    
    ## http://racing.scmp.com/racecardpro/HorseHistory/HorseHistoryN254.asp
    