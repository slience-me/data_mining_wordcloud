import requests
import bs4
import datetime
import multiprocessing
import os
import time
import jieba
import re
from zhon.hanzi import punctuation as puncZH
from string import punctuation as puncEN
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# ȫ������
encoding = 'utf-8'
global_path = '../data/'
font_path = '../Fonts/�������кڼ���.ttf'
width = 9000
height = 6000
punctuation_set = set(puncZH + puncEN)


def fetch_url(url):
    """
        ���ܣ����� url ����ҳ����ȡ��ҳ���ݲ�����
    :param url: Ŀ����ҳ�� url
    :return: Ŀ����ҳ�� html ����
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
        ���ܣ���ȡ���챨ֽ�ĸ�����������б�
    :param year: �� �ı�������ƴ�ӳ���Ҫ��ȡ��url
    :param month: ��
    :param day: ��
    :return: ���ص��챨ֽ�ĸ�����������б�
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
        ���ܣ���ȡ��ֽĳһ��������������б�
    :param year: ��
    :param month: ��
    :param day: ��
    :param pageUrl: �ð��������
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
        ���ܣ����� HTML ��ҳ����ȡ���ŵ���������
    :param html: html ��ҳ����
    :return: ����+����
    """
    bs_obj = bs4.BeautifulSoup(html, 'html.parser')

    # ��ȡ���� ����
    title = bs_obj.h3.text + '\n' + bs_obj.h1.text + '\n' + bs_obj.h2.text + '\n'
    # print(title)

    # ��ȡ���� ����
    p_list = bs_obj.find('div', attrs={'id': 'ozoom'}).find_all('p')
    content = ''
    for p in p_list:
        content += p.text + '\n'
    # print(content)

    resp = title + content
    return resp


def save_file(content, path, filename):
    """
        ���ܣ����������� content ���浽�����ļ���
    :param content: Ҫ���������
    :param path: ·��
    :param filename: �ļ���
    :return:
    """
    # ���û�и��ļ��У����Զ�����
    if not os.path.exists(path):
        os.makedirs(path)
        # print('��ȡ�����£�����������...')

    # �����ļ�
    with open(path + filename, 'w', encoding='utf-8') as f:
        f.write(content)
    # print('��ȡ�����£�����������...')
    # print('������д�룺' + path)


def download_rmrb(year, month, day, destdir):
    """
        ���ܣ���ȡ�������ձ�����վĳ��,ĳ��,ĳ�յ��������ݣ���������ָ��Ŀ¼��
    :param year: ��
    :param month: ��
    :param day: ��
    :param destdir: �ļ�����ĸ�Ŀ¼
    :return:
    """
    page_list = get_page_list(year, month, day)
    for page in page_list:
        title_list = get_title_list(year, month, day, page)
        for url in title_list:
            # ��ȡ������������
            html = fetch_url(url)
            content = get_content(html)
            # ���ɱ�����ļ�·�����ļ���
            temp = url.split('_')[2].split('.')[0].split('-')
            page_no = temp[1]
            title_no = temp[0] if int(temp[0]) >= 10 else '0' + temp[0]
            path = destdir + '/' + year + month + day + '/'
            file_name = year + month + day + '-' + page_no + '-' + title_no + '.txt'

            # �����ļ�
            save_file(content, path, file_name)
            # time.sleep(3) ����


def gen_dates(b_date, days):
    day = datetime.timedelta(days=1)
    for i in range(days):
        yield b_date + day * i


def get_date_list(beginDate, endDate):
    """
        ��ȡ�����б�
    :param beginDate: ��ʼ����
    :param endDate: ��������
    :return:
    """
    start = datetime.datetime.strptime(beginDate, "%Y%m%d")
    end = datetime.datetime.strptime(endDate, "%Y%m%d")

    data = []
    for d in gen_dates(start, (end - start).days + 1):
        data.append(d)
    # return: ���ؿ�ʼ���ںͽ�������֮��������б�
    return data

    # ���������������


def get_news(local_data):
    # ������ֹ���ڣ���ȡ֮�������
    print('---������ȡϵͳ---')
    begin_date = input('�����뿪ʼ����(��ʽ��20231101):')
    end_date = input('�������������(��ʽ��20231101):')
    data = get_date_list(begin_date, end_date)

    for d in data:
        year = str(d.year)
        month = str(d.month) if d.month >= 10 else '0' + str(d.month)
        day = str(d.day) if d.day >= 10 else '0' + str(d.day)
        # ��ȡ������tͳһ�浽����ļ���,û�л��Զ�����
        destdir = "../data"

        # �ж������Ƿ���local_data�У��������continue
        date = int(year + month + day)
        print(date)
        if date in local_data:
            print('��ȡ����ʱ��Ϊ��' + year + '/' + month + '/' + day + '�������Ѿ�����!')
            continue
        print('---��ʼ��ȡ���£�����Ϊ' + year + '/' + month + '/' + day + '---')
        # time.sleep(3) ����
        download_rmrb(year, month, day, destdir)
        print("��ȡ������ɣ�")


def get_news_path():
    """
        ��ȡ·���µ�ȫ����������
    :return: ȫ�����µ�·��
    """
    news_path = []
    for dirname, _, filenames in os.walk('../data'):
        for filename in filenames:
            news_path.append(os.path.join(dirname, filename).replace('\\', '/'))
    print("func get_news_path() is called��������������Ϊ: ", len(news_path))
    return news_path


def remove_punctuation(s: str):
    """
        ȥ��������
    :param s: ������ַ���
    :return: ȥ�������ź���ַ���
    """
    s = re.sub(r"[%s]+" % puncZH, "", s)
    s = re.sub(r"[%s]+" % puncEN, "", s)
    s = re.sub(r"[\d\n\t\r]+", "", s)
    return s


def has_punctuation(s: str):
    """
        �ж��ַ������Ƿ���ڱ�����
    :param s: ������ַ���
    :return: bool��ʶ
    """
    # f = False
    # f |= bool(re.match(r"[%s]+" % puncZH, s))
    # f |= bool(re.match(r"[%s]+" % puncEN, s))
    # f |= bool(re.match(r"[\d\n\t\r]+", s))
    # return f
    return any(char in punctuation_set for char in s)


def get_words(news: str):
    """
        ��ȡĳ·����ĳ�������ڵ�ȫ������
    :param news:
    :return:
    """
    split_news = jieba.lcut(news)  # ���þ�ȷģʽ���зִ�
    removed_split_news = []
    for text in split_news:
        if has_punctuation(text) is False:
            removed_split_news.append(text)
    return removed_split_news


def get_words_count(news_path):
    """
        ��ȡȫ�����µ�ȫ������
    :param news_path:
    :return:
    """
    words = []
    for path in news_path:
        # news = open(path, 'r', encoding=encoding).read()
        # words += get_words(news)
        with open(path, 'r', encoding=encoding) as file:
            news = file.read()
            words.extend(get_words(news))
    print('func get_words_count() is called����������: ', len(words))
    return words


from collections import Counter


def get_unique_words_count(words):
    """
        ͳ��ĳ������Ĵ�Ƶ��Ϣ
    :param words: �����б�
    :return: �����Ƶ���ֵ�
    """
    word_count = Counter(words)  # ʹ��collections.Counter��������ͳ�ƴ�Ƶ
    # word_count = {}
    # for word in words:
    #     word_count[word] = word_count.get(word, 0) + 1
    print('func get_unique_words_count() is called��ȥ�ش���ĸ�����', len(word_count))
    return word_count


def get_stop_words():
    """
        ��ȡͣ�ô�
    :return:
    """
    # stopwords = []
    # for dirname, _, filenames in os.walk('./stopwords-master'):
    #     for filename in filenames:
    #         with open(os.path.join(dirname, filename)) as f:
    #             if filename.endswith('txt'):
    #                 stopwords += list(f.read().split())
    #
    # stopwords.append('��')
    # stopwords.append('��')
    # stopwords.append('��')
    # stopwords.append('��')
    # stopwords.append('��')
    # stopwords.append('����')
    # stopwords.append('��')
    # stopwords.append('��')
    # stopwords.append('��')
    # stopwords.append('Ϊ')
    # stopwords.append('��')
    # stopwords.append('\xa0')
    #
    # stopwords = list(set(stopwords))
    # print('ͳ��ͣ�ô�����: ', len(stopwords))
    stopwords = set()
    for dirname, _, filenames in os.walk('../stopwords-master'):
        for filename in filenames:
            if filename.endswith('txt'):
                with open(os.path.join(dirname, filename)) as f:
                    stopwords.update(f.read().split())

    common_stopwords = {'��', '��', '��', '��', '��', '����', '��', '��', '��', 'Ϊ', '��', '\xa0', '\n', ' ', '��',
                        '��'}
    stopwords.update(common_stopwords)
    stopwords = list(stopwords)
    print('func get_unique_words_count() is called��ͳ��ͣ�ô�����: ', len(stopwords))
    return stopwords


def word_count_remove_stopword(word_count):
    """
        ��ȫ���������Ƴ�ͣ�ô�
    :param word_count:
    :return:
    """
    # stopwords = get_stop_words()
    # for stopword in stopwords:
    #     if stopword in word_count:
    #         word_count.pop(stopword)
    # print('����ֹͣ���Ψһ��������: ', len(word_count))
    stopwords = set(get_stop_words())
    word_count = {word: count for word, count in word_count.items() if word not in stopwords}
    print('func get_unique_words_count() is called������ͣ�ôʵ�Ψһ��������: ', len(word_count))
    word_count_no_single = {word: count for word, count in word_count.items() if len(word) > 1}
    print('func get_unique_words_count() is called��ȥ�������ֵ�Ψһ��������: ', len(word_count_no_single))
    return word_count_no_single


def timer_process():
    """
        ��ʱ�������ڼ�ʱ���ɴ���ͼ����ʱ��
    :return:
    """
    start_time = time.time()
    while True:
        current_time = time.time()
        elapsed_time = current_time - start_time
        print(f"����ͼ����ʱ���ʱ����ǰ�Ѿ���ʱ: {int(elapsed_time)} ��", end='\r')
        time.sleep(1)


def draw_wordcloud(word_count):
    """
        ���ɴ���ͼ������
    :param word_count: ��Ƶ�ֵ�
    :param font_path: ����·��
    :param width: ͼƬ���
    :param height: ͼƬ�߶�
    """
    start_time = time.time()
    print("��ʼ��ʼ��WordCloud init")
    wc = WordCloud(font_path=font_path, width=width, height=height, background_color="red",
                   max_words=1000,
                   color_func=lambda *args, **kwargs: (255, 255, 0))
    print("��ʼ�����! ��ʼ����WordCloudͼƬ!Ԥ��503��")
    timer = multiprocessing.Process(target=timer_process)
    timer.start()
    wc.generate_from_frequencies(word_count)
    # ������ִ����Ϻ󣬹رռ�ʱ����
    timer.terminate()
    timer.join()
    print("����ͼƬ���! ��ʼ����ͼƬ!")
    wc.to_file("People's Daily WordCloud Zh_1.png")
    plt.figure(figsize=(32, 16))
    plt.imshow(plt.imread("./People's Daily WordCloud Zh_1.png"))
    plt.axis("off")
    plt.show()
    print(f"�����ִ��ʱ�䣺{time.time() - start_time} ��")


def get_current_data_list():
    """
        ��ȡ��ǰ��������
    :param global_path:
    :return:
    """
    local_data = []
    for dirname, _, filenames in os.walk(global_path):
        if global_path == dirname:
            continue  # ������·��
        local_data.append(int(dirname.replace(global_path, '')))
    local_data.sort()
    print('��ǰ�Ѿ��е�������:', local_data)
    return local_data


def get_new_data():
    """
        �ж��û��Ƿ�Ҫ���������
    :return:
    """
    local_data = get_current_data_list()
    while True:
        flag = input("��������������? (Y/N): ").strip().upper()
        if flag == 'Y':
            get_news(local_data)
            break
        elif flag == 'N':
            print('�����������!')
            break
        else:
            print('������Y��N!')


if __name__ == '__main__':
    # ����������
    get_new_data()
    news_path = get_news_path()
    words = get_words_count(news_path)
    word_count = get_unique_words_count(words)
    word_count = word_count_remove_stopword(word_count)
    draw_wordcloud(word_count)
