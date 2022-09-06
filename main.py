import math
import re
import pandas as pd
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from googleapiclient.discovery import build

stemmer = SnowballStemmer("russian")
stop_words = set(stopwords.words('russian'))
api_key = "AIzaSyCJk-C6RJfzZahZSiuTg4Ahs-xGjKF2jMo"
video_id = ["yMBHihjcgaA", "-kicGBIh5dw", "70JDd-Ywnio", "37v1PJqG06g", "7hQqaEvXPho", "m13BBD6wAFQ", "FAl7z9w0e5k",
            "6LEUTrA5NrE", "isW8jWoEPGE", "dFeimaTDX84"]
col = ['Author', 'Text', 'Likes', 'Date']


def tf_calc(dictionary, sum_nk):
    local_dict = {}
    for word, counts in dictionary.items():
        local_dict[word] = counts / sum_nk  # Делим количество вхождений на количество слов.
    return local_dict


def df_download(dataFrame):
    for v_id in video_id:  # Проходимся по видео
        request = resource.commentThreads().list(
            part="snippet",
            videoId=v_id,
            maxResults=100,
            order="orderUnspecified")
        response = request.execute()
        items = response["items"][:1000]
        for item in items:  # Проходимся по комментариям
            item_info = item["snippet"]
            line = []
            topLevelComment = item_info["topLevelComment"]
            comment_info = topLevelComment["snippet"]
            line.append(comment_info["authorDisplayName"])
            line.append(comment_info["textDisplay"])
            line.append(comment_info["likeCount"])
            line.append(comment_info["publishedAt"])
            y_data.append(line)
    dataFrame = pd.DataFrame(data=y_data)  # Записываем результат в датафрейм
    return dataFrame

def df_manipulation(dataFrame):
    index = 0
    for string in df['Text']:  # Проходимся по тексту комментариев
        df.loc[index, 'Text'] = re.sub("[^А-Яа-я0-9 ё]", "", string).lower()  # Удаляем ненужные символы
        my_string = df.loc[index, 'Text'].split()  # Возвращаем формат

        """ Uncomment this if not need numbers
        my_string = "".join((char for char in df.loc[index, 'Text'] if not char.isdigit()))
        my_string = my_string.split()
        """

        final_list = [word for word in my_string if word not in stop_words]  # Проверяем стоп-слова
        final = [stemmer.stem(word) for word in final_list]  # Стемминг
        df.loc[index, 'Text'] = ' '.join(final)  # И опять возвращаем формат, так как работали не со string, а с char[]
        index += 1
    return dataFrame


if __name__ == "__main__":

    resource = build('youtube', 'v3', developerKey=api_key)
    word_dict = {}
    arr = []
    y_data = []
    _len = 0
    this_key = ""

    df = pd.DataFrame(data=y_data)
    df = df_download(df)  #  Функция загрузки
    df.columns = col  # Обьявляем колонки
    df.to_csv('BeforeChange.csv', index=False, header=True)  #  Запись в файл
    print("All comments in BeforeChange.csv")  # Все комментарии будут загружены в файл BeforeChange.csv
    df = df_manipulation(df)  #  Функция изменения
    df.to_csv('AfterChange.csv', index=False, header=True)  #  Запись в файл
    print("Edited comments in AfterChange.csv")  # Записываем получившиеся в AfterChange.csv


    for comments in df['Text']:  # Пробегаемся по тексту комментариев
        comments = comments.split()
        word_set = set(comments)
        dict_comm = dict.fromkeys(word_set, 0)
        for word in comments:  # Проверяем на наличие слова в словаре
            if word not in word_dict:
                word_dict[word] = 0  # Ставим нули если ещё не в словаре
        for word in comments:  # Считаем количество
            word_dict[word] += 1
            dict_comm[word] += 1
        arr.append(dict_comm)

    _len = len(word_dict.keys())
    tf = tf_calc(word_dict, _len)  # Вызываем функцию по словарю и длине

    #  Создание словарей с нулями
    idf = dict.fromkeys(word_dict.keys(), 0)
    tfidf = dict.fromkeys(word_dict.keys(), 0)

    for word in word_dict.keys():  # Снова проходим
        word_counts = 0
        for dict_comm in arr:  # По массиву словарей
            if word in dict_comm:
                word_counts += 1
        idf[word] = math.log(len(arr) / word_counts)  #  log длины массива на количество вхождений

    for word in word_dict:
        tfidf[word] = tf[word] * idf[word]

    #  Тут начинается запись по файлам

    with open('bag.txt', 'w') as file:  #  Запись мешка слов
        for key, value in tfidf.items():
            file.write(f'{key}\n')
    print("bag words in bag.txt")

    with open('tfidf.txt', 'w') as file:  #  Запись tfidf
        for key, value in tfidf.items():
            file.write(f'{key}, {value}\n')
    print("tfidf in tfidf.txt")

    """ Uncomment this if not need numbers as separate words
    with open('tfidf.txt', 'w') as file:
        for key, value in tfidf.items():
            if not key.isdigit():
                file.write(f'{key}, {value}\n')
    """

    print("Success.")
