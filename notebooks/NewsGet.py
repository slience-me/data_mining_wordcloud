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
            time.sleep(120)  # 休眠120s


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
    beginDate = input('请输入开始日期(格式如20231101):')
    endDate = input('请输入结束日期(格式如20231101):')
    data = get_date_list(beginDate, endDate)

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
