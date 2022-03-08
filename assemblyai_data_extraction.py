from transcribe import *
import time
import pandas as pd
import numpy as np
import sys
import requests
import json
from datetime import datetime
import string


def json_data_extraction(result,fname):

    audindex = pd.json_normalize(result['words'])
    audindex['fname'] = fname

    speakers = list(audindex.speaker)  # Change df to your dataframe name
    previous_speaker = 'A'
    l = len(speakers)
    i = 1
    speaker_seq_list = list()
    for index, new_speaker in enumerate(speakers):
        if index > 0:
            previous_speaker = speakers[index - 1]
        if new_speaker != previous_speaker:
            i += 1
        speaker_seq_list.append(i)
        # print(str(previous_speaker)+"  "+str(new_speaker)+"  "+str(i))
    audindex['seq'] = speaker_seq_list
    df = pd.DataFrame(audindex.groupby(['fname', 'speaker', 'seq']).agg(utter=('text', ' '.join), stime=('start', 'min'),etime=('end', 'max')))
    df.reset_index(inplace=True)
    df.sort_values(by=['stime'], inplace=True)

    df['stime'] = df.stime // 1000
    df['etime'] = df.etime // 1000
    df['seq'] = df.seq - 1
    df.rename(columns = {'speaker':'spcode'},inplace=True)

    if(df.utter.str.contains('record')[0]):
        spcode = df.spcode[0]
        df['splabel'] = np.where((df.spcode == spcode),'moderator','respondent')
    else:
        spcode = df.spcode[0]
        df['splabel'] = np.where((df.spcode == spcode),'respondent','moderator')    
    
    hilites = pd.json_normalize(result['auto_highlights_result']['results'])
    hilites = hilites.text.unique()
    df['key_phrase'] = 'none'
    for x in hilites:
        df.loc[(df.utter.str.contains(x)), 'key_phrase'] = x
    # df.to_csv('tx_speaker_db.csv', mode='a', header=False, index=False)
    return df

def sentclass(x):
    if x >= 0.05:
        return "Positive"
    elif x <= - 0.05:
        return "Negative"
    else:
        return "Neutral"


def data_generation(df):
    df['wcount'] = df['utter'].apply(lambda x: len(x.split()))
    df.reset_index(inplace=True)
    df.drop('index', axis=1, inplace=True)
    df['emotion'] = df.utter.apply(lambda x: te.get_emotion(x))
    df['emotion'] = df.emotion.apply(lambda x: max(x, key=x.get))
    analyzer = SentimentIntensityAnalyzer()
    df['senti'] = [analyzer.polarity_scores(x)['compound'] for x in df['utter']]
    df['senti'] = [sentclass(x) for x in df['senti']]
    df['compound'] = [analyzer.polarity_scores(x)['compound'] for x in df['utter']]
    df['positive'] = [analyzer.polarity_scores(x)['pos'] for x in df['utter']]
    df['negative'] = [analyzer.polarity_scores(x)['neg'] for x in df['utter']]
    df['neutral'] = [analyzer.polarity_scores(x)['neu'] for x in df['utter']]
    # df.to_csv('tx_speaker_db.csv', mode='a', header=False, index=False)
    return df