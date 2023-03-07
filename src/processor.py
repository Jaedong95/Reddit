import json
import os 
import re 
import pandas as pd 
import nltk
import matplotlib.pyplot as plt 
from nltk.tokenize import word_tokenize

class RedditData():
    def __init__(self, subreddit, data_path):
        self.subreddit = subreddit
        self.data_path = data_path
        self.file_list = os.listdir(self.data_path)   # 2010_
        self.rs_dtype = {'id': str, 'subreddit': str, 'author': str, 'title': str, 'context': str, 'url': str}
        self.rc_dtype = {'id': str, 'subreddit': str, 'author': str, 'comment': str}
         
    def extract_info(self, year, reddit_type):
        assert reddit_type in ['rs','rc','RS','RC']
        
        reddit_info = []
        error_list = []
        
        reddit = [file for file in self.file_list if file.startswith(reddit_type) and year in file]
        print(reddit)
        for month in reddit: 
            reddit_file = open(os.path.join(self.data_path, month), 'r')
            reddit_data = reddit_file.readlines()
            
            print(f'{month}월, 데이터 개수: {len(reddit_data)}')
            for reddit_content in reddit_data:
                try:
                    reddit_json = json.loads(reddit_content)
                    # 간혹 json file의 key 값에 reddit, reddit_id가 없는 경우 존재 (외부 게시글)
                    if reddit_type.lower() == 'rs':
                        assert reddit_json['subreddit'], reddit_json['selftext']
                    elif reddit_type.lower() == 'rc':
                        assert reddit_json['subreddit'], reddit_json['comment']
                except:
                    error_list.append(reddit_content)
                    continue 
                    
                if self.check_condition(reddit_json, reddit_type):
                    reddit_info.append(reddit_json)
        
        print(reddit_info)
        print(f'{len(error_list)}개의 파일 로드에 실패하였습니다.')
        return reddit_info, error_list
        
    def convert_to_df(self, reddit_info, reddit_type):
        reddit_df = []
        columns = []
        errs = []
        for info in reddit_info:
            if reddit_type == 'RS':
                columns = ['id', 'subreddit', 'author', 'title', 'context', 'comments', 'score', 'url', 'created_utc']
                try:
                    reddit_df.append([str(info['id']), self.subreddit, info['author'], info['title'], info['selftext'], \
                                      info['num_comments'], info['score'], info['url'], info['created_utc']])
                except:
                    errs.append(info)
                    continue
                
            elif reddit_type == 'RC':   # 2016년도에는 comment -> body로 변경됨, downs 없어짐 
                columns = ['id', 'subreddit', 'author', 'body', 'ups', 'downs', 'score', 'created_utc']
                try:
                    reddit_df.append([str(info['link_id']), self.subreddit, info['author'], info['comment'], info['ups'], \
                                      info['downs'], info['score'], info['created_utc']]) 
                except:
                    errs.append(info)
                    continue       
        
        print(f'변환 과정 중 {len(errs)}개의 파일 오류 발생')
        reddit_df = pd.DataFrame(reddit_df, columns=columns)            
        return reddit_df
    
    def load_data(self, file_name, reddit_type):
        assert reddit_type in ['rs', 'rc', 'RS', 'RC']
        reddit_df = pd.read_csv(os.path.join(self.save_path, file_name), \
                                dtype=self.rs_dtype if reddit_type.lower=='rs' else self.rc_dtype, engine='python')
        return reddit_df
    
    def save_df(self, reddit_df, filename):
        reddit_df.to_csv(os.path.join(self.save_path, filename), index=None)


class RedditProcessor():
    def __init__(self, data_path, save_path):
        self.data_path = data_path
        self.save_path = save_path
    
    def drop_na(self, reddit_df, reddit_type, na_type):
        '''
        na_type: 'na' (None object) or 'nc' ('')
        '''
        assert na_type in ['na','nc']
        assert reddit_type in ['rs', 'rc', 'RS', 'RC']
        
        if na_type == 'na':
            reddit_df.dropna(inplace=True)
        else:
            if reddit_type.lower() == 'rs':
                reddit_df = reddit_df[reddit_df.title != '']
                reddit_df = reddit_df[reddit_df.context != '']
            else:
                reddit_df = reddit_df[reddit_df.body != '']
        reddit_df.reset_index(inplace=True, drop=True)
        return reddit_df 
    
    def drop_duplicates(self, reddit_df):
        reddit_df.drop_duplicates(keep='first', inplace=True)
        reddit_df.reset_index(inplace=True, drop=True)
        return reddit_df

    def cleanse_text(self, text):
        if isinstance(text, float):
            return []
        
        text = text.lower()   # lower case
        text = re.sub(r"http\S*|\S*\.com\S*|\S*www\S*", " ", text)    # delete url 
        text = re.sub(r"\s@\S+", " ", text)   # delete @mentions
        text = re.sub(r"\s+", " ", text)   # replace all whitespace with a single space
        text = text.strip()    # strip off spaces on either end
        
        if len(text) < 6: 
            return ''
        return text
    
    def get_token_list(self, reddit_df, reddit_type):
        assert reddit_type in ['RS', 'RC', 'rs', 'rc']
        if reddit_type.lower() == 'rs':
            return [word_tokenize(context) for context in reddit_df.context.values.tolist()]
        else:   # 2016  -> comment -> body
            return [word_tokenize(context) for context in reddit_df.body.values.tolist()]
    
    def set_max_tok(self, reddit_df, reddit_type, max_len):
        assert reddit_type in ['RS', 'RC', 'rs', 'rc']
        tok_list = self.get_token_list(reddit_df, reddit_type)
        idx_list = [idx for idx in range(len(tok_list)) if len(tok_list[idx]) <= max_len]
        reddit_df = reddit_df.loc[idx_list]
        reddit_df.reset_index(inplace=True, drop=True)
        return reddit_df

    def map_rc_rs(self, reddit_rs, reddit_rc):
        '''
        submission이 존재하지 않는 comment 제거 후, reddit_rc 반환하는 함수 
        '''
        id_list = reddit_rs.id.unique().tolist()
        id_list = ['t3_' + id for id in id_list]
        reddit_rc = reddit_rc[reddit_rc.id.isin(id_list)]
        reddit_rc.reset_index(drop=True, inplace=True)
        return reddit_rc