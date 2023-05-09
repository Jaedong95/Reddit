import pandas as pd 
import os 
import argparse
from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline
from src import RedditData


def main(args):
    default_path = os.getcwd()
    data_path = os.path.join(default_path, args.data_path)
    save_path = os.path.join(args.data_path, 'processed')
    reddit = RedditData(args.subreddit, data_path)

    # reddit_df = reddit.load_df(os.path.join(save_path, 'dataset2_' + args.year + '.csv'))
    reddit_df = reddit.load_df(os.path.join(save_path, 'aud_dsm.csv'))

    tokenizer = AutoTokenizer.from_pretrained("dslim/bert-base-NER")
    model = AutoModelForTokenClassification.from_pretrained("dslim/bert-base-NER")
    nlp = pipeline("ner", model=model, tokenizer=tokenizer)
    
    idx_list = []
    ner_result = []

    for idx in range(len(reddit_df)):
        ner = nlp(reddit_df.text[idx])
        if ner != []: 
            for ne in ner:
                if ne['entity'] in ['B-PER', 'I-PER']:
                    idx_list.append(idx)
                    ner_result.append(ner)

    idx_list = list(set(idx_list))
    print(f'length of data before removing personal info: {len(reddit_df)}')
    reddit_df.drop(idx_list, inplace=True)
    reddit_df.reset_index(drop=True, inplace=True)
    print(f'length of data after removing personal info: {len(reddit_df)}')
    # reddit.save_df(reddit_df, os.path.join(save_path, 'dataset3_' + args.year + '.csv'))
    reddit.save_df(reddit_df, os.path.join(save_path, 'aud_dsm_fin.csv'), index=False)

if __name__ == '__main__':
    cli_parser = argparse.ArgumentParser()
    cli_parser.add_argument("--data_path", type=str, default='data', help='path that have train, val data')
    cli_parser.add_argument("--subreddit", type=str, help='subreddit name')
    
    cli_argse = cli_parser.parse_args()
    main(cli_argse)