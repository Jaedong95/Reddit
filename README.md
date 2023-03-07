# Reddit
Reddit data crawling &amp; archieve data processing

### 0. Requirements 
#### 1) packages 
```python
zstd   - pip install zstandard 
```

#### 2) data directory
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

### 1. How to work 
#### 1) Extract data 
