import os
import email
from nltk.tokenize import RegexpTokenizer
from nltk.stem.snowball import EnglishStemmer
from nltk.corpus import stopwords
import numpy as np
import math
import sqlite3

path = '/Users/apple/Downloads/maildir'


def getfilelist(mail_dir, filelist):
    if os.path.isfile(mail_dir):
        filelist.append(mail_dir)
    elif os.path.isdir(mail_dir):
        for s in os.listdir(mail_dir):
            newdir = os.path.join(mail_dir, s)
            getfilelist(newdir, filelist)
    return filelist


file_list = getfilelist(path, [])

tokenizer = RegexpTokenizer(r'[A-Za-z][A-Za-z]+')

es = EnglishStemmer()

forwardIndex = dict()
for i in range(len(file_list)):
    files = open(file_list[i], 'r')
    tokendict = dict()
    tempEmail = email.message_from_string(files.read())
    tempMessage = tempEmail.get_payload()
    tokens = list()
    tokens += (tokenizer.tokenize(str(tempEmail['Subject']) + str(tempMessage)))
    tokens_without_Stopword = [w for w in tokens if w not in stopwords.words('english')]
    tokens_stemmed = [es.stem(word) for word in tokens_without_Stopword]
    for token in tokens_stemmed:
        if token in tokendict:
            tokendict[token] += 1
        else:
            tokendict[token] = 1
    forwardIndex[file_list[i]] = tokendict
    print(i)
    files.close()

print("forwardIndex complete!")

con = sqlite3.connect("complete_path.db")
cur = con.cursor()

sql = "CREATE TABLE IF NOT EXISTS test(path text, id integer, primary key (path))"

cur.execute(sql)

it = 0
for i in forwardIndex:
    cur.execute("INSERT OR IGNORE INTO test(path, id) values(?, ?)", (i, it))

con.commit()

cur.close()
con.close()

invertIndex = dict()

word_tf_Index = dict()

for path in forwardIndex:
    dicts = forwardIndex[path]
    for words in dicts:
        times = dicts[words]
        if words not in invertIndex:
            invertIndex[words] = dict()
        invertIndex[words][path] = times

print("invertIndex complete!")

for i in invertIndex:
    times = 0
    for j in invertIndex[i].values():
        times += j
    word_tf_Index[i] = times

print("word_tf_Index complete!")

word_tf_Index_gt65 = dict()
for i in word_tf_Index:
    times = word_tf_Index[i]
    if times > 64:
        word_tf_Index_gt65[i] = times

top_1000 = sorted(word_tf_Index_gt65.items(), key=lambda kv: (kv[1], kv[0]))

top_1000_word = list()
top_1000_len = len(top_1000)

for i in range(0, 1000):
    top_1000_word.append(list(top_1000[top_1000_len-i-1])[0])

invertIndex_top1000 = dict()
for i in top_1000_word:
    invertIndex_top1000[i] = invertIndex[i]

top_1000_lexorder = sorted(invertIndex_top1000.items(), key=lambda kv: (kv[0], kv[1]))

top_1000_word_lexorder = list()
top_1000_lexorder_len = len(top_1000_lexorder)

for i in range(0, 1000):
    top_1000_word_lexorder.append(list(top_1000_lexorder[i])[0])

invertIndex_top1000_lexorder = dict()
for i in top_1000_word_lexorder:
    invertIndex_top1000_lexorder[i] = invertIndex_top1000[i]

print("invertIndex_top1000_lexorder complete!")

con = sqlite3.connect("complete_word.db")
cur = con.cursor()

sql = "CREATE TABLE IF NOT EXISTS test(word text, id integer, primary key (word))"

cur.execute(sql)

it = 0
for i in invertIndex_top1000_lexorder:
    cur.execute("INSERT OR IGNORE INTO test(word, id) values(?, ?)", (i, it))

con.commit()

cur.close()
con.close()

con = sqlite3.connect("complete_invertIndex_top1000_lexorder.db")

cur = con.cursor()

sql = "CREATE TABLE IF NOT EXISTS test(word text, id integer, path text , primary key (word, id))"

cur.execute(sql)

it = 0

for i in invertIndex_top1000_lexorder:
    it = 0
    for j in invertIndex_top1000_lexorder[i]:
        cur.execute("INSERT OR IGNORE INTO test(word, id, path) values(?, ?, ?)", (i, it, j))
        it += 1

con.commit()

cur.close()
con.close()

print("complete_invertIndex_top1000_lexorder.db complete!")

path_column_Index = dict()

word_line_Index = dict()

word_df_Index = dict()
it = 0
for i in forwardIndex:
    path_column_Index[i] = it
    it += 1

it = 0
for i in invertIndex_top1000_lexorder:
    word_line_Index[i] = it
    it += 1

N = len(forwardIndex)

for word in invertIndex_top1000_lexorder:
    word_df_Index[word] = N / len(invertIndex_top1000_lexorder[word])

line = len(invertIndex_top1000_lexorder)

column = len(forwardIndex)

tf_idf = np.zeros((line, column))

column_it = 0
for path in forwardIndex:
    word_tf = forwardIndex[path]
    word_tf_list_in_top1000 = list()
    for i in word_tf:
        word_tf_list_in_top1000.append(i)

    word_tf_list_in_top1000 = list(set(word_tf_list_in_top1000).intersection(set(top_1000_word_lexorder)))

    for word in word_tf_list_in_top1000:
        lineinmatrix = word_line_Index[word]
        columninmatrix = column_it
        tf_idf[lineinmatrix][columninmatrix] = (1+math.log(word_tf[word], 10))*math.log(word_df_Index[word], 10)

    column_it += 1

con = sqlite3.connect("complete_tf_idf_1000.db")
cur = con.cursor()

sql = "CREATE TABLE IF NOT EXISTS test(path text, word text, line integer, td_idf real , primary key (path, word))"


cur.execute(sql)

for i in invertIndex_top1000_lexorder:
    for j in invertIndex_top1000_lexorder[i]:
        cur.execute("INSERT OR IGNORE INTO test(path, word, line, td_idf) values(?, ?, ?, ?)",
                    (j, i, word_line_Index[i], tf_idf[word_line_Index[i]][path_column_Index[j]]))

con.commit()

cur.execute("create index path_index on test(path, word)")

con.commit()

cur.close()
con.close()

print("complete_tf_idf_1000.db complete!")
