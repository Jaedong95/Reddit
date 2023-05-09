import pandas as pd 
import os 
import argparse 
from nltk.tokenize import word_tokenize 
from src import RedditData, RedditProcessor

def check_swear(text):
    text = text.lower()
    for word in swear_words: 
        if word.lower() in text:
            return True 
    return False 

def is_repeated(text):
    pass

def main(args):
    default_path = os.getcwd()
    data_path = os.path.join(default_path, args.data_path)
    save_path = os.path.join(data_path, 'processed')

    reddit = RedditData(args.subreddit, data_path)
    reddit_p = RedditProcessor(args.data_path)
    dialog = reddit.load_df(os.path.join(save_path, f'one_to_one_{args.year}.csv'))
    
    
    # 공격적 언어 포함하고 있는 대화 제거 
    global swear_words
    swear_words = ['cumbubble', 'fuck', 'f*ck', 'F*ck', 'Shitbag', 'Shit', 'Piss off', 'Asshole', 'Dickweed', 'Son of a bitch', 'Bastard', 'Bitch', 'Damn', 'Bollocks', 'Bitch', 'Damn', \
                   'Bollocks','Bugger', 'Cocknose', 'Bloody hell', 'Knobhead', 'Choad', 'Bitchtits' , 'Crikey', 'Rubbish', 'Pissflaps', 'Shag', 'Wanker', 'Talking the piss', 'Twat', \
                    'Arsebadger', 'Jizzcock', 'Cumdumpster', 'Wanker', 'Bollocks', 'Twatwaffle', 'Thundercunt', 'Dickhead', 'Shitpouch', 'Jizzstain', 'Nonce', 'Pisskidney', 'Wazzock',\
                    'Cumwipe', 'Fanny', 'Bellend', 'Pisswizard', 'Knobjockey', 'Cuntpuddle', 'Dickweasel', 'Quim', 'Bawbag', 'Fuckwit', 'Tosspot', 'Cockwomble', 'Twat face', 'Cack']
    
    print(f'공격적 언어 제거 전: {len(dialog)}')
    swear_list = dialog[dialog.text.apply(check_swear)].dialog_id.unique().tolist()
    dialog = dialog[~dialog.dialog_id.isin(swear_list)]
    dialog.reset_index(inplace=True, drop=True)
    print(f'공격적 언어 제거 후: {len(dialog)}')

    # 응답 토큰 길이가 이상치를 넘어가는 대화 제거 
    tok_list = [word_tokenize(context) for context in dialog.text.values.tolist()]
    dialog['tok_len'] = [len(tok) for tok in tok_list]
 
    tok_q3 = dialog['tok_len'].quantile(0.75) 
    tok_q1 = dialog['tok_len'].quantile(0.25) 
    tok_iqr = tok_q3 - tok_q1
    print(tok_q3 + 1.5 * tok_iqr, tok_q1 - 1.5 * tok_iqr)

    idx_list = [idx for idx in range(len(tok_list)) if len(tok_list[idx]) < int(tok_q3 + 1.5 * tok_iqr)]
    dialog_list = dialog.loc[idx_list].dialog_id.unique().tolist()

    dialog = dialog[dialog.dialog_id.isin(dialog_list)]
    dialog.reset_index(inplace=True, drop=True)
    print(f'길이가 긴 대화 데이터 제거 후: {len(dialog)}')

    # print(dialog.groupby('dialog_id').count().sort_values('author'))
    print(dialog[dialog.dialog_id=='dialog_5426'])
    dialog[dialog.dialog_id=='dialog_5426'].to_csv(os.path.join(data_path, 'turn_47.csv'), index=False)

if __name__ == '__main__':
    cli_parser = argparse.ArgumentParser()
    cli_parser.add_argument("--data_path", type=str, default='data', help='path that have train, val data')
    cli_parser.add_argument("--year", type=str, help='ex: 2010')
    cli_parser.add_argument("--subreddit", type=str, help='subreddit name')
    
    cli_argse = cli_parser.parse_args()
    main(cli_argse)