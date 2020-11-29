from nltk.tokenize import RegexpTokenizer
from nltk.stem.snowball import EnglishStemmer
from nltk.corpus import stopwords
import sqlite3
import math
import time
import re

begin = time.time()

tokenizer = RegexpTokenizer(r'[A-Za-z][A-Za-z]+')

es = EnglishStemmer()

# inputstr = "team customers project price natural"
inputstr = "team customers"

con = sqlite3.connect("complete_word.db")
cur = con.cursor()

words_list = list()

for word in cur.execute("select word from test"):
    words_list.append(word[0])

cur.close()
con.close()

con = sqlite3.connect("complete_path.db")
cur = con.cursor()

files_list = list()

for file in cur.execute("select path from test"):
    files_list.append(file[0])

cur.close()
con.close()

con = sqlite3.connect("complete_invertIndex_top1000_lexorder.db")
cur = con.cursor()

tokens_input = list()
tokens_input += (tokenizer.tokenize(inputstr.lower()))
tokens_input_without_Stopword = [w for w in tokens_input if w not in stopwords.words('english')]
tokens_input_stemmed = [es.stem(word) for word in tokens_input_without_Stopword]

tokens_OR = list()
it = 0
if len(tokens_input_stemmed)-1 is 0:
    tokens_OR.append(tokens_input_stemmed[it])
else:
    for it in range(len(tokens_input_stemmed)-1):
        tokens_OR.append(tokens_input_stemmed[it])
        tokens_OR.append("OR")
    tokens_OR.append(tokens_input_stemmed[it+1])

input_bool_str = ""

for i in tokens_OR:
    input_bool_str += i


def match_query(input_str):
    if re.search('AND', input_str) is not None:
        begin = re.search('AND', input_str).span()[0]
        end = re.search('AND', input_str).span()[1]
        temp1 = input_str[0:begin]
        temp2 = input_str[end:len(input_str)]

        return list(set(match_query(temp1)).intersection(set(match_query(temp2))))

    elif re.search('OR', input_str) is not None:
        begin = re.search('OR', input_str).span()[0]
        end = re.search('OR', input_str).span()[1]
        temp1 = input_str[0:begin]
        temp2 = input_str[end:len(input_str)]

        return list(set(match_query(temp1)).union(set(match_query(temp2))))

    elif re.search('NOT', input_str) is not None:
        end = re.search('NOT', input_str).span()[1]
        temp = input_str[end:len(input_str)]
        return list(set(files_list).difference(set(match_query(temp))))

    else:
        templist = list()
        for row in cur.execute("select * from test where test.word = '" + input_str + "'"):
            templist.append(row[2])
        return templist


path_semantic = match_query(input_bool_str)

cur.close()
con.close()

con = sqlite3.connect("complete_tf_idf_1000.db")
cur = con.cursor()

len_invertindex = 1000


def tf_idf_path(path, leninvertindex):
    templist = list()
    temploc = dict()
    for tempword in words_list:
        for row in cur.execute("select * from test where path = '" + path + "' and word = '" + tempword + "'"):
            temploc[row[2]] = row[3]
    for i in range(0, leninvertindex):
        if temploc.get(i) is not None:
            templist.append(temploc[i])
        else:
            templist.append(0)
    return templist


def input_tf_idf(tokensinputstemmed):
    temp = list()
    for it in range(len_invertindex):
        flag = 0
        for j in range(len(tokensinputstemmed)):
            if words_list[it] == tokensinputstemmed[j]:
                temp.append(1)
                flag = 1
        if flag == 0:
            temp.append(0)
    return temp


def cosine(lista, listb):
    mulab = 0
    mulaa = 0
    mulbb = 0
    for it in range(0, len(lista)):
        if lista[it] is not 0:
            mulaa += lista[it] * lista[it]
            if listb[it] is not 0:
                mulab += lista[it] * listb[it]
                mulbb += listb[it] * listb[it]
    if mulbb is 0:
        return 0
    else:
        return mulab / (math.sqrt(mulaa) * math.sqrt(mulbb))


input_tfidf = input_tf_idf(tokens_input_stemmed)

cos_list = dict()

for i in path_semantic:
    cos_list[i] = cosine(input_tfidf, tf_idf_path(i, len_invertindex))

cos_list_maxorder = sorted(cos_list.items(), key=lambda kv: (kv[1], kv[0]))

top_5 = list()
len_cos_list_maxorder = len(cos_list_maxorder)

for i in range(5):
    top_5.append(list(cos_list_maxorder[len_cos_list_maxorder-i-1])[0])

print(top_5)

end = time.time()
print("semantic check total cost:" , end - begin)

cur.close()
con.close()
