codeby: slience_me(宋保贤)

myblog: https://blog.csdn.net/slience_me

myGitHub: https://github.com/slience-me
# 人民日报文章内容分析

## 1.数据获取 


```python
import requests
import bs4
import os
import datetime
import time


def fetch_url(url):
    """
        功能：访问 url 的网页，获取网页内容并返回
    :param url: 目标网页的 url
    :return: 目标网页的 html 内容
    """
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
    }

    r = requests.get(url, headers=headers)
    r.raise_for_status()
    r.encoding = r.apparent_encoding
    return r.text


def get_page_list(year, month, day):
    """
        功能：获取当天报纸的各版面的链接列表
    :param year: 年 改变年月日拼接成需要爬取的url
    :param month: 月
    :param day: 日
    :return: 返回当天报纸的各版面的链接列表
    """
    url = 'http://paper.people.com.cn/rmrb/html/' + year + '-' + month + '/' + day + '/nbs.D110000renmrb_01.htm'
    html = fetch_url(url)
    bs_obj = bs4.BeautifulSoup(html, 'html.parser')
    temp = bs_obj.find('div', attrs={'id': 'pageList'})
    if temp:
        page_list = temp.ul.find_all('div', attrs={'class': 'right_title-name'})
    else:
        page_list = bs_obj.find('div', attrs={'class': 'swiper-container'}).find_all('div',
                                                                                     attrs={'class': 'swiper-slide'})
    link_list = []
    for page in page_list:
        link = page.a["href"]
        url = 'http://paper.people.com.cn/rmrb/html/' + year + '-' + month + '/' + day + '/' + link
        link_list.append(url)
    return link_list


def get_title_list(year, month, day, pageUrl):
    """
        功能：获取报纸某一版面的文章链接列表
    :param year: 年
    :param month: 月
    :param day: 日
    :param pageUrl: 该版面的链接
    :return:
    """
    html = fetch_url(pageUrl)
    bs_obj = bs4.BeautifulSoup(html, 'html.parser')
    temp = bs_obj.find('div', attrs={'id': 'titleList'})
    if temp:
        title_list = temp.ul.find_all('li')
    else:
        title_list = bs_obj.find('ul', attrs={'class': 'news-list'}).find_all('li')
    link_list = []

    for title in title_list:
        temp_list = title.find_all('a')
        for temp in temp_list:
            link = temp["href"]
            if 'nw.D110000renmrb' in link:
                url = 'http://paper.people.com.cn/rmrb/html/' + year + '-' + month + '/' + day + '/' + link
                link_list.append(url)
    return link_list


def get_content(html):
    """
        功能：解析 HTML 网页，获取新闻的文章内容
    :param html: html 网页内容
    :return: 标题+内容
    """
    bs_obj = bs4.BeautifulSoup(html, 'html.parser')

    # 获取文章 标题
    title = bs_obj.h3.text + '\n' + bs_obj.h1.text + '\n' + bs_obj.h2.text + '\n'
    # print(title)

    # 获取文章 内容
    p_list = bs_obj.find('div', attrs={'id': 'ozoom'}).find_all('p')
    content = ''
    for p in p_list:
        content += p.text + '\n'
    # print(content)

    resp = title + content
    return resp


def save_file(content, path, filename):
    """
        功能：将文章内容 content 保存到本地文件中
    :param content: 要保存的内容
    :param path: 路径
    :param filename: 文件名
    :return:
    """
    # 如果没有该文件夹，则自动生成
    if not os.path.exists(path):
        os.makedirs(path)
        # print('爬取到文章，正在下载中...')

    # 保存文件
    with open(path + filename, 'w', encoding='utf-8') as f:
        f.write(content)
    # print('爬取到文章，正在下载中...')
    # print('文章已写入：' + path)


def download_rmrb(year, month, day, destdir):
    """
        功能：爬取《人民日报》网站某年,某月,某日的新闻内容，并保存在指定目录下
    :param year: 年
    :param month: 月
    :param day: 日
    :param destdir: 文件保存的根目录
    :return:
    """
    page_list = get_page_list(year, month, day)
    for page in page_list:
        title_list = get_title_list(year, month, day, page)
        for url in title_list:
            # 获取新闻文章内容
            html = fetch_url(url)
            content = get_content(html)
            # 生成保存的文件路径及文件名
            temp = url.split('_')[2].split('.')[0].split('-')
            page_no = temp[1]
            title_no = temp[0] if int(temp[0]) >= 10 else '0' + temp[0]
            path = destdir + '/' + year + month + day + '/'
            file_name = year + month + day + '-' + page_no + '-' + title_no + '.txt'

            # 保存文件
            save_file(content, path, file_name)
            # time.sleep(3) 休眠


def gen_dates(b_date, days):
    day = datetime.timedelta(days=1)
    for i in range(days):
        yield b_date + day * i


def get_date_list(beginDate, endDate):
    """
        获取日期列表
    :param beginDate: 开始日期
    :param endDate: 结束日期
    :return:
    """
    start = datetime.datetime.strptime(beginDate, "%Y%m%d")
    end = datetime.datetime.strptime(endDate, "%Y%m%d")

    data = []
    for d in gen_dates(start, (end - start).days + 1):
        data.append(d)
    # return: 返回开始日期和结束日期之间的日期列表
    return data

    # 主函数：程序入口


def get_news(local_data):
    # 输入起止日期，爬取之间的新闻
    print('---文章爬取系统---')
    begin_date = input('请输入开始日期(格式如20231101):')
    end_date = input('请输入结束日期(格式如20231101):')
    data = get_date_list(begin_date, end_date)

    for d in data:
        year = str(d.year)
        month = str(d.month) if d.month >= 10 else '0' + str(d.month)
        day = str(d.day) if d.day >= 10 else '0' + str(d.day)
        # 爬取后文章t统一存到这个文件夹,没有会自动创建
        destdir = "../data"

        # 判断日期是否在local_data中，如果在则continue
        date = int(year + month + day)
        print(date)
        if date in local_data:
            print('爬取文章时间为：' + year + '/' + month + '/' + day + '的文章已经存在!')
            continue
        print('---开始爬取文章，日期为' + year + '/' + month + '/' + day + '---')
        # time.sleep(3) 休眠
        download_rmrb(year, month, day, destdir)
        print("爬取文章完成！")
```

# 2.数据处理


```python
import multiprocessing
import os
import time
import jieba
import re
from zhon.hanzi import punctuation as puncZH
from string import punctuation as puncEN
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# 全局配置
encoding = 'utf-8'
global_path = '../data/'
font_path = '../Fonts/方正正中黑简体.ttf' 
width=9000
height=6000
punctuation_set = set(puncZH + puncEN)


def get_news_path():
    """
        获取路径下的全部文章内容
    :return: 全部文章的路径
    """
    news_path = []
    for dirname, _, filenames in os.walk('../data'):
        for filename in filenames:
            news_path.append(os.path.join(dirname, filename).replace('\\', '/'))
    print("func get_news_path() is called：现有新闻总数为: ", len(news_path))
    return news_path


def remove_punctuation(s: str):
    """
        去除标点符号    
    :param s: 传入的字符串
    :return: 去除标点符号后的字符串
    """
    s = re.sub(r"[%s]+" % puncZH, "", s)
    s = re.sub(r"[%s]+" % puncEN, "", s)
    s = re.sub(r"[\d\n\t\r]+", "", s)
    return s


def has_punctuation(s: str):
    """
        判断字符串中是否存在标点符号        
    :param s: 传入的字符串
    :return: bool标识
    """
    return any(char in punctuation_set for char in s)


def get_words(news: str):
    """
        获取某路径下某个文章内的全部词语
    :param news: 
    :return: 
    """
    split_news = jieba.lcut(news)  # 采用精确模式进行分词
    removed_split_news = []
    for text in split_news:
        if has_punctuation(text) is False:
            removed_split_news.append(text)
    return removed_split_news


def get_words_count(news_path):
    """
        获取全部文章的全部词语
    :param news_path: 
    :return: 
    """
    words = []
    for path in news_path:
        with open(path, 'r', encoding=encoding) as file:
            news = file.read()
            words.extend(get_words(news))
    print('func get_words_count() is called：词语数量: ', len(words))
    return words


from collections import Counter


def get_unique_words_count(words):
    """
        统计某个词语的词频信息
    :param words: 词语列表
    :return: 词语词频的字典
    """
    word_count = Counter(words)  # 使用collections.Counter来更简洁地统计词频
    print('func get_unique_words_count() is called：去重词语的个数：', len(word_count))
    return word_count


def get_stop_words():
    """
        获取停用词
    :return: 
    """
    stopwords = set()
    for dirname, _, filenames in os.walk('../stopwords-master'):
        for filename in filenames:
            if filename.endswith('txt'):
                try:
                    with open(os.path.join(dirname, filename), 'r', encoding='utf-8') as file:
                        stopwords.update(file.read().split())
                except UnicodeDecodeError as e:
                    print(f"UnicodeDecodeError: {dirname,filename}{e}")
                # 在这里处理异常，如忽略或记录错误
    
    common_stopwords = {'年', '月', '日', '上', '中', '本报', '的', '和', '在', '为', '了', '\xa0', '\n', ' ', '■', '是'}
    stopwords.update(common_stopwords)
    stopwords = list(stopwords)
    print('func get_unique_words_count() is called：统计停止词总数: ', len(stopwords))
    return stopwords


def word_count_remove_stopword(word_count):
    """
        从全部词语中移除停止词
    :param word_count: 
    :return: 
    """
    stopwords = set(get_stop_words())
    word_count = {word: count for word, count in word_count.items() if word not in stopwords}
    print('func get_unique_words_count() is called：不带停止词的唯一单词总数: ', len(word_count))
    word_count_no_single = {word: count for word, count in word_count.items() if len(word) > 1 }
    print('func get_unique_words_count() is called：去除单个字的唯一单词总数: ', len(word_count_no_single))
    return word_count_no_single


def timer_process():
    """
        计时器，用于计时生成词云图所用时间
    :return: 
    """
    start_time = time.time()
    while True:
        current_time = time.time()
        elapsed_time = current_time - start_time
        print(f"词云图生成时间计时，当前已经用时: {int(elapsed_time)} 秒", end='\r')
        time.sleep(1)


def draw_wordcloud(word_count):
    """
        生成词云图并保存
    :param word_count: 词频字典
    :param font_path: 字体路径
    :param width: 图片宽度
    :param height: 图片高度
    """
    start_time = time.time()
    print("开始初始化WordCloud init")
    wc = WordCloud(font_path=font_path, width=width, height=height, background_color="red",
                   max_words=1000,
                   color_func=lambda *args, **kwargs: (255, 255, 0))
    print("初始化完成! 开始生成WordCloud图片!预计503秒")
    timer = multiprocessing.Process(target=timer_process)
    timer.start()
    wc.generate_from_frequencies(word_count)
    # 主进程执行完毕后，关闭计时进程
    timer.terminate()
    timer.join()
    print("生成图片完成! 开始保存图片!")
    wc.to_file("People's Daily WordCloud Zh_1.png")
    plt.figure(figsize=(32, 16))
    plt.imshow(plt.imread("./People's Daily WordCloud Zh_1.png"))
    plt.axis("off")
    plt.show()
    print(f"代码块执行时间：{time.time() - start_time} 秒")


def get_current_data_list():
    """
        获取当前现有文章
    :param global_path: 
    :return: 
    """
    local_data = []
    for dirname, _, filenames in os.walk(global_path):
        if global_path == dirname:
            continue  # 跳过根路径
        local_data.append(int(dirname.replace(global_path, '')))
    local_data.sort()
    print('当前已经有的数据有:', local_data)
    return local_data


def get_new_data():
    """
        判断用户是否要添加新数据
    :return: 
    """
    local_data = get_current_data_list()
    while True:
        flag = input("新增文章数据吗? (Y/N): ").strip().upper()
        if flag == 'Y':
            get_news(local_data)
            break
        elif flag == 'N':
            print('不添加新数据!')
            break
        else:
            print('请输入Y或N!')

```


```python
get_new_data()
```

    当前已经有的数据有: [20230901, 20230902, 20230903, 20230904, 20230905, 20230906, 20230907, 20230908, 20230909, 20230910, 20230911, 20230912, 20230913, 20230914, 20230915, 20230916, 20230917, 20230918, 20230919, 20230920, 20230921, 20230922, 20230923, 20230924, 20230925, 20230926, 20230927, 20230928, 20230929, 20231001, 20231002, 20231003, 20231004, 20231005, 20231006, 20231007, 20231008, 20231009, 20231010, 20231011, 20231012, 20231013, 20231014, 20231015, 20231016, 20231017, 20231018, 20231019, 20231020, 20231021, 20231022, 20231023, 20231024, 20231025, 20231026, 20231027, 20231028, 20231029, 20231101, 20231102, 20231103, 20231104]
    不添加新数据!
    


```python
news_path = get_news_path()
```

    func get_news_path() is called：现有新闻总数为:  4495
    


```python
words = get_words_count(news_path)
```

    func get_words_count() is called：词语数量:  2717908
    


```python
word_count = get_unique_words_count(words)
```

    func get_unique_words_count() is called：去重词语的个数： 93063
    


```python
word_count = word_count_remove_stopword(word_count)
```

    func get_unique_words_count() is called：统计停止词总数:  2320
    func get_unique_words_count() is called：不带停止词的唯一单词总数:  91900
    func get_unique_words_count() is called：去除单个字的唯一单词总数:  88986
    


```python
draw_wordcloud(word_count)
```

    开始初始化WordCloud init
    初始化完成! 开始生成WordCloud图片!预计503秒
    生成图片完成! 开始保存图片!
    


    
![png](images/output_10_1.png)
    


    代码块执行时间：456.9963958263397 秒
    


```python
import pandas as pd
word_ds=pd.DataFrame(word_count,index=[0])
word_ds=word_ds.T
word_ds.columns=['count']
word_ds.sort_values(by=['count'],ascending=False,inplace=True)
```


```python
# from pylab import mpl
# mpl.rcParams['font.sans-serif'] = ['simhei'] # 指定默认字体
# mpl.rcParams['axes.unicode_minus'] = False # 解决保存图像是负号'-'显示为方块的问题
word_ds.head(20).plot(kind='bar', figsize=(12, 5), color='skyblue',title='人民日报关键词词频统计')
plt.xlabel('关键词名称')
plt.xticks(rotation=0)
plt.ylabel('词频统计')
plt.legend(['数量'])
plt.grid(axis='y', linestyle='--', alpha=0.6)
plt.show()
```


    
![png](images/output_12_0.png)
    



```python
# 针对不同的领域进行分析
category = ['政治与国际关系', '经济与金融', '文化与教育', '社会与人民生活', '科技与创新', '军事与国防', '环境与可持续发展', '国内地区报道', '国际报道']
category_keywords_politics = ['政治与国际关系', '政治','党和政府', '国内政策', '国际外交', '国际合作', '政府工作', '政治改革', '政治动态', '政权', '外交政策', '政府机构', '党派政治', '领导人', '政治体制', '政治制度', '政治经济', '政治发展', '政治体制', '外交', '外交政策', '外交动态', '外交事务', '外交动态', '外交事务', '习近平']
category_keywords_economy = ['经济与金融', '经济', '金融', '经济发展', '贸易', '发展', '建设', '金融市场', '宏观经济政策', '产业发展', '经济改革', '经济动态', '经济增长', '经济政策', '经济动态', '经济体制', '经济体制', '经济领域', '经济政策', '经济改革']
category_keywords_culture = ['文化与教育', '文化活动', '艺术', '文化传承', '教育政策', '教育改革', '文化领域', '文化发展', '教育体制',  '文化教育', '文化发展', '文化传承', '文化发展', '文化', '教育', '传统文化', '中华文化', '传承', '历史', '学习', '诗词', '弘扬', '故宫', '书法', '博物馆', '国学']
category_keywords_society = ['社会与人民生活', '社会', '人民', '生活', '社会问题', '医疗卫生', '社会保障', '人民生活水平', '社会动态', '社会改革', '社会发展', '社会福利']
category_keywords_science = ['科技与创新', '科技', '创新', '科研发展', '科技政策', '创新技术', '信息技术', '科学研究', '科技领域', '科技创新', '技术发展']
category_keywords_military = ['军事与国防','国防', '军事', '军事动态', '军事政策', '军事技术', '军队', '国防建设', '军事演习', '军事合作', '官兵', '部队', '战士', '连队', '战友',  '战场', '装备', '军人', '强军', '海军', '飞行员', '官兵', '空军', '陆军', '导弹', '武警']
category_keywords_environment = ['环境与可持续发展', '环境', '可持续', '可持续发展', '环保政策', '可持续发展', '环境保护', '气候变化', '环境污染', '生态保护', '环境政策', '可持续资源利用']
category_keywords_domestic = ['国内地区报道', '国内', '地区', '地方政府工作', '地方动态', '地方经济', '地方政策', '地方社会', '地方文化', '地方发展', '地方改革']
category_keywords_internation = ['国际报道', '国际', '世界', '国际新闻', '国际事务', '国际合作', '国际外交', '国际关系', '国际经济', '国际政治', '国际动态']
```


```python
word_count
```




    {'中共中央政治局': 217,
     '会议': 1322,
     '审议': 252,
     '干部': 1982,
     '教育': 3988,
     '培训': 1764,
     '工作': 6011,
     '条例': 246,
     '全国': 2702,
     '规划': 1032,
     '二三': 14,
     '二七': 1,
     '中共中央': 163,
     '总书记': 4059,
     '习近平': 7589,
     '主持会议': 39,
     '建设': 10094,
     '高素质': 188,
     '干部队伍': 81,
     '先导性': 22,
     '基础性': 141,
     '战略性': 254,
     '工程': 1464,
     '推进': 5922,
     '中国': 17036,
     '特色': 2635,
     '社会主义': 2425,
     '伟大事业': 67,
     '党的建设': 233,
     '伟大工程': 32,
     '地位': 319,
     '作用': 2050,
     '贯彻': 877,
     '时代': 4542,
     '思想': 2985,
     '认真落实': 57,
     '组织路线': 25,
     '深刻': 1000,
     '领悟': 118,
     '两个': 836,
     '确立': 237,
     '决定性': 128,
     '意义': 736,
     '增强': 1588,
     '四个': 226,
     '意识': 428,
     '坚定': 1196,
     '自信': 729,
     '维护': 1407,
     '理想信念': 123,
     '宗旨': 121,
     '执政': 77,
     '本领': 214,
     '重点': 1755,
     '培养': 731,
     '造就': 119,
     '政治': 1407,
     '过硬': 100,
     '具备': 222,
     '领导': 1326,
     '现代化': 3740,
     '能力': 2034,
     '学习': 1809,
     '主题': 1654,
     '主线': 82,
     '坚持不懈': 69,
     '用党': 40,
     '创新': 6649,
     '理论': 1602,
     '凝心': 115,
     '铸魂': 145,
     '强基': 28,
     '固本': 60,
     '训练': 351,
     '贯穿': 226,
     '成长': 544,
     '周期': 138,
     '教育引导': 69,
     '树立': 435,
     '正确': 455,
     '权力观': 15,
     '政绩观': 119,
     '事业': 1515,
     '提高': 1780,
     '判断力': 26,
     '领悟力': 24,
     '执行力': 33,
     '推动': 8385,
     '供给': 640,
     '需求': 1593,
     '精准': 646,
     '匹配': 78,
     '更好': 1662,
     '组织': 2901,
     '岗位': 376,
     '优化': 1364,
     '方式': 1589,
     '方法': 478,
     '进一步': 2361,
     '系统性': 158,
     '针对性': 171,
     '有效性': 49,
     '围绕': 961,
     '党中央': 1047,
     '决策': 425,
     '部署': 816,
     '国家': 9859,
     '战略': 2186,
     '领域': 3683,
     '专题学习': 15,
     '提升': 4126,
     '高质量': 3681,
     '发展': 24279,
     '服务': 5594,
     '群众': 2415,
     '防范': 283,
     '化解': 360,
     '风险': 972,
     '扎实': 477,
     '做好': 1034,
     '基础': 1922,
     '保障': 2164,
     '发挥': 1929,
     '党校': 89,
     '行政': 749,
     '学院': 550,
     '主渠道': 25,
     '主阵地': 25,
     '把关': 34,
     '持续': 4239,
     '下大': 6,
     '气力': 10,
     '抓好': 252,
     '师资队伍': 26,
     '弘扬': 784,
     '联系实际': 21,
     '马克思主义': 879,
     '学风': 20,
     '力戒': 21,
     '形式主义': 67,
     '勤俭': 8,
     '规范': 511,
     '办学': 123,
     '新华社': 937,
     '北京': 2438,
     '31': 311,
     '日电': 1568,
     '2023': 1719,
     '2027': 52,
     '指出': 1480,
     '研究': 2138,
     '事项': 307,
     '第十一次': 26,
     '归侨': 90,
     '侨眷': 86,
     '代表大会': 30,
     '在京开幕': 12,
     '李强': 495,
     '赵乐际': 208,
     '王沪宁': 115,
     '蔡奇丁': 14,
     '薛祥': 141,
     '韩正': 97,
     '祝贺': 157,
     '李希': 86,
     '代表': 1341,
     '致词': 97,
     '记者': 1952,
     '张烁': 18,
     '上午': 272,
     '北京人民大会堂': 38,
     '开幕': 294,
     '蔡奇': 152,
     '党和国家': 346,
     '领导人': 418,
     '人民大会堂': 182,
     '大礼堂': 10,
     '气氛': 71,
     '庄重': 22,
     '热烈': 212,
     '主席台': 17,
     '上方': 18,
     '悬挂': 34,
     '会标': 7,
     '后幕': 6,
     '正中': 11,
     '象征': 80,
     '五大洲': 23,
     '侨胞': 30,
     '心向祖国': 2,
     '侨联': 87,
     '会徽': 26,
     '10': 3925,
     '红旗': 30,
     '分列': 11,
     '两侧': 63,
     '二楼': 20,
     '眺台': 5,
     '指导': 960,
     '二十大': 581,
     '精神': 2592,
     '团结': 605,
     '凝聚': 599,
     '海外侨胞': 86,
     '中华民族': 1432,
     '复兴': 1112,
     '奋斗': 555,
     '巨型': 33,
     '横幅': 11,
     '1200': 64,
     '100': 588,
     '多个': 1163,
     '600': 144,
     '特邀嘉宾': 9,
     '欢聚一堂': 11,
     '主席': 2653,
     '中央军委': 104,
     '步入': 79,
     '会场': 74,
     '全场': 98,
     '响起': 81,
     '掌声': 115,
     '大会': 820,
     '雄壮': 18,
     '中华人民共和国': 592,
     '国歌声': 11,
     '发表': 372,
     '题为': 61,
     '强国': 1291,
     '民族': 1389,
     '侨界': 37,
     '团结奋斗': 145,
     '磅礴': 104,
     '力量': 1668,
     '工作者': 241,
     '致以': 77,
     '诚挚': 73,
     '问候': 78,
     '李希在': 5,
     '中说': 44,
     '坚强': 246,
     '第十次': 25,
     '贯彻落实': 518,
     '侨务工作': 8,
     '群团': 25,
     '论述': 281,
     '中心': 2428,
     '服务大局': 40,
     '履行': 394,
     '职能': 112,
     '政治性': 55,
     '先进性': 30,
     '群众性': 49,
     '影响力': 353,
     '始终': 975,
     '祖国': 306,
     '奋进': 282,
     '人民': 4061,
     '经济': 6395,
     '脱贫': 475,
     '攻坚': 278,
     '抗疫': 59,
     '斗争': 200,
     '对外开放': 462,
     '港澳': 91,
     '长期': 603,
     '繁荣': 980,
     '稳定': 1177,
     '祖国统一': 20,
     '独特': 440,
     '优势': 1737,
     '作出': 1558,
     '贡献': 1242,
     '建成': 890,
     '第二个': 151,
     '百年': 416,
     '奋斗目标': 132,
     '中国式': 1379,
     '海内外': 115,
     '中华儿女': 90,
     '共同努力': 191,
     '希望': 1014,
     '积极响应': 48,
     '党和人民': 96,
     '号召': 46,
     '助力': 1296,
     '构建': 2559,
     '格局': 883,
     '展现': 823,
     '更大': 603,
     '铸牢': 83,
     '共同体': 1764,
     '中华': 1263,
     '优秀': 1370,
     '传统': 2171,
     '文化': 8010,
     '人类': 2169,
     '命运': 1706,
     '国和住': 4,
     '共担': 42,
     '重任': 109,
     '共享': 1226,
     '荣光': 66,
     '创造': 1274,
     '业绩': 91,
     '共青团中央书记处': 12,
     '第一书记': 65,
     '阿东': 3,
     '中华全国总工会': 53,
     '中国共产主义青年团': 7,
     '中央委员会': 15,
     '中华全国妇女联合会': 35,
     '中国文学艺术界联合会': 11,
     '中国作家协会': 13,
     '中国科学技术协会': 10,
     '中华全国台湾同胞联谊会': 5,
     '中国残疾人联合会': 31,
     '贺词': 14,
     '各群': 3,
     '团组织': 15,
     '牢记': 219,
     '使命': 683,
     '相互': 359,
     '密切合作': 39,
     '发扬': 121,
     '优良传统': 77,
     '征程': 862,
     '局面': 266,
     '会上': 187,
     '宣读': 22,
     '国务院': 830,
     '侨办': 9,
     '表彰': 70,
     '杰出人物': 6,
     '先进个人': 11,
     '人力资源': 229,
     '社会保障部': 36,
     '全国侨联': 5,
     '系统': 1401,
     '先进集体': 12,
     '先进': 532,
     '获奖': 45,
     '单位': 872,
     '颁奖': 41,
     '主席团': 30,
     '常务主席': 9,
     '万立骏': 6,
     '第十届': 39,
     '委员会': 717,
     '报告': 940,
     '王毅': 263,
     '石泰峰': 34,
     '李干杰': 30,
     '李书磊': 24,
     '陈文清': 36,
     '王小洪': 55,
     '洛桑': 22,
     '江村': 26,
     '咸辉': 10,
     '出席会议': 109,
     '中央': 837,
     '国家机关': 95,
     '部门': 1739,
     '人民团体': 29,
     '军队': 130,
     '北京市': 240,
     '负责同志': 209,
     '民主党派': 23,
     '全国工商联': 51,
     '负责人': 995,
     '首都': 268,
     '参加': 1063,
     '开幕会': 13,
     '全文': 31,
     '求是': 56,
     '杂志': 42,
     '文章': 238,
     '传承': 1167,
     '座谈会': 389,
     '讲话': 184,
     '出版': 260,
     '17': 409,
     '源远流长': 116,
     '中华文明': 723,
     '博大精深': 67,
     '历史': 3034,
     '创造性': 290,
     '转化': 978,
     '创新性': 229,
     '现代文明': 246,
     '把握': 902,
     '特性': 104,
     '元素': 210,
     '塑造出': 3,
     '连续性': 67,
     '从根本上': 62,
     '理解': 317,
     '古代': 138,
     '未来': 1555,
     '守正': 173,
     '守旧': 17,
     '尊古': 16,
     '复古': 20,
     '进取精神': 16,
     '不惧': 8,
     '挑战': 981,
     '勇于': 106,
     '接受': 331,
     '事物': 69,
     '无畏': 17,
     '品格': 87,
     '统一性': 45,
     '融为一体': 35,
     '遭遇': 89,
     '挫折': 21,
     '牢固': 130,
     '国土': 113,
     '文明': 2992,
     '信念': 97,
     '统一': 757,
     '永远': 147,
     '核心': 1226,
     '利益': 597,
     '各族人民': 139,
     '所系': 6,
     '包容性': 127,
     '交往': 406,
     '交流': 2450,
     '交融': 189,
     '取向': 47,
     '宗教信仰': 11,
     '多元': 422,
     '并存': 40,
     '和谐': 473,
     '中华文化': 346,
     '世界': 4653,
     '兼收并蓄': 64,
     '开放': 2409,
     '胸怀': 161,
     '和平': 1471,
     '建设者': 153,
     '全球': 4646,
     '贡献者': 73,
     '国际': 6317,
     '秩序': 218,
     '维护者': 22,
     '追求': 506,
     '互鉴': 718,
     '霸权': 39,
     '价值观念': 24,
     '政治体制': 8,
     '强加于人': 13,
     '合作': 10473,
     '对抗': 149,
     '党同伐异': 2,
     '小圈子': 39,
     '深刻理解': 50,
     '重大意义': 70,
     '五千多年': 75,
     '深厚': 309,
     '开辟': 401,
     '基本原理': 92,
     '相结合': 379,
     '必由之路': 81,
     '这是': 860,
     '探索': 1307,
     '道路': 1157,
     '规律性': 66,
     '取得成功': 30,
     '法宝': 28,
     '第一': 652,
     '前提': 164,
     '契合': 189,
     '来源': 256,
     '高度': 583,
     '有机': 322,
     '成就': 687,
     '经由': 39,
     '新文化': 32,
     '形态': 195,
     '第三': 132,
     '筑牢': 211,
     '根基': 249,
     '关键': 899,
     '宏阔': 37,
     '深远': 93,
     '纵深': 81,
     '拓展': 962,
     '旧邦': 9,
     '新命': 8,
     '重焕': 29,
     '第四': 76,
     '打开': 282,
     '空间': 1055,
     '主动': 575,
     '制度': 2049,
     '思想解放': 16,
     '广阔': 346,
     '充分运用': 46,
     '宝贵': 231,
     '资源': 1985,
     '面向未来': 155,
     '第五': 27,
     '主体性': 113,
     '创立': 65,
     '这一': 691,
     '体现': 788,
     '中国化': 161,
     '时代化': 144,
     '经验': 1010,
     '规律': 336,
     '自觉性': 26,
     '担负起': 97,
     '起点': 171,
     '历经': 101,
     '数千年': 41,
     '绵延': 99,
     '忧患': 10,
     '经久不衰': 13,
     '人类文明': 369,
     '奇迹': 113,
     '底气': 119,
     '秉持': 328,
     '包容': 851,
     '博大': 20,
     '气象': 152,
     '得益于': 138,
     '自古以来': 51,
     '姿态': 104,
     '积极主动': 51,
     '借鉴': 250,
     '成果': 2102,
     '以守': 11,
     '正气': 33,
     '锐气': 28,
     '赓续': 141,
     '文脉': 186,
     '谱写': 227,
     '当代': 270,
     '华章': 87,
     '继承': 117,
     '礼敬': 18,
     '新形态': 67,
     '努力创造': 26,
     '回信': 113,
     '勉励': 65,
     '安徽省': 185,
     '山野': 23,
     '中学': 152,
     '考取': 15,
     '军校': 42,
     '同学': 126,
     '忠诚': 124,
     '刻苦': 49,
     '锤炼': 57,
     '作风': 96,
     '努力': 1383,
     '专业化': 149,
     '新型': 736,
     '军事': 104,
     '人才': 1831,
     '近日': 537,
     '20': 1121,
     '予以': 122,
     '亲切': 159,
     '从军报国': 9,
     '人生': 275,
     '考上': 17,
     '开启': 262,
     '军旅': 18,
     '生涯': 21,
     '表示祝贺': 15,
     '强军': 110,
     '一批': 809,
     '有志': 6,
     '青年': 956,
     '接续': 104,
     '国防': 173,
     '贡献力量': 207,
     '位于': 436,
     '大别山': 11,
     '革命': 466,
     '老区': 80,
     '国防教育': 124,
     '鲜明': 315,
     '该校': 23,
     '多名': 178,
     '学生': 1159,
     '报考': 19,
     '录取': 23,
     '给习': 4,
     '写信': 16,
     '表达': 263,
     '献身': 16,
     '矢志': 34,
     '决心': 214,
     '复信': 68,
     '史迪威': 59,
     '将军': 62,
     '后人': 28,
     '29': 142,
     '美国': 377,
     '外孙': 5,
     '约翰': 15,
     '伊斯特': 16,
     '布鲁克': 16,
     '感谢': 215,
     '来信': 15,
     '分享': 397,
     '家族': 37,
     '几代人': 16,
     '友好': 622,
     '故事': 887,
     '身上': 100,
     '感受': 645,
     '情谊': 71,
     '老朋友': 29,
     '解放': 58,
     '进步事业': 13,
     '给予': 320,
     '积极支持': 71,
     '中美': 69,
     '对此': 147,
     '忘记': 33,
     '前不久': 166,
     '重庆市': 129,
     '诞辰': 5,
     '140': 66,
     '周年纪念': 13,
     '活动': 2631,
     '视频': 466,
     '致辞': 331,
     '女儿': 58,
     '女婿': 2,
     '孙辈们': 1,
     '亲临现场': 2,
     '第五代': 10,
     '欣慰': 32,
     '回望': 44,
     '两国为': 4,
     '抗击': 42,
     '日本': 230,
     '法西斯': 7,
     '并肩战斗': 2,
     '展望未来': 67,
     '两国': 633,
     '中美关系': 106,
     '民间': 337,
     '源泉': 105,
     '两国人民': 283,
     '增进': 539,
     '两国关系': 198,
     '注入': 688,
     '新动力': 106,
     '成员': 382,
     '将会': 33,
     '致信': 53,
     '回顾': 98,
     '经历': 254,
     '介绍': 1539,
     '人文': 695,
     '支持': 3200,
     '致敬': 78,
     '中国政府': 240,
     '致力于': 384,
     '愿望': 120,
     '全国人大常委会': 336,
     '列席代表': 3,
     '座谈': 44,
     '充分发挥': 491,
     '人大代表': 120,
     '粮食安全': 406,
     '中共': 244,
     '中央政治局常委': 99,
     '委员长': 85,
     '日同': 3,
     '列席': 5,
     '十四届': 135,
     '第五次': 65,
     '确保': 725,
     '情况': 1218,
     '自觉': 375,
     '履职': 223,
     '提出': 2427,
     '意见建议': 72,
     '倾听': 64,
     '一系列': 773,
     '揭示': 96,
     '粮食': 611,
     '安全观': 75,
     '大政方针': 5,
     '政策': 2055,
     '强化': 1124,
     '党政': 70,
     '同责': 20,
     '全方位': 375,
     '夯实': 406,
     '指明': 257,
     '方向': 961,
     '提供': 3668,
     '地区': 2638,
     '艰苦': 54,
     '我国': 2995,
     '举世瞩目': 52,
     '巨大成就': 46,
     '吃不饱': 6,
     '吃得饱': 2,
     '历史性': 349,
     '清醒': 42,
     '不稳固': 7,
     '这根': 13,
     '特别': 772,
     '农业': 2083,
     '科技战线': 2,
     '要带头': 12,
     '宣传': 876,
     '法律法规': 107,
     '政策措施': 109,
     '引导': 837,
     '农民': 693,
     '耕地': 421,
     '保护意识': 16,
     '种粮': 104,
     '积极性': 151,
     '理念': 1568,
     '深入人心': 113,
     '本职工作': 16,
     '粮于': 29,
     '粮于技': 32,
     '落到实处': 70,
     '大户': 80,
     '合作社': 237,
     '龙头企业': 104,
     '扎根': 201,
     '农村': 1105,
     '土地': 364,
     '带动': 862,
     '多种': 291,
     '种好': 26,
     '奔头': 25,
     '产业': 4005,
     '专家学者': 128,
     '面向世界': 26,
     '科技前沿': 37,
     '核心技术': 219,
     '攻关': 239,
     '坚实': 219,
     '科技': 3480,
     '支撑': 1139,
     '技术员': 24,
     '基层': 930,
     '农技': 67,
     '推广': 620,
     '打通': 210,
     '进村': 34,
     '入户': 29,
     '公里': 470,
     '建言献策': 28,
     '调研': 503,
     '思考': 206,
     '注重': 455,
     '法律': 895,
     '层面': 191,
     '发现': 765,
     '影响': 826,
     '矛盾': 331,
     '短板': 179,
     '法定': 82,
     '渠道': 458,
     '解决问题': 137,
     '完善': 1751,
     '全国人大': 129,
     '涉及': 423,
     '建议': 402,
     '290': 5,
     '19': 405,
     '督办': 34,
     '办理': 383,
     '委员': 434,
     '副委员长': 90,
     '李鸿忠': 55,
     '主持': 232,
     '同志': 735,
     '朋友': 330,
     '隆重开幕': 27,
     '我受': 4,
     '委托': 97,
     '十九': 119,
     '统筹': 915,
     '全局': 217,
     '未有': 112,
     '大变局': 120,
     '带领': 313,
     '全党全军': 7,
     '效应': 242,
     '严峻': 101,
     '国际形势': 47,
     '接踵而至': 7,
     '攻克': 82,
     '解决': 1466,
     '难题': 427,
     '办成': 57,
     '事关': 149,
     '长远': 281,
     '大事': 137,
     '要事': 6,
     '重大成就': 38,
     '实践': 1807,
     '充分证明': 66,
     '发生': 644,
     '变革': 437,
     '全党': 97,
     '领航': 65,
     '掌舵': 32,
     '科学': 1585,
     '指引': 387,
     '历史进程': 60,
     '广泛开展': 84,
     '系列': 444,
     '品牌': 783,
     '引领': 1293,
     '改革': 1504,
     '着力': 947,
     '五年': 86,
     '主战场': 48,
     '第一线': 21,
     '科教': 65,
     '最前沿': 8,
     '乡村': 2042,
     '振兴': 1387,
     '行列': 35,
     '火热': 76,
     '活跃': 128,
     '身影': 75,
     '冬奥会': 65,
     '残奥会': 89,
     '运动员': 771,
     '拼搏': 141,
     '捐建': 2,
     '冬奥': 13,
     '冰雪': 86,
     '博物馆': 465,
     '窗口': 257,
     '心系': 30,
     '倾力': 27,
     '驰援': 12,
     '守望相助': 58,
     '携手': 863,
     '同行': 161,
     '紧紧': 92,
     '连在一起': 8,
     '奔走': 15,
     '中外': 272,
     '奉献': 170,
     '充分肯定': 51,
     '寄予厚望': 20,
     '擘画': 144,
     '宏伟蓝图': 76,
     '从现在起': 9,
     '心往': 15,
     '一处': 100,
     '劲往': 18,
     '紧跟': 46,
     '步伐': 260,
     '加快': 2613,
     '推动者': 42,
     '受益者': 69,
     '顺应': 186,
     '大势': 124,
     '资金': 927,
     '技术': 3444,
     '信息': 1065,
     '管理': 1971,
     '融通': 240,
     '内外': 107,
     '熟悉': 89,
     '规则': 487,
     '高水平': 1027,
     '自立自强': 229,
     '体系': 2698,
     '区域': 1620,
     '协调': 922,
     '共同富裕': 279,
     '绿色': 3041,
     '低碳': 493,
     '大显身手': 10,
     '畅通': 501,
     '国内': 913,
     '双循环': 102,
     '共建': 6328,
     '一带': 7480,
     '一路': 7629,
     '坚守': 332,
     '民族大义': 12,
     '一位': 170,
     '肩负': 45,
     '责任': 833,
     '不可或缺': 33,
     '所长': 72,
     '融洽': 9,
     '同胞': 100,
     '感情': 60,
     '共识': 693,
     '发展壮大': 190,
     '爱国': 190,
     '爱港': 5,
     '爱澳': 10,
     '一国两制': 52,
     '香港': 299,
     '澳门': 195,
     '融入': 692,
     '大局': 205,
     '作贡献': 55,
     '台湾': 255,
     '共同愿望': 24,
     '反独': 2,
     '促统': 9,
     '深化': 2159,
     '两岸': 440,
     '融合': 1940,
     '心灵': 91,
     '旗帜鲜明': 44,
     '反对': 343,
     '分裂': 84,
     '言论': 11,
     '大团结': 18,
     '热爱祖国': 9,
     '天下': 224,
     '离不开': 229,
     '康庄大道': 47,
     '社会': 3087,
     '持久和平': 69,
     '美好': 589,
     '梦想': 418,
     '人间正道': 58,
     '基因': 190,
     '讲好': 214,
     '传播': 836,
     '声音': 187,
     '民众': 421,
     '相互了解': 27,
     '全人类': 214,
     '价值': 951,
     '落实': 1656,
     '倡议': 2510,
     '各国': 1821,
     '一道': 558,
     '秉承': 52,
     '改革开放': 288,
     '一大批': 176,
     '桑梓': 9,
     '华侨': 35,
     '分不开': 4,
     '越来越': 875,
     '落地生根': 103,
     '繁衍生息': 10,
     '紧密结合': 68,
     '自强不息': 80,
     '艰苦创业': 7,
     '遵守': 86,
     '尊重': 406,
     '习俗': 26,
     '回馈': 15,
     '国同': 2,
     '牵线搭桥': 13,
     '中国共产党': 643,
     '肩负着': 36,
     '不懈': 97,
     '光荣': 126,
     '统领': 30,
     '武装': 89,
     '人心': 141,
     '画好': 7,
     '同心圆': 34,
     '国之大者': 85,
     '紧紧围绕': 94,
     '目标': 1230,
     '找准': 104,
     '切入点': 30,
     '结合点': 13,
     '急难': 138,
     '建功': 52,
     '联谊': 8,
     '联络': 13,
     '广交': 5,
     '深交': 2,
     '壮大': 218,
     '侨社': 1,
     '年轻一代': 31,
     '华裔': 1,
     '青少年': 277,
     '对祖': 1,
     '认同': 146,
     '水平': 1432,
     '治会': 1,
     '可信赖': 5,
     '温暖': 220,
     '深入开展': 155,
     '契机': 269,
     '贴心人': 12,
     ...}




```python
# 创建一个字典，用于存储每个领域的词频统计
category_word_counts = {}
# 遍历每个领域的关键词列表
for category_keywords in [category_keywords_politics, category_keywords_economy,category_keywords_culture,category_keywords_society,category_keywords_science,category_keywords_military,category_keywords_environment,category_keywords_domestic,category_keywords_internation]:
    # 初始化该领域的词频统计
    category_word_count = {}
    
    # 遍历关键词列表，统计词频
    for keyword in category_keywords:
        # 如果关键词存在于word_count中，将其词频添加到该领域的词频统计中
        if keyword in word_count:
            category_word_count[keyword] = word_count[keyword]
    
    # 将该领域的词频统计添加到category_word_counts字典中
    category_word_counts[category_keywords[0]] = category_word_count

category_word_counts_sum = {}
# 打印每个领域的词频统计
for category, word_count_ in category_word_counts.items():
    print(f'{category}词频统计：')
    sum = 0
    for keyword, count in word_count_.items():
        sum+=count
        print(f'{keyword}: {count}')
    category_word_counts_sum[category] = sum
    print()
print(category_word_counts_sum)
```

    政治与国际关系词频统计：
    政治: 1407
    党和政府: 49
    政权: 26
    外交政策: 39
    领导人: 418
    政治体制: 8
    政治经济: 20
    外交: 280
    外交事务: 9
    习近平: 7589
    
    经济与金融词频统计：
    经济: 6395
    金融: 1640
    贸易: 1558
    发展: 24279
    建设: 10094
    金融市场: 29
    经济体制: 55
    
    文化与教育词频统计：
    艺术: 734
    教育体制: 4
    文化教育: 25
    文化: 8010
    教育: 3988
    中华文化: 346
    传承: 1167
    历史: 3034
    学习: 1809
    诗词: 160
    弘扬: 784
    故宫: 11
    书法: 20
    博物馆: 465
    国学: 5
    
    社会与人民生活词频统计：
    社会: 3087
    人民: 4061
    生活: 1825
    医疗卫生: 130
    社会保障: 161
    社会福利: 4
    
    科技与创新词频统计：
    科技: 3480
    创新: 6649
    信息技术: 145
    科学研究: 75
    科技领域: 20
    
    军事与国防词频统计：
    国防: 173
    军事: 104
    军队: 130
    国防建设: 7
    官兵: 107
    部队: 170
    战士: 33
    连队: 20
    战友: 32
    战场: 34
    装备: 476
    军人: 41
    强军: 110
    海军: 43
    飞行员: 21
    空军: 18
    陆军: 14
    导弹: 7
    武警: 8
    
    环境与可持续发展词频统计：
    环境: 1932
    环境保护: 377
    气候变化: 480
    环境污染: 85
    
    国内地区报道词频统计：
    国内: 913
    地区: 2638
    
    国际报道词频统计：
    国际: 6317
    世界: 4653
    国际事务: 69
    
    {'政治与国际关系': 9845, '经济与金融': 44050, '文化与教育': 20562, '社会与人民生活': 9268, '科技与创新': 10369, '军事与国防': 1548, '环境与可持续发展': 2874, '国内地区报道': 3551, '国际报道': 11039}
    


```python
# 提取领域和词频数据
# 创建柱状图
plt.figure(figsize=(12, 5))
plt.barh(list(category_word_counts_sum.keys()), list(category_word_counts_sum.values()), color='skyblue')
plt.xlabel('词频统计')
plt.title('不同领域的词频统计')
plt.grid(axis='x', linestyle='--', alpha=0.6)
plt.gca().invert_yaxis()  # 逆序显示

# 显示图表
plt.show()
```


    
![png](images/output_16_0.png)
    



```python
def plot_word_count(word_count, title):
    plt.figure(figsize=(12, 5))
    plt.bar(word_count.keys(), word_count.values(), color='skyblue')
    plt.xlabel('领域')
    plt.ylabel('词频')
    plt.title(title)
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.6)
    plt.show()
```


```python
# 打印每个领域的词频统计
for category, word_count_ in category_word_counts.items():
    plot_word_count(word_count_, category)
```


    
![png](images/output_18_0.png)
    



    
![png](images/output_18_1.png)
    



    
![png](images/output_18_2.png)
    



    
![png](images/output_18_3.png)
    



    
![png](images/output_18_4.png)
    



    
![png](images/output_18_5.png)
    



    
![png](images/output_18_6.png)
    



    
![png](images/output_18_7.png)
    



    
![png](images/output_18_8.png)
    

