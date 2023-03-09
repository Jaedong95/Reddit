# Reddit
##### reddit archive data curating 

##### 1) reddit submissions:  https://files.pushshift.io/reddit/submissions/
##### 2) reddit comment: http://files.pushshift.io/reddit/comments/

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
```

***
### 1. How to use 
##### 1) Extract data 
###### We extract data corresponding to the specified subreddit and year from the zst file.   
###### The extracted data is stored in the origin folder.

```bash
$ python data-extract.py --data_path {$DATA_PATH} --subreddit {$SUBREDDIT_NAME} --year {$YEAR} 
```

##### 2) Process data 
###### we pre-process reddit data to create dataset1.csv as follows
######   1. drop (na, cross post, deleted data)
######   2. delete rc that does not have parent rs post (rs: id, rc: link_id  - 't3_' + id)
######   3. cleanse text    
######   4. drop duplicates  -> dataset1.csv 

###### we pre-process reddit data to create dataset2.csv as follows 
######   1. split data (sep: '.') 
######   2. set max tokens (max tok: 32) 
######   3. cleanse text  (delete str len < 6) 
######   4. drop na 

###### Processed data is stored in the processed folder. (dataset1: document, dataset2: single sentence) 

```bash 
$ python data-process.py
```
