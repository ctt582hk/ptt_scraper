### ptt-scraper
**前言**

**Preface**

此模組是一個專門爬取批踢踢(PTT)貼文資料的爬蟲

This program is a crawlers specially designed to crawl PTT post data.

此模組是基於 [PTT-Crawler](https://github.com/zake7749/PTT-Crawler) 上作出的改良, 支持依 版塊, 日期, 頁數, 關鍵字搜索並下載貼文, 結果會儲存為json檔

This program is based on improvements made on [PTT-Crawler](https://github.com/zake7749/PTT-Crawler) and supports board, date, page, keywords search.The results will stored in .json

此模組使用python語言編寫  

This program is use python.


**功能**

**what can it do?**

可根據版塊, 日期, 頁數, 關鍵字搜索並下載貼文, 結果會儲存為json檔

supports board, date, page, keywords search. The results will stored in .json

如果該版塊需要按確定,如18禁提醒,則可能爬取失敗

if the board need to pressing "ok", such as 18 years old warning, the data will fail to catch

此模組僅擷取文字

this program can get text only

可根據需要選擇是否下載貼文下的回應

download respond(option)

結果包含符合條件的貼文標題, 內容, 作者, 發文時間, 回文(可選)

results including post title, content, author, date, respond(option)


**如何使用?**

**How to use?**

1.下載Crawler.py在你的專案所在的資料夾上

2.在你的專案中輸入  `from Crawler import PttCrawler`

3.輸入  `crawler = PttCrawler()`  使用模組

4.輸入  `crawler.crawl_Search()`  並輸入條件,程式會根據條件自動爬取符合條件的貼文

詳細使用方法可參考sample.py


1.download Crawler.py in your program file

2.enter `from Crawler import PttCrawler` in your program

3.enter `crawler = PttCrawler()` in your program to use this module

4.enter `crawler.crawl_Search()` in your program and enter condition,the module will catch post that meet the conditions

read the sample.py for more information


**常用函式**

**Common methods**

    -PttCrawler():                                                                        初始化   initialize 

    -crawl_Search(board: str, mode, date_range, page_range, sleep_time, keywords):        根據條件搜索貼文  Search posts based on condition

        -board:       (必選)欲搜索的版塊                    (Required)To be searched board
  
        -mode:        (必選)符合條件的貼文中下載回文的模式    (Required)Pattern for downloading palindrome in eligible posts
  
            -all:         (預設)(可選)取得所有回文   (Default)(option)Get all responds
    
            -up:          (可選)取得推文            (option)  Get good responds 
    
            -down:        (可選)取得噓文            (option)  Get bad responds
    
            -normal:      (可選)取得平文            (option)  Get normal responds
    
            -no respond:  (可選)不取得回文          (option)  Don't get any responds
    
        -date_range:  (可選)搜索指定日期範圍內的貼文, 格式:[date_start, date_end]    (option)Search data in date range, format:[date_start, date_end]  

        -page_range:  (可選)搜索指定頁數範圍內的貼文, 格式:[page_start, page_end]    (option)Search data in page range, format:[page_start, page_end]

        -keywords:    (可選)搜索含有指定關鍵字的貼文, 格式:[kw1,kw2,...]             (option)Search data including keyword, format:[kw1,kw2,...]

        -sleep_time:  (可選)檢查貼文之間的停止時間           (option)Check the stop time between posts

    -parse_article(url, mode, keywords):  輸入網址,根據mode and keyword爬取該網址頁面的貼文    input url, catch post according mode and keywords

    -output(filename, data):              輸入data, 把輸入的data輸出為json檔,檔名=filename    input data,output data stored in .json, name=filename


**已知BUG**

**Bugs**

如果檢索日期在第一頁, 第一頁會有低機率捉到錯誤資料, 原因未明

if the date starts from the first page, there is less chance of catching wrong data in first page for unknown reason

當爬的資料較大時(page>6000), 可能會導致電腦反應緩慢 (我在跑程式時跑到大概6000頁時電腦反應異常緩慢, 不得不重新開機), 不排除是電腦的其它問題引起, 建議爬取大量資料時分批進行

if the amount of data you are retrieving is large(page>6000), it may slow down your computer. if you want to do this, it is recommended to do it in batches


**結語**

**Conclusion**

第一次寫(改)爬蟲, 如果寫得不好請多見諒, 目前的功能夠我使用了, 所以至少近期內也不會更新, 如果想修改/新增功能可以隨便改

如有問題, 可以連絡我, 我會儘量回答

~~快寫好才發現PTT有放API出來, 但已經寫了大半只好硬着頭皮寫完的我真的是baka~~
