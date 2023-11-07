import multiprocessing
import os
import time

import jieba
from NewsGet import get_news
from random import sample
import re
from zhon.hanzi import punctuation as puncZH
from string import punctuation as puncEN
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# 全局配置
encoding = 'utf-8'


def get_news_path():
    news_path = []
    for dirname, _, filenames in os.walk('../data'):
        for filename in filenames:
            news_path.append(os.path.join(dirname, filename).replace('\\', '/'))
    print("新闻总数为: ", len(news_path))
    # print(news_path)
    return news_path


def removePunctuation(s: str):
    s = re.sub(r"[%s]+" % puncZH, "", s)
    s = re.sub(r"[%s]+" % puncEN, "", s)
    s = re.sub(r"[\d\n\t\r]+", "", s)
    return s


def hasPunctuation(s: str):
    f = False
    f |= bool(re.match(r"[%s]+" % puncZH, s))
    f |= bool(re.match(r"[%s]+" % puncEN, s))
    f |= bool(re.match(r"[\d\n\t\r]+", s))
    return f


def getWords(news: str):
    split_news = jieba.lcut_for_search(news)
    removed_split_news = []
    for text in split_news:
        if hasPunctuation(text) is False:
            removed_split_news.append(text)
    return removed_split_news


def get_words_count(news_path):
    words = []
    news_path_len = len(news_path)
    news_path_len_sample = int(news_path_len * 0.8)
    for path in sample(news_path, k=news_path_len_sample):
        news = open(path, 'r', encoding=encoding).read()
        words += getWords(news)
    print('词语数量: ', len(words))
    return words


def get_unique_words_count(words):
    word_count = {}
    for word in words:
        word_count[word] = word_count.get(word, 0) + 1
    print('去重词语的个数：', len(word_count))
    return word_count


def get_stop_words():
    stopwords = []
    for dirname, _, filenames in os.walk('./stopwords-master'):
        for filename in filenames:
            with open(os.path.join(dirname, filename)) as f:
                if filename.endswith('txt'):
                    stopwords += list(f.read().split())

    stopwords.append('年')
    stopwords.append('月')
    stopwords.append('日')
    stopwords.append('上')
    stopwords.append('中')
    stopwords.append('本报')
    stopwords.append('的')
    stopwords.append('和')
    stopwords.append('在')
    stopwords.append('为')
    stopwords.append('了')
    stopwords.append('\xa0')

    stopwords = list(set(stopwords))
    print('统计停止词总数: ', len(stopwords))
    return stopwords


def data_handle_word_ds(word_count):
    word_ds = pd.DataFrame(word_count, index=[0])
    word_ds = word_ds.T
    word_ds.columns = ['count']
    word_ds.sort_values(by=['count'], ascending=False, inplace=True)
    return word_ds


def word_count_remove_stopword(word_count):
    stopwords = get_stop_words()
    for stopword in stopwords:
        if stopword in word_count:
            word_count.pop(stopword)
    print('不带停止语的唯一单词总数: ', len(word_count))
    return word_count


def timer_process():
    start_time = time.time()
    while True:
        current_time = time.time()
        elapsed_time = current_time - start_time
        print(f"词云图生成时间计时，当前已经用时: {int(elapsed_time)} 秒", end='\r')
        time.sleep(1)


def draw_wordcloud(word_count):
    start_time = time.time()
    print("开始初始化WordCloud init")
    wc = WordCloud(font_path='../Fonts/方正正中黑简体.ttf', width=9000, height=6000, background_color="red",
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
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"代码块执行时间：{elapsed_time} 秒")


def get_current_data_list(global_path):
    local_data = []
    for dirname, _, filenames in os.walk(global_path):
        if global_path == dirname:
            continue  # 跳过根路径
        local_data.append(int(dirname.replace(global_path, '')))
    local_data.sort()
    print('当前已经有的数据有:', local_data)
    return local_data


def get_new_data(global_path):
    local_data = get_current_data_list(global_path)
    while (True):
        flag = input("新增文章数据吗?输入Y或N")
        if flag == 'Y':
            get_news(local_data)
            break
        elif flag == 'N':
            print('不添加新数据!')
            break
        else:
            print('请输入Y或N!')


if __name__ == '__main__':
    global_path = '../data/'
    get_new_data(global_path)
    news_path = get_news_path()
    words = get_words_count(news_path)
    word_count = get_unique_words_count(words)
    word_count = word_count_remove_stopword(word_count)
    draw_wordcloud(word_count)
