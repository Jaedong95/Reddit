import json
import os 
import re 
import pandas as pd 
import nltk
import io 
import zstandard as zstd
from pathlib import Path
import json
import matplotlib.pyplot as plt 
from nltk.tokenize import word_tokenize

class Zstd():
    def __init__(self):
        self.dctx = zstd.ZstdDecompressor(max_window_size=2**31)

    def read_lines_from_zst_file(self, zstd_file_path:Path):
        with (
            zstd.open(zstd_file_path, mode='rb', encoding='utf-8', dctx=self.dctx) as zfh,
            io.TextIOWrapper(zfh, encoding='utf-8') as iofh
        ):
            for line in iofh:
                yield line       


class RedditData():
    def __init__(self, subreddit, data_path):
        self.subreddit = subreddit
        self.data_path = data_path
        self.file_list = os.listdir(self.data_path)   # 2010_

    def extract_subreddit(self, year, reddit_type, zstd):
        '''
        zst 파일에서 지정한 subreddit에 해당하는 데이터만 추출 
        '''
        assert reddit_type in ['rs','rc','RS','RC']
        
        reddit_info = []
        
        reddit = [file for file in self.file_list if file.lower().startswith(reddit_type.lower()) and year in file]
        print(reddit)
        for reddit_f in reddit: 
            reddit_file = Path(os.path.join(self.data_path, reddit_f))   # reddit_file(str): RS_2010-01.zst, ... 
            reddit_records = map(json.loads, zstd.read_lines_from_zst_file(reddit_file))   # read data from zst files 
            try:    # skip null data ('')
                for reddit_record in reddit_records:
                    try:    # skip abnormal data that doesn't have subreddit 
                        assert reddit_record['subreddit']     
                    except: 
                        continue 
                    if reddit_record['subreddit'] == self.subreddit:
                        reddit_info.append(reddit_record)
                        continue
            except:
                continue
        return reddit_info
        
    def convert_df(self, reddit_info):
        '''
        convert reddit info (dict) to reddit df (dataframe) 
        '''
        columns = reddit_info[0].keys()
        reddit_df = pd.DataFrame(reddit_info, columns=columns)
        return reddit_df
    
    def load_df(self, filename):
        reddit_df = pd.read_csv(filename)
        return reddit_df
    
    def save_df(self, reddit_df, filename):
        reddit_df.to_csv(filename, index=False)


class RedditProcessor():
    def __init__(self, data_path, save_path):
        self.data_path = data_path
        self.save_path = save_path
    
    def drop_na(self, reddit_df, type=0, tok=None):
        '''
        type: 0  - only drop NULL, NaN
        type: 1  - drop NaN + tok 
        '''
        # reddit_df.dropna(axis=0, subset=[col], inplace=True) 
        reddit_df.dropna(inplace=True)
        reddit_df.reset_index(inplace=True, drop=True) 
        return reddit_df 
    
    def drop_duplicates(self, col, reddit_df):
        #print(reddit_df[reddit_df[col].duplicated()])
        reddit_df.drop_duplicates(subset=[col], keep='first', inplace=True)
        reddit_df.reset_index(inplace=True, drop=True)
        return reddit_df
    
    def drop_odd(self, col, reddit_df):
        '''
        cross post, deleted 
        '''
        odd_idx = []
        # print(len(reddit_df[reddit_df[col].str.contains('deleted')].selftext))
        odd_idx.extend(reddit_df[reddit_df[col].str.contains('cross post')].index.tolist())
        odd_idx.extend(reddit_df[reddit_df[col].str.contains('deleted')].index.tolist())
        reddit_df.drop(odd_idx, inplace=True) 
        reddit_df.reset_index(drop=True, inplace=True)
        return reddit_df

    def cleanse_text(self, text):
        if isinstance(text, float):
            return None
        
        text = text.lower()   # lower case
        text = re.sub(r"http\S*|\S*\.com\S*|\S*www\S*", " ", text)    # delete url 
        text = re.sub(r"\s@\S+", " ", text)   # delete @mentions
        text = re.sub(r"\s+", " ", text)   # replace all whitespace with a single space
        text = text.strip()    # strip off spaces on either end
        
        if len(text) < 6: 
            return None
        return text
    
    def split_sent(self, text):
        '''
        input: document 
        output: sentence list [[sent1], [sent2], ...]
        '''
        return text.split('.')
    
    def convert_df(self, subreddit, reddit_df, reddit_type):
        '''
        reddit_df.text: list of text 
        new_df.text: single text  
        '''
        reddit_t = reddit_df.copy()
        reddit_t = reddit_t[reddit_t.type==reddit_type]
        reddit_t.reset_index(drop=True, inplace=True) 
        text_list = [text.split('.') for text in reddit_t.text.values.tolist()]
        new_df = []
        for idx in range(len(text_list)):
            for text in text_list[idx]:
                if text == '':
                    continue 
                text = text.strip()
                new_df.append([reddit_t.id[idx], subreddit, text, reddit_type])
        new_df = pd.DataFrame(new_df, columns = ['id', 'subreddit', 'text', 'type'])
        new_df.reset_index(inplace=True, drop=True) 
        return new_df 

    def get_token_list(self, reddit_df):
            return [word_tokenize(context) for context in reddit_df.text.values.tolist()]
    
    def set_max_tok(self, reddit_df, max_len):
        tok_list = self.get_token_list(reddit_df)
        idx_list = [idx for idx in range(len(tok_list)) if len(tok_list[idx]) <= max_len]
        reddit_df = reddit_df.loc[idx_list]
        reddit_df.reset_index(inplace=True, drop=True)
        return reddit_df

    def map_rc_rs(self, reddit_df):
        '''
        submission이 존재하지 않는 comment 제거 후, reddit_rc 반환하는 함수 
        '''
        reddit_rs = reddit_df.copy()
        reddit_rs = reddit_rs[reddit_rs.type.isin(['post', 'title'])]
        id_list = reddit_rs.id.unique().tolist()
        id_list = ['t3_' + id for id in id_list]
        reddit_rc = reddit_df.copy()
        reddit_rc = reddit_rc[reddit_rc.id.isin(id_list)]
        reddit_df = pd.concat([reddit_rs, reddit_rc])
        reddit_df.reset_index(drop=True, inplace=True)
        return reddit_df
