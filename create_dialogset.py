import pandas as pd 
import os 
import argparse 
from src import RedditData, RedditProcessor

def get_conv(df, o_id):
    author = []; text = []; s_time = []; order = []; o_id_list = []; p_id_list = []
    o_val = 0
    if sum(df.parent_id == 't1_' + o_id) == 0:   # 해당 댓글에 대댓글이 없는 경우 
        return None 
    
    idx = df[df.o_id == o_id].index.values[0]
    
    # o_id가 해당 값에 해당하는 데이터 추가  (댓글)
    author.append(df.loc[idx].author)
    text.append(df.loc[idx].text)  
    s_time.append(df.loc[idx].time) 
    o_id_list.append(df.loc[idx].o_id)
    p_id_list.append(df.loc[idx].parent_id)
    order.append(o_val)

    flag = True  
    o_val += 1 
    while flag:   # 대댓글이 더이상 존재하지 않을 때 까지 
        try: 
            idx = df[df.parent_id == 't1_' + df.loc[idx].o_id].index.values[0]
        except: 
            flag = False 
            continue 

        author.append(df.loc[idx].author)
        text.append(df.loc[idx].text)  
        s_time.append(df.loc[idx].time) 
        o_id_list.append(df.loc[idx].o_id)
        p_id_list.append(df.loc[idx].parent_id) 

    conv = pd.DataFrame(zip(author, text, s_time, o_id_list, p_id_list), columns=['author', 'text', 'time', 'o_id', 'parent_id'])
    return conv 

def main(args):
    default_path = os.getcwd()
    data_path = os.path.join(default_path, args.data_path)
    save_path = os.path.join(data_path, 'processed')

    reddit = RedditData(args.subreddit, data_path)
    reddit_p = RedditProcessor(args.data_path)

    # reddit_df = reddit.load_df(os.path.join(save_path, 'aud_doc.csv'))
    reddit_df = reddit.load_df(os.path.join(save_path, f'dataset1_{args.year}.csv'))
    # title_id_list = reddit_df[reddit_df.type=='title'].id.unique().tolist()
    # title_id_list = ['t3_' + ]
    # print(title_id_list[:2])

    reddit_df = reddit_p.drop_na(reddit_df)    # 결측값 제거
    reddit_df = reddit_df[reddit_df.author!='[deleted]']   # 작성자 정보가 없는 데이터 제거 
    reddit_comment = reddit_df[reddit_df.type=='comment']    # comment만 추출 
    comment_id_list = reddit_comment.id.unique().tolist()   # 게시글 id 정보 저장 
    
    # create dialog dataset 
    dialog = dict() 
    dict_id = 0 
    for idx in range(len(comment_id_list)):
        comment_df = reddit_comment[reddit_comment.id == comment_id_list[idx]]   # 각 게시글에 달린 댓글과 대댓글만 추출 
        comment_df.reset_index(inplace=True, drop=True)

        if sum(comment_df.parent_id.str.startswith('t3')) > 0 and sum(comment_df.parent_id.str.contains('t1_')) != 0:   # 댓글과 대댓글이 있는 대화만 추출
            dialog[dict_id] = comment_df 
            dict_id += 1 

    # mapping dialog
    oto = dict()   # one to one
    mtm = dict()   # many to many 
    o_idx = 0  
    m_idx = 0 

    for idx in range(len(dialog)):
        '''
        1. parent_id가 t3_으로 시작하는 o_id 리스트업 
        2. o_id를 반복하며, o_id와 이어지는 데이터 추출 
          * o_id에 이어지는 발화가 없으면 해당 o_id는 사용 못하는 데이터 
        3. 각 o_id에 해당하는 대화의 작성자 수 파악  -> 2: oto, 2 이상: mtm mapping 
        '''
        o_id = dialog[idx][dialog[idx].parent_id.str.startswith('t3')].o_id.unique().tolist()
        for id in o_id: 
            conv = get_conv(dialog[idx], id)
            if conv is None:   # 대댓글이 없는 댓글일 경우 
                continue 
            if len(conv.author.unique()) == 2: 
                oto[o_idx] = conv 
                o_idx += 1 
            elif len(conv.author.unique()) > 2: 
                mtm[m_idx] = conv 
                m_idx += 1 

    o_df = pd.DataFrame([[0, 0, 0, 0, 0, 0]], columns=['author', 'text', 'time', 'parent_id', 'o_id', 'dialog_id'])
    d_idx = 1
    for _ , value in oto.items():
        value['dialog_id'] = 'dialog_' + str(d_idx)
        o_df = pd.concat([o_df, value])
        d_idx += 1 

    m_df = pd.DataFrame([[0, 0, 0, 0, 0, 0]], columns=['author', 'text', 'time', 'parent_id', 'o_id', 'dialog_id'])
    d_idx = 1 
    for _ , value in mtm.items():
        value['dialog_id'] = 'dialog_' + str(d_idx)
        m_df = pd.concat([m_df, value])
        d_idx += 1 

    o_df.reset_index(inplace=True, drop=True)
    o_df.drop([0], axis=0, inplace=True)
    o_df.reset_index(inplace=True, drop=True)
    m_df.reset_index(inplace=True, drop=True)
    m_df.drop([0], axis=0, inplace=True)
    m_df.reset_index(inplace=True, drop=True)
    
    o_df = o_df[['dialog_id', 'author', 'text', 'time', 'parent_id', 'o_id']]
    m_df = m_df[['dialog_id', 'author', 'text', 'time', 'parent_id', 'o_id']]
    print(m_df.head(10))
    o_df.to_csv(os.path.join(data_path, 'processed', f'one_to_one_{args.year}.csv'), index=False) 
    m_df.to_csv(os.path.join(data_path, 'processed', f'many_to_many_{args.year}.csv'), index=False)

if __name__ == '__main__':
    cli_parser = argparse.ArgumentParser()
    cli_parser.add_argument("--data_path", type=str, default='data', help='path that have train, val data')
    cli_parser.add_argument("--year", type=str)
    cli_parser.add_argument("--subreddit", type=str, help='subreddit name')
    
    cli_argse = cli_parser.parse_args()
    main(cli_argse)