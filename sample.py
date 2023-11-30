from Crawler import PttCrawler
import os

crawler = PttCrawler()
# 想查的版
boards = ['Gossiping', 'C_Chat', 'HatePolitics', 'WomenTalk', 'Boy-Girl', 'BabyMother', 'Kaohsiung', 'Marginalman',
          'TaichungBun', 'Tainan', 'Hsinchu', 'ChungLi', 'BigBanciao', 'Chiayi']

# search key words
keywords = ['SDM', 'sdm', 'shared decision making', 'Shared Decision Making', '共享決策', '共同決策']

page_start = 4010
page_end = 4011
date_start = '2022-09-02'
date_end = '2022-09-03'

for board in boards:

    try:
        #    根據搜查版面建立檔案
        path1 = '.\\data'
        path2 = path1 + '\\' + board
        # 判斷路徑是否存在,不存在則創造路徑
        if not os.path.isdir(path1):    #.\data
            os.mkdir(path1)
        if not os.path.isdir(path2):    #.\data\[boards]
            os.mkdir(path2)

        #   爬ptt
        crawler.crawl_Search(board=board, mode='no respond', date_range=[date_start, date_end],
                                          keywords=keywords, page_range=[page_start, page_end])

    except Exception as err:
        print('Can not get the data from ' + board + ', error message is : ', err)
        continue

    finally:
        print(board+' is finish!')

