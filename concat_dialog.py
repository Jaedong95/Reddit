import pandas as pd 
import argparse 
import os 
from nltk.tokenize import word_tokenize 
from src import RedditData, RedditProcessor

def main(args):
    default_path = os.getcwd()
    data_path = os.path.join(default_path, args.data_path)
    reddit_year = list(range(2010, 2020))
    reddit_p = RedditProcessor(args.data_path)
    dialog_df = pd.DataFrame([[0, 0, 0, 0, 0, 0]], columns=['dialog_id', 'author', 'text', 'time', 'parent_id', 'o_id'])

    for year in reddit_year: 
        if args.dtype == 0:
            dialog_data = pd.read_csv(os.path.join(data_path, 'processed', f'one_to_one_{year}.csv'))
        elif args.dtype == 1: 
            dialog_data = pd.read_csv(os.path.join(data_path, 'processed', f'many_to_many_{year}.csv'))
        dialog_data.dialog_id = dialog_data.dialog_id.apply(lambda x: x + '_' + str(year))
        dialog_df = pd.concat([dialog_df, dialog_data]) 

    dialog_df.reset_index(inplace=True, drop=True) 
    dialog_df.drop([0], axis=0, inplace=True)
    dialog_df.reset_index(inplace=True, drop=True) 
    print(f'길이가 긴 대화 데이터 제거 전: {len(dialog_df.dialog_id.unique())}')
    tok_list = [word_tokenize(context) for context in dialog_df.text.values.tolist()]
    dialog_df['tok_len'] = [len(tok) for tok in tok_list]

    tok_q3 = dialog_df['tok_len'].quantile(0.75) 
    tok_q1 = dialog_df['tok_len'].quantile(0.25) 
    tok_iqr = tok_q3 - tok_q1 
    
    print(tok_q3 + 1.5 * tok_iqr, tok_q1 - 1.5 * tok_iqr)   # tok: 42 (이상치), tok 평균 길이가 42보다 큰 텍스트 삭제 
    idx_list = [idx for idx in range(len(tok_list)) if len(tok_list[idx]) < int(tok_q3 + 1.5 * tok_iqr)]
    dialog_list = dialog_df.loc[idx_list].dialog_id.unique().tolist()
    dialog_df = dialog_df[dialog_df.dialog_id.isin(dialog_list)]
    print(f'길이가 긴 대화 데이터 제거 후: {len(dialog_df.dialog_id.unique())}')

    dialog_df.drop_duplicates('text', inplace=True)
    dialog_df.reset_index(inplace=True, drop=True)
    print(f'중복 처리 후: {len(dialog_df.dialog_id.unique())}')
    
    dialog_id_prev = dialog_df.dialog_id.unique().tolist()
    dialog_id_new = list(range(1, len(dialog_id_prev) + 1))
    dialog_id_new = ['dialog_' + str(id) for id in dialog_id_new]
    dialog_id_dict = dict(zip(dialog_id_prev, dialog_id_new))
    dialog_df.dialog_id = dialog_df.dialog_id.apply(lambda x: dialog_id_dict[x])
    
    if args.dtype == 0:
        dialog_df.to_csv(os.path.join(data_path, 'processed', 'one_to_one_dialog.csv'), index=False)
    elif args.dtype == 1: 
        dialog_df.to_csv(os.path.join(data_path, 'processed', 'many_to_many_dialog.csv'), index=False)

if __name__ == '__main__':
    cli_parser = argparse.ArgumentParser()
    cli_parser.add_argument("--data_path", type=str, default='data', help='path that have train, val data')
    cli_parser.add_argument("--subreddit", type=str, help='subreddit name')
    cli_parser.add_argument("--dtype", type=int, default=0, help='one_to_on: 0, many_to_many: 1')
    
    cli_argse = cli_parser.parse_args()
    main(cli_argse)