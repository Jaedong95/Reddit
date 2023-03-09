# Reddit
##### reddit archive data curating 

###### 1) reddit submissions:  https://files.pushshift.io/reddit/submissions/
###### 2) reddit comment: http://files.pushshift.io/reddit/comments/

***
### 0. Requirements 
##### 1) packages 
```python
zstd   - pip install zstandard 
nltk   - pip install nltk
```

##### 2) data directory
```bash 
|---data 
|   |---2010
|   |   |--- RS_2010-01.zst 
|   |   |--- ... 
|   |   |--- RS_2010-12.zst 
|   |   |--- RC_2010-01.zst 
|   |   |--- ...
|   |   |--- RC_2010-12.zst
|   |---origin
|   |   |--- rs_2010.csv 
|   |   |--- rc_2010.csv 
|   |   |--- ...  
|   |---processed
|   |   |--- dataset1.csv 
|   |   |--- dataset2.csv 
|   |   |--- dataset3.csv
```
***
### 1. Data Explanation  
##### 1) rs*.csv, rc*.csv (origin folder) 
###### extracted data from RS*.zst, RC*.zst  

##### 2) dataset1.csv 
###### it's text is consist of multi sentence  (column: id, subreddit, text, type: title, post, comment) 

##### 3) dataset2.csv 
###### it's text is consist of single sentence  (column: id, subreddit, text, type: title, post, comment) 

##### 4) dataset3.csv 
###### we remove personal info from dataset2.csv using bert ner tagger 

***
### 2. How to use 
##### 1) Extract data 
###### We extract data corresponding to the specified subreddit and year from the zst file.   

```bash
$ python data_extract.py --data_path {$DATA_PATH} --subreddit {$SUBREDDIT_NAME} --year {$YEAR} 
```
##### The extracted data is stored in the origin folder.

##### 2) Process data 
###### we pre-process reddit data to create dataset1.csv as follows

```bash
$ python create_dataset1.py --data_path {$DATA_PATH} --subreddit {$SUBREDDIT_NAME} --year {$YEAR} 
```

###### we pre-process datset1.csv to create dataset2.csv as follows 

```bash
$ python create_dataset2.py --data_path {$DATA_PATH} --subreddit {$SUBREDDIT_NAME} --year {$YEAR} 
```

##### Processed data is stored in the processed folder. (dataset1: document, dataset2: single sentence)
