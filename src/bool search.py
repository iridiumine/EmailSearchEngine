from nltk.tokenize import RegexpTokenizer
from nltk.stem.snowball import EnglishStemmer
import re
import sqlite3
import time

begin = time.time()

tokenizer = RegexpTokenizer(r'[A-Za-z][A-Za-z]+')

es = EnglishStemmer()

inputstr = "team AND project AND customers AND price OR NOT natural"

con = sqlite3.connect("complete_path.db")
cur = con.cursor()

files_list = list()

for file in cur.execute("select path from test"):
    files_list.append(file[0])

cur.close()
con.close()

con = sqlite3.connect("complete_invertIndex_top1000_lexorder.db")
cur = con.cursor()


def stem_input(input_str):
    tokens_input = list()
    tokens_input += (tokenizer.tokenize(input_str))

    for i in range(len(tokens_input)):
        if tokens_input[i] != 'AND':
            if tokens_input[i] != 'OR':
                if tokens_input[i] != 'NOT':
                    tokens_input[i] = es.stem(tokens_input[i])

    tempstr = ""
    for i in range(len(tokens_input)):
        tempstr += tokens_input[i]

    return tempstr


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


print(match_query(stem_input(inputstr)))
print(len(match_query(stem_input(inputstr))))

end = time.time()
print("bool check total cost:" , end - begin)

cur.close()
con.close()
