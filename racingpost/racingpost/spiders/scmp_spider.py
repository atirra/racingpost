import re

from datetime import datetime

import scrapy
from scrapy import log

from racingpost import items


class HorseSpider(scrapy.Spider):

    name = 'scmp'
    count_all_horse_requests = 0
    count_unique_horse_request = 0
    code_set = set()

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
        log.msg('*********************************************************', level=log.INFO)
        log.msg(horsecodes, level=log.INFO)
        log.msg(horsenames, level=log.INFO)
        HorseSpider.count_all_horse_requests += len(zip(horsecodes, horsenames))
        log.msg('HorseSpider.count_all_horse_requests', level=log.INFO)
        log.msg(HorseSpider.count_all_horse_requests, level=log.INFO)
        for code_dirty, horsename in zip(horsecodes, horsenames):
            meta_dict['horsename'] = horsename
            code = re.match(code_regexp, code_dirty).groupdict()['code']
            self.code_set.add(code)
            log.msg('-------------------------------------------------', level=log.INFO)
            log.msg(('code_set', len(self.code_set)), level=log.INFO)
            request = scrapy.Request(url_mask.format(code), callback=self.parse_horse)
            request.meta.update(meta_dict)
            yield request

    @staticmethod
    def get_td_ind(tr, index):

        ind = 0
        result_ind = 0
        for i, td in enumerate(tr.xpath('td'), 1):
            colspan = td.xpath('self::td/@colspan').extract()
            ind += colspan and int(colspan[0]) or 1
            if index <= ind:
                result_ind = i
                break

        return result_ind

    def parse_horse(self, response):

        
        HorseSpider.count_unique_horse_request += 1
        log.msg(('HorseSpider.count_unique_horse_request', HorseSpider.count_unique_horse_request), level=log.INFO)

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
        get_td_text = lambda tr, ind: tr.xpath('td[{}]//font/text()'.format(
            self.get_td_ind(tr, ind))).extract()[0]
        for tr in line_selector:
            prevrun_date_str = tr.xpath('td[1]//a/text()').extract()[0]
            prevrun_date_ = datetime.strptime(prevrun_date_str, '%d-%m-%y')
            if prevrun_date_ < response.meta['racedate']:
                prevrun_date.append(prevrun_date_)
                prevrun_dist.append(get_td_text(tr, 4))
                prevrun_sectimes.append(get_td_text(tr, 17))
                prevrun_horsewt.append(get_td_text(tr, 21))
                prevrun_rt.append(get_td_text(tr, 22))
                prevrun_oddsON.append(get_td_text(tr, 23))
                prevrun_oddsLast.append(get_td_text(tr, 24))

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
    