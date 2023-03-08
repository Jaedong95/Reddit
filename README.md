# Reddit
##### reddit archiev data curating 

##### 1) reddit submissions:  https://files.pushshift.io/reddit/submissions/
##### 2) reddit comment: http://files.pushshift.io/reddit/comments/

***
### 0. Requirements 
##### 1) packages 
```python
zstd   - pip install zstandard 
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
###### - delete cross post, post that contains url, mention(@), tags(#) and NULL post 
###### - cleanse data 
###### - split data (sep: '.') 
###### - delete comments that do not have parent post 

###### Processed data is stored in the processed folder. (dataset1: document, dataset2: single sentence) 

```bash 
$ python data-process.py
```
