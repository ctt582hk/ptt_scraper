# -*- coding: UTF-8 -*-
import json
import requests
import time
from datetime import datetime
import os

from bs4 import BeautifulSoup
from bs4.element import NavigableString


def main():
    crawler = PttCrawler()
    crawler.crawl(board="Gossiping", start=10001, end=11000)

    # res = crawler.parse_article("https://www.ptt.cc/bbs/Gossiping/M.1119928928.A.78A.html")
    # crawler.output("test", res)


class PttCrawler:
    root = "https://www.ptt.cc/bbs/"
    main = "https://www.ptt.cc"
    gossip_data = {
        "from": "bbs/Gossiping/index.html",
        "yes": "yes"
    }
    run_time = datetime.strptime('1995-12-11', '%Y-%m-%d')  # 正在檢查的貼文的發佈日期
    start_time = None  # search time:begining
    end_time = None  # search time:end
    is_first = True  # 當run time >= start time時,判斷是否第一次遇到
    contains_keywords = False  # 判斷文本(title,context,回文等) 是否包含keyword

    def __init__(self):
        self.session = requests.session()
        requests.packages.urllib3.disable_warnings()
        self.session.post("https://www.ptt.cc/ask/over18",
                          verify=False,
                          data=self.gossip_data)

    def articles(self, page):
        '''文章內容的生成器
        Args:
            page: 頁面網址
        Returns:
            文章內容的生成器
        '''

        res = self.session.get(page, verify=False)
        soup = BeautifulSoup(res.text, "lxml")

        for article in soup.select(".r-ent"):
            try:
                yield self.main + article.select(".title")[0].select("a")[0].get("href")
            except:
                pass  # (本文已被刪除)

    def pages(self, board=None, index_range=None):  # 根據頁數範圍產生各頁的web site links
        '''頁面網址的生成器
        Args:
            board: 看板名稱
            index_range: 文章頁數範圍
        Returns:
            網址的生成器
        '''

        target_page = self.root + board + "/index"

        try:
            if range is None:
                yield target_page + ".html"
            else:
                for index in index_range:
                    yield target_page + str(index) + ".html"
        except GeneratorExit:
            print(GeneratorExit.__context__)
            return

    #   檢查text內是否包含任意一個keyword
    def is_contain_keywords(self, text, keywords: list):
        if keywords is None:
            yield False

        yield any(kw in text for kw in keywords)

    def parse_article(self, url, mode, keywords: list):
        '''解析爬取的文章，整理進dict
        Args:
            url: 欲爬取的PTT頁面網址
            mode: 欲爬取回文的模式。全部(all)、推文(up)、噓文(down)、純回文(normal)
        Returns:
            article: 爬取文章後資料的dict
            
        '''

        # 處理mode標誌
        if mode == 'all':
            mode = 'all'
        elif mode == 'up':
            mode = u'推'
        elif mode == 'down':
            mode = u'噓'
        elif mode == 'normal':
            mode = '→'
        elif mode == 'no respond':
            mode = 'no respond'
        else:
            raise ValueError("mode變數錯誤", mode)

        raw = self.session.get(url, verify=False)
        soup = BeautifulSoup(raw.text, "lxml")

        try:
            article = {}

            # 取得文章作者與文章標題,時間
            article["Author"] = soup.select(".article-meta-value")[0].contents[0].split(" ")[0]
            article["Title"] = soup.select(".article-meta-value")[2].contents[0]
            article["Date"] = str(soup.select(".article-meta-value")[3].contents[0])
            # 調整時間輸出為:年-月-日
            article['Date'] = (str(time.strptime(article['Date']).tm_year) + '-'
                               + str(time.strptime(article['Date']).tm_mon) + '-'
                               + str(time.strptime(article['Date']).tm_mday))
            # 取得正在檢查的貼文的發佈時間
            self.run_time = datetime.strptime(article['Date'], '%Y-%m-%d')

            # 取得內文
            content = ""
            for tag in soup.select("#main-content")[0]:
                if type(tag) is NavigableString and tag != '\n':
                    content += tag
                    break
            article["Content"] = content
            #   若keywords存在, 判斷title and context是否包含任意keywords

            if keywords is not None:
                title = next(self.is_contain_keywords(str(article['Title']), keywords))
                cont = next(self.is_contain_keywords(str(article['Content']), keywords))

                if title or cont:
                    self.contains_keywords = True

            if mode != 'no respond':

                # 處理回文資訊
                upvote = 0
                downvote = 0
                novote = 0
                response_list = []

                for response_struct in soup.select(".push"):

                    # 跳脫「檔案過大！部分文章無法顯示」的 push class
                    if "warning-box" not in response_struct['class']:

                        response_dic = {}

                        # 根據不同的mode去採集response
                        if mode == 'all':
                            response_dic["Content"] = response_struct.select(".push-content")[0].contents[0][1:]
                            response_dic["Vote"] = response_struct.select(".push-tag")[0].contents[0][0]
                            response_dic["User"] = response_struct.select(".push-userid")[0].contents[0]
                            response_list.append(response_dic)

                            if response_dic["Vote"] == u"推":
                                upvote += 1
                            elif response_dic["Vote"] == u"噓":
                                downvote += 1
                            else:
                                novote += 1
                        else:
                            response_dic["Content"] = response_struct.select(".push-content")[0].contents[0][1:]
                            response_dic["Vote"] = response_struct.select(".push-tag")[0].contents[0][0]
                            response_dic["User"] = response_struct.select(".push-userid")[0].contents[0]

                            if response_dic["Vote"] == mode:
                                response_list.append(response_dic)

                                if mode == u"推":
                                    upvote += 1
                                elif mode == u"噓":
                                    downvote += 1
                                else:
                                    novote += 1

                article["Responses"] = response_list
                article["UpVote"] = upvote
                article["DownVote"] = downvote
                article["NoVote"] = novote

        except Exception as e:
            print(e)
            print(u"在分析 %s 時出現錯誤" % url)

        return article

    def output(self, filename, data):
        '''
        爬取完的資料寫到json文件
        Args:
            filename: json檔的文件路徑
            data: 爬取完的資料
        '''

        try:
            with open(filename + ".json", 'wb+') as op:
                op.write(json.dumps(data, indent=4, ensure_ascii=False).encode('utf-8'))
                print('爬取完成~', filename + '.json', '輸出成功！')
        except Exception as err:
            print(filename + '.json', '輸出失敗 :(')
            print('error message:', err)

    #   根據條件爬取條件範圍內的post, 支持依 日期, 頁數, keyword爬取
    def crawl_Search(self,  board: str, mode='all', date_range=None, page_range=None, sleep_time=0.5,
                     keywords=None):
        '''根據條件爬取條件範圍內的post, 支持依 日期, 頁數, keyword爬取
        爬取資料主要接口
        Args:
            board: 欲爬取的看版名稱
            mode: 欲爬取回文的模式。全部(all)、推文(up)、噓文(down)、純回文(normal)、只取貼文內容(no respond)
            sleep_time: sleep間隔時間
            date_range: search data in time range, format= [date_start,date_end]
            page_range: search data in page range, format= [page_start,page_end]
            keywords: search data including keywords, format= [k1,k2,...]
        '''

        # 判斷time_range是否正確輸入
        if date_range != None:
            self.start_time = datetime.strptime(date_range[0], '%Y-%m-%d')
            self.end_time = datetime.strptime(date_range[1], '%Y-%m-%d')

            if self.start_time > self.end_time:
                print('Error Time Range!')
                return
        else:
            self.start_time = datetime.min
            self.end_time = datetime.today()

        # 設定搜索的頁面範圍
        crawl_range = None
        page_start = 0
        page_end = 0
        if page_range is not None:
            page_start = page_range[0]
            page_end = page_range[-1]
            crawl_range = [page_start]

            if page_start<=0 or page_start>page_end:
                print('page_range輸入錯誤!')

        else:
            crawl_range = [1]

        # 第一次的pre_page=page
        pre_page = None  # page是當前爬的頁面,pre_page是上一頁
        for page in self.pages(board, crawl_range):
            pre_page = page
            break

        #   對每頁的第一則貼文作檢查,若其日期小於start time則跳過該頁,第一次遇到大於等於start time的時候則檢查上一頁每個貼文,下載每一個大於等於start time的貼文
        #   檢查每頁最後一則貼文,若run time>end time則檢查前一頁貼文,把所有符合條件的貼文下載
        for page in self.pages(board, crawl_range):

            #   檢查每頁最後一則貼文run time是否大於end time
            if self.run_time > self.end_time:
                # 檢查前一頁內容,從上到下把資料儲存,直到遇到run time > end time的貼文
                res2 = []
                count2 = 0
                for article in self.articles(pre_page):
                    temp2 = self.parse_article(article, mode, keywords)
                    time.sleep(sleep_time)

                    if self.run_time > self.end_time:
                        break

                    if (keywords is not None and self.contains_keywords) or keywords is None:
                        res2.append(temp2)
                        count2 += 1
                        self.contains_keywords = False  # 這則貼文包含keywords,下一則未必包含
                        print(str(board) + '2版第' + str(crawl_range[-1] - 1) + '頁有' + str(count2) + '則貼文符合條件')

                print(u"已經完成 %s 版面第 %d 頁的爬取" % (board, crawl_range[-1] - 1))

                if len(res2) > 0:  # 若len(res2) <= 0 ,則該頁沒有end time的貼文
                    print('該頁面存在最後一則符合條件的貼文,日期為' + str(self.end_time.date()))
                    self.output('.\\data\\' + board + '\\' + board + str(crawl_range[-1] - 1), res2)
                else:
                    if keywords is None:
                        print('最後一則日期為' + str(self.end_time.date()) + '的貼文在第 ' + str(crawl_range[-1] - 2) + ' 頁')
                        #   run time所在的頁面沒有time range內的貼文,可以删除
                        file = board + str(crawl_range[-1] - 1) + '.json'
                        try:
                            os.remove(file)
                        except OSError as e:
                            print(u'File %s get error message: %s' % (file, e.strerror))
                    else:
                        print('該頁面沒有符合條件的貼文!')

                #   找到end time的最後一則貼文後可以中止程式
                print('已檢查Time Range內所有貼文!')
                break

            res = []
            print(U'正在檢查 %s 版面第 %d 頁...' % (board, crawl_range[-1]))
            count = 0

            for article in self.articles(page):
                temp = self.parse_article(article, mode, keywords)
                time.sleep(sleep_time)

                if self.is_first:  # 判斷是否第一次self.run_time>=self.start_time
                    if self.run_time >= self.start_time:
                        self.is_first = False

                        if crawl_range[-1] != 1:    # 在第一頁時不需檢查前一頁

                            # 檢查前一頁內容,直到self.run_time >= self.start_time,然後把之後的內容儲存
                            res1 = []
                            count1 = 0
                            for article in self.articles(pre_page):
                                temp1 = self.parse_article(article, mode, keywords)
                                time.sleep(sleep_time)
                                if self.run_time >= self.start_time and crawl_range[-1] != page_start:
                                    if (keywords is not None and self.contains_keywords) or keywords is None:
                                        count1 += 1
                                        print(str(board) + '1版第' + str(crawl_range[-1] - 1) + '頁有' + str(count1) + '則貼文符合條件')
                                        self.contains_keywords = False
                                        res1.append(temp1)

                            print(u"已經完成 %s 版面第 %d 頁的爬取" % (board, crawl_range[-1] - 1))
                            if len(res1) > 0:  # len(res1)=0 表示前一頁沒有start_time日期的貼文
                                print('該頁面存在第一則符合條件的貼文,日期為' + str(self.run_time.date()))
                                self.output('.\\data\\' + board + '\\' + board + str(crawl_range[-1] - 1), res1)
                            else:
                                print('該頁面沒有符合條件的貼文!')

                    # 若self.run_time<self.start_time,則跳出loop,在此結構下只會檢查每頁第一筆資料
                    else:
                        break


                if (keywords is not None and self.contains_keywords) or keywords is None:
                    count += 1
                    res.append(temp)
                    print(str(board) + '0版第' + str(crawl_range[-1]) + '頁有' + str(count) + '則貼文符合條件')
                    self.contains_keywords = False


            print(u"已經完成 %s 版面第 %d 頁的爬取" % (board, crawl_range[-1]))
            if len(res) <= 0:
                print(u'%s 版面第 %d 頁沒有符合條件的貼文' % (board, crawl_range[-1]))
            else:
                print("該頁面存在符合條件的貼文")
                self.output('.\\data\\' + board + '\\' + board + str(crawl_range[-1]), res)

            print('\n')

            # 從page_start開始逐頁檢查,若page_range沒有設定,則從第一頁到最後一頁逐頁檢查
            crawl_range.append(crawl_range[-1] + 1)

            if crawl_range[-1] > page_end and page_range is not None:
                print('已完成第' + str(page_start) + '頁到第' + str(page_end) + '頁的檢查!')
                return

            pre_page = page
            os.system('cls')


if __name__ == '__main__':
    main()
