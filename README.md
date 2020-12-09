# Email Searching Engine
[This code has been uploaded to GitHub](https://github.com/iridiumine/EmailSearchEngine)<br>
[This output has been uploaded to Baidu Netdisk, Extraction code:WEB1](https://pan.baidu.com/s/1CQxwJn8m3QDXwRNk8nx09g)<br>
## Introduction
An email searching engine based on Enron Email Database, which provides bool search and semantic search.<br>
Maintained by <br>
[Yunhao Sha](https://github.com/PercySHA/)([percy@mail.ustc.edu.cn](mailto:percy@mail.ustc.edu.cn))<br>
[Shuyi Zhang](https://github.com/iridiumine)([iridiumine@mail.ustc.edu.cn](mailto:iridiumine@mail.ustc.edu.cn))<br>
## Language
python3<br>

## directory structure
```log
.
│  README.md                                            ->you are here
│  
├─dataset                                               
│  │  dirty.py                                          ->To clean up dirty data not encoded by UTF-8
│  │  utf_8_exp.txt                                     ->Records of deleted dirty data
│  │                        
│  ├─dirty data(empty)                                  ->Dirty data directory,empty
│  └─maildir(empty)                                     ->Cleaned data directory,empty
├─output
│      complete_invertIndex_top1000_lexorder.db         ->Inverted list of Top 1000 words in frequency,lexicographic ordered
│      complete_path.db                                 ->The database file that contains the absolute path of all data
│      complete_tf_idf_1000.db                          ->Tf-idf matrix of Top 1000 words in frequency
│      complete_word.db                                 ->The database file that contains Top 1000 words
│      
└─src
       bool_search.py                                   ->Bool search,using complete_path.db and complete_invertIndex_top1000_lexorder.db
       main.py                                          ->Generate the database files needed for retrieval                                        
       semantic_search.py                               ->Sematic search,using complete_path.db, complete_word.db and complete_tf_idf_1000.db
```
## Data preprocessing
3 types of mails in the original mail dataset. Ordinary mail which can be decoded with ASCII accounts for the majority;some of the rest can be decoded by gbk instead, but they may be garbled after decoding; the rest cannot be decoded by gbk. We only use the first type of mail, using dirty.py to clean up the dataset.

## Generate inverted list and tf-idf matrix

Execute `main.py`(We have run it locally and upload the database files generated to the output folder, so you don't have to do this)

## bool search

Execute `bool_search.py` to complete a bool search, the program will return the absolute paths that meet the query.

## semantic search

Execute `semantic_search.py` to complete a semantic search, the program will return the absolute paths that meet the query.This may be a little slow, please be patient.
