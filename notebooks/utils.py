import chardet

# 读取文件内容并检测编码
with open('../stopwords-master/baidu_stopwords.txt', 'rb') as file:
    rawdata = file.read()
    result = chardet.detect(rawdata)

# 从检测结果中获取编码
detected_encoding = result['encoding']

print(f"The detected encoding is: {detected_encoding}")

with open('../stopwords-master/baidu_stopwords.txt', 'r', encoding=detected_encoding) as file:
    content = file.read()
