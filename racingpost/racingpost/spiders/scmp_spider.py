import re

from datetime import datetime

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

        racedate_dirty = response.xpath('(//td[@colspan="2"]/b/font/text())'
            '[1]').extract()[0].encode('utf-8')
        racedate_regexp = r'^(?P<month>[A-Z]{1}[a-z]+) (?P<day>\d{1,2}).{3}(?P<year>\d{4}).*$'
        racedate_dict = re.match(racedate_regexp, racedate_dirty).groupdict()
        racedate = datetime.strptime('{}-{}-{}'.format(racedate_dict['month'],
            racedate_dict['day'], racedate_dict['year']), '%B-%d-%Y')

        horsenames = response.xpath('(//table//table//table//table)[1]//td[3]'
            '//a/text()').extract()

        horsecodes = response.xpath('(//table//table//table//table)[1]//td[3]//text()[ not(ancestor::a) and preceding::a[contains(@onclick, "MarkYourCard")] ]').extract()
        #use horse codes to get horsehistory
        jb_comment = ''.join(response.xpath("(//font[child::b[contains(text(),'Phillip Woo') or contains(text(),'John Bell')]]//text())[position()>2]").extract())

        meta_dict = {
            'racename': racename,
            'jb_comment': jb_comment,
            'racedate': racedate,
        }
        url_mask = 'http://racing.scmp.com/racecardpro/HorseHistory/HorseHistory{}.asp'
        code_regexp = r'^ \((?P<code>\w+)\)$'
        for code_dirty, horsename in zip(horsecodes, horsenames):
            meta_dict['horsename'] = horsename
            code = re.match(code_regexp, code_dirty).groupdict()['code']
            request = scrapy.Request(url_mask.format(code), callback=self.parse_horse)
            request.meta.update(meta_dict)
            yield request

    def parse_horse(self, response):

        horsehealth = ''.join(response.xpath('//i[text()="Health : "]/../../text()'
            ).extract())

        prevrun_date = []
        prevrun_dist = []
        prevrun_sectimes = []
        prevrun_horsewt = []
        prevrun_rt = []
        prevrun_oddsON = []
        prevrun_oddsLast = []
        line_selector = response.xpath('//td[@nowrap]/font[@face="ARIAL"]/../..')
        for sel in line_selector:
            prevrun_date_str = sel.xpath('td[1]//a/text()').extract()[0]
            prevrun_date_ = datetime.strptime(prevrun_date_str, '%d-%m-%y')
            if prevrun_date_ < response.meta['racedate']:
                prevrun_date.append(prevrun_date_)
                prevrun_dist.append(sel.xpath('td[4]//font/text()').extract()[0])
                prevrun_sectimes.append(sel.xpath('td[17]/font/text()').extract()[0])
                prevrun_horsewt.append(sel.xpath('td[8]/font/text()').extract()[0])
                prevrun_rt.append(sel.xpath('td[22]/font/text()').extract()[0])
                prevrun_oddsON.append((sel.xpath('td[23]//font/text()').extract() or
                    sel.xpath('td[21]//font/text()').extract())[0])
                prevrun_oddsLast.append((sel.xpath('td[24]//font/text()').extract() or
                    sel.xpath('td[22]//font/text()').extract())[0])

        return items.ScmpHorseItem(
            racename=response.meta['racename'],
            jb_comment=response.meta['jb_comment'],
            horsename=response.meta['horsename'],
            horsehealth=horsehealth,
            prevrun_date=prevrun_date,
            prevrun_dist=prevrun_dist,
            prevrun_sectimes=prevrun_sectimes,
            prevrun_horsewt=prevrun_horsewt,
            prevrun_rt=prevrun_rt,
            prevrun_oddsON=prevrun_oddsON,
            prevrun_oddsLast=prevrun_oddsLast,
        )

    ##URL http://racing.scmp.com/racecardpro/HorseHistory/HorseHistory{HORSECODE}.asp    
    ## http://racing.scmp.com/racecardpro/HorseHistory/HorseHistoryN254.asp
    