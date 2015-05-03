import unittest

from scrapy import selector

from . import scmp_spider


class TestSCMPGetTdInd(unittest.TestCase):

    def test_no_colspan(self):

        tr_text = '''
            <tr bgcolor="WHITE" align="CENTER">
                <td nowrap=""><font size="1" face="ARIAL"><a target="_self" href="../../Resultspro/2013/ResultsPro13754.asp">07-07-13</a></font></td>
                <td align="CENTER"><font size="1" face="ARIAL">754 D</font></td>
                <td align="LEFT"><font size="1" face="ARIAL">ST tf g/f -B+2  </font></td>
                <td><font size="1" face="ARIAL">1200</font></td>
                <td><font size="1" face="ARIAL">4</font></td>
                <td><font size="1" face="ARIAL">8</font></td>
                <td align="LEFT"><font size="1" face="ARIAL">P. F. Yiu</font></td>
                <td><font size="1" face="ARIAL">125</font></td>
                <td align="LEFT"><font size="1" face="ARIAL">T. Berry</font></td>
                <td align="CENTER"><font size="1" face="ARIAL">2</font></td>
                <td align="CENTER"><font size="1" face="ARIAL">B1/XB</font></td>
                <td align="LEFT"><font size="1" face="ARIAL">DINING STAR</font></td>
                <td><font size="1" face="ARIAL">PSYCHOLOGIST</font></td>
                <td><font size="1" face="ARIAL">MULTIEXPRESS</font></td>
                <td><font size="1" face="ARIAL">1:09.5</font></td>
                <td><font size="1" face="ARIAL">(22.7 )</font></td>
                <td><font size="1" face="ARIAL">24.73&nbsp;22.51&nbsp;23.08</font></td>
                <td><font size="1" face="ARIAL">1:10.3</font></td>
                <td><font size="1" face="ARIAL">9-9-8</font></td>
                <td align="CENTER"><font size="1" face="ARIAL">5</font></td>
                <td align="CENTER"><font size="1" face="ARIAL">1178</font></td>
                <td><font size="1" face="ARIAL">52</font></td>
                <td align="CENTER"><font size="1" face="ARIAL">5.1</font></td>
                <td align="CENTER"><blink><font color="#FF0000" size="1" face="ARIAL">3.9</font></blink></td>
                <td align="CENTER"><a href="../mg_bf_race.asp?Hores_Name=GRACEFUL+KINGDOM&amp;Horse_id=P145&amp;rdate=07-Jul-2013"><img width="25" height="23" border="0" src="/images/morngall-s.gif"></a></td>
            </tr>
        '''
        tr = selector.Selector(text=tr_text).xpath('//tr')

        self.assertEquals(scmp_spider.HorseSpider.get_td_ind(tr, 1), 1)
        self.assertEquals(scmp_spider.HorseSpider.get_td_ind(tr, 25), 25)

    def test_one_td_with_three_colspan(self):

        # 18 td with attribute "colspan"
        tr_text = '''
            <tr bgcolor="WHITE" align="CENTER">
                <td nowrap=""><font size="1" face="ARIAL"><a target="_self" href="../../Resultspro/2013/ResultsPro13659.asp">02-06-13</a></font></td>
                <td align="CENTER"><font size="1" face="ARIAL">659 D</font></td>
                <td align="LEFT"><font size="1" face="ARIAL">ST tf g/f -A+3  </font></td>
                <td><font size="1" face="ARIAL">1200</font></td>
                <td><font size="1" face="ARIAL">4</font></td>
                <td><font size="1">DISQ</font></td>
                <td align="LEFT"><font size="1" face="ARIAL">P. F. Yiu</font></td>
                <td><font size="1" face="ARIAL">125</font></td>
                <td align="LEFT"><font size="1" face="ARIAL">T. Berry</font></td>
                <td align="CENTER"><font size="1" face="ARIAL">2</font></td>
                <td align="CENTER"><font size="1" face="ARIAL">&nbsp;</font></td>
                <td align="LEFT"><font size="1" face="ARIAL">REGENCY CHAMPION</font></td>
                <td><font size="1" face="ARIAL">T-BOLT</font></td>
                <td><font size="1" face="ARIAL">FAY DEEP</font></td>
                <td><font size="1" face="ARIAL">1:09.5</font></td>
                <td><font size="1" face="ARIAL">(22.8 )</font></td>
                <td><font size="1" face="ARIAL">24.71&nbsp;22.59&nbsp;25.48</font></td>
                <td colspan="3"><center><font size="2">DISQ</font></center></td>
                <td align="CENTER"><font size="1" face="ARIAL">1180</font></td>
                <td><font size="1" face="ARIAL">52</font></td>
                <td align="CENTER"><font size="1" face="ARIAL">2.6</font></td>
                <td align="CENTER"><blink><font color="#FF0000" size="1" face="ARIAL">2.8</font></blink></td>
                <td align="CENTER"><a href="../mg_bf_race.asp?Hores_Name=GRACEFUL+KINGDOM&amp;Horse_id=P145&amp;rdate=02-Jun-2013"><img width="25" height="23" border="0" src="/images/morngall-s.gif"></a></td>
            </tr>
        '''
        tr = selector.Selector(text=tr_text).xpath('//tr')

        self.assertEquals(scmp_spider.HorseSpider.get_td_ind(tr, 1), 1)
        self.assertEquals(scmp_spider.HorseSpider.get_td_ind(tr, 17), 17)
        self.assertEquals(scmp_spider.HorseSpider.get_td_ind(tr, 18), 18)
        self.assertEquals(scmp_spider.HorseSpider.get_td_ind(tr, 19), 18)
        self.assertEquals(scmp_spider.HorseSpider.get_td_ind(tr, 20), 18)
        self.assertEquals(scmp_spider.HorseSpider.get_td_ind(tr, 21), 19)
        self.assertEquals(scmp_spider.HorseSpider.get_td_ind(tr, 25), 23)

    def test_three_td_with_three_four_five_colspan(self):

        # 18 td with attribute "colspan"
        tr_text = '''
            <tr bgcolor="WHITE" align="CENTER">
                <td nowrap=""><font size="1" face="ARIAL"><a target="_self" href="../../Resultspro/2013/ResultsPro13659.asp">02-06-13</a></font></td>
                <td align="CENTER"><font size="1" face="ARIAL">659 D</font></td>
                <td align="LEFT"><font size="1" face="ARIAL">ST tf g/f -A+3  </font></td>
                <td><font size="1" face="ARIAL">1200</font></td>
                <td><font size="1" face="ARIAL">4</font></td>
                <td><font size="1">DISQ</font></td>
                <td align="LEFT"><font size="1" face="ARIAL">P. F. Yiu</font></td>
                <td colspan="3"><font size="1" face="ARIAL">125</font></td>
                <td align="LEFT"><font size="1" face="ARIAL">T. Berry</font></td>
                <td colspan="4"><font size="1" face="ARIAL">T-BOLT</font></td>
                <td><font size="1" face="ARIAL">FAY DEEP</font></td>
                <td><font size="1" face="ARIAL">1:09.5</font></td>
                <td><font size="1" face="ARIAL">(22.8 )</font></td>
                <td><font size="1" face="ARIAL">24.71&nbsp;22.59&nbsp;25.48</font></td>
                <td colspan="5"><center><font size="2">DISQ</font></center></td>
                <td align="CENTER"><font size="1" face="ARIAL">1180</font></td>
                <td><font size="1" face="ARIAL">52</font></td>
            </tr>
        '''
        tr = selector.Selector(text=tr_text).xpath('//tr')

        self.assertEquals(scmp_spider.HorseSpider.get_td_ind(tr, 1), 1)
        self.assertEquals(scmp_spider.HorseSpider.get_td_ind(tr, 8), 8)
        self.assertEquals(scmp_spider.HorseSpider.get_td_ind(tr, 9), 8)
        self.assertEquals(scmp_spider.HorseSpider.get_td_ind(tr, 15), 10)
        self.assertEquals(scmp_spider.HorseSpider.get_td_ind(tr, 16), 11)
        self.assertEquals(scmp_spider.HorseSpider.get_td_ind(tr, 24), 15)
        self.assertEquals(scmp_spider.HorseSpider.get_td_ind(tr, 26), 17)

if __name__ == '__main__':
    unittest.main()
