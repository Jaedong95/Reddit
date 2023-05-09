import os 
import pandas as pd
import argparse 
from src import RedditData, RedditProcessor

def main(args): 
    '''
    언어 감지 완료된 데이터를 입력받아 데이터세트를 다시 구축하는 코드 
    '''
    default_path = os.getcwd() 
    data_path = os.path.join(default_path, args.data_path)
    reddit_p = RedditProcessor(data_path)

    reddit = pd.read_csv(os.path.join(data_path, 'processed', 'dataset3_l_' + args.year + '.csv'))
    lan_id = reddit.id.unique().tolist() 
    en_df = pd.DataFrame(lan_id, columns=['id'])
    # en_df.to_csv(os.path.join(data_path, 'processed', 'en_' + args.year + '_id_list.csv'), index=False)
    document = pd.read_csv(os.path.join(data_path, 'processed', 'dataset1_' + args.year + '.csv'))
    print(len(document))
    origin_id = document.id.unique().tolist()
    
    lan_id2 = [id for id in lan_id if id in origin_id] 
    new_df = document[document.id.isin(lan_id2)]
    new_df.text = new_df.text.apply(reddit_p.cleanse_text)   # cleanse text
    print(len(new_df))
    new_df.to_csv(os.path.join(data_path, 'processed', 'document_' + args.year + '.csv'))

if __name__ == '__main__':
    cli_parser = argparse.ArgumentParser()
    cli_parser.add_argument("--data_path", type=str, default='data', help='path that have train, val data')
    cli_parser.add_argument("--year", type=str, help='ex: 2010')
    cli_parser.add_argument("--subreddit", type=str, help='subreddit name')
    
    cli_argse = cli_parser.parse_args()
    main(cli_argse)