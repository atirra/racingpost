import re

import scrapy

from racingpost import items


class HorseSpider(scrapy.Spider):

    name = 'hkjc'

    def __init__(self, date, racecoursecode, *args, **kwargs):
        assert racecoursecode in ['ST', 'HV']
        super(HorseSpider, self).__init__(*args, **kwargs)
        self.domain = 'hkjc.com'
        self.start_urls = [
            'http://racing.{domain}/racing/Info/Meeting/Results/English/Local/'
            '{date}/{racecoursecode}/1'.format(domain=self.domain, 
                date=date, racecoursecode=racecoursecode),
        ]

    def parse(self, response):
        race_paths = response.xpath('//div[@class="raceNum clearfix"]//'
            'td[position()!=last()]/a/@href').extract()
        race_urls = ['http://racing.{domain}{path}'.format(domain=self.domain, 
            path=path) for path in race_paths] + self.start_urls
        for url in race_urls:
            yield scrapy.Request(url, callback=self.parse_race)

    def parse_race(self, response):

        race_text = response.xpath('//div[@class="rowDiv15"]/div[@class='
            '"boldFont14 color_white trBgBlue"]/text()').extract()
        racenumber = None
        raceindex = None
        if race_text:
            race_regexp = '^RACE (?P<number>\d+) \((?P<index>\d+)\)$'
            race_dict = re.match(race_regexp, race_text[0]).groupdict()
            racenumber = race_dict['number']
            raceindex = race_dict['index']

        racename = response.xpath('//div[@class="rowDiv15"]//table[@class='
            '"tableBorder0 font13"]//tr[2]/td[1]/text()').extract()

        sectional_time_url = response.xpath('//div[@class="rowDiv15"]/div['
            '@class="rowDivRight"]/a/@href').extract()[0]
        request = scrapy.Request(sectional_time_url, callback=
            self.parse_sectional_time)
        meta_dict = {
            'racenumber': racenumber,
            'raceindex': raceindex,
            'racename': racename[0] if racename else None
        }
        request.meta.update(meta_dict)

        yield request

    def parse_sectional_time(self, response):

        horse_lines_selector = response.xpath('//table[@class="bigborder"]//'
            'table//a/../../..')
        sectional_time_selector = response.xpath('//table[@class='
            '"bigborder"]//table//a/../../../following-sibling::tr[1]')
        for line_selector, time_selector in zip(horse_lines_selector, 
                sectional_time_selector):

            horsenumber = line_selector.xpath('td[1]/div/text()').extract()[0].strip()

            horse_name_cell = line_selector.xpath('td[3]/div/a/text()').extract()[0]
            horse_name_regexp = '^(?P<name>[^\(]+)\((?P<code>[^\)]+)\)$'
            horse_name_dict = re.match(horse_name_regexp, horse_name_cell).groupdict()
            horsename = horse_name_dict['name']
            horsecode = horse_name_dict['code']

            timelist = [time.strip() for time in time_selector.xpath('td/text()').extract()]
            timelist_len = len(timelist)
            timelist.extend([None for i in xrange(6-timelist_len)])

            horse_path = line_selector.xpath('td[3]/div/a/@href').extract()[0]
            horse_url = 'http://www.{domain}/english/racing/{path}&Option=1#htop'.format(
                domain=self.domain, path=horse_path)
            request = scrapy.Request(horse_url, callback=self.parse_horse)
            meta_dict = {
                'racenumber': response.meta['racenumber'],
                'raceindex': response.meta['raceindex'],
                'racename': response.meta['racename'],
                'horsenumber': horsenumber,
                'horsename': horsename,
                'horsecode': horsecode,
                'timelist': timelist,
            }
            request.meta.update(meta_dict)

            yield request

    def parse_horse(self, response):

        sirename_dirty = response.xpath('//font[text()="Sire"]/../'
            'following-sibling::td/font/a/text()'
            ).extract() or response.xpath('//font[text()="Sire"]/../'
            'following-sibling::td/font/text()').extract()
        sirename = sirename_dirty[0].strip() if sirename_dirty else None
        race_rows_selector = response.xpath('//table[@class="bigborder"]//'
            'tr[@bgcolor][position()<6]')
        racedate = []
        place = []
        for race_raw_sel in race_rows_selector:
            racedate.append(race_raw_sel.xpath('td[3]/text()').extract()[0])
            place.append(race_raw_sel.xpath('td[2]//font/text()').extract()[0])

        yield items.HkjcHorseItem(
            racenumber=response.meta['racenumber'],
            raceindex=response.meta['raceindex'],
            racename=response.meta['racename'],
            horsenumber=response.meta['horsenumber'],
            horsename=response.meta['horsename'],
            horsecode=response.meta['horsecode'],
            timelist=response.meta['timelist'],
            sirename=sirename,
            racedate=racedate,
            place=place,
        )

    def parse_horse2(self, response):

        sirename = response.xpath('//th[text()="Sire"]/following-sibling::td/'
            'a/text()').extract()[0]
        race_rows_selector = response.xpath('(//tr[@class="even"] | //tr['
            '@class="even"]/preceding-sibling::tr[1])[position()<6]')
        racedate = []
        place = []
        final_sec_time = []
        for race_raw_sel in race_rows_selector:
            racedate.append(race_raw_sel.xpath('td[3]/text()').extract()[0])
            place.append(race_raw_sel.xpath('td[2]/text()').extract()[0])
            final_sec_time.append(race_raw_sel.xpath('td[17]/text()').extract()[0])

        yield items.HkjcHorseItem(
            racenumber=response.meta['racenumber'],
            raceindex=response.meta['raceindex'],
            racename=response.meta['racename'],
            horsenumber=response.meta['horsenumber'],
            horsename=response.meta['horsename'],
            horsecode=response.meta['horsecode'],
            timelist=response.meta['timelist'],
            sirename=sirename,
            racedate=racedate,
            place=place,
            final_sec_time=final_sec_time,
        )
