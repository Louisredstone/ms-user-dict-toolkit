import os, sys

def add_path(path):
    if path not in sys.path:
        sys.path.insert(0, path)
        
add_path('.')

import pandas as pd
import argparse
from datetime import datetime

from lib.user_dict import UserDict
from lib.utils import hex_str

def parse_args():
    parser = argparse.ArgumentParser(description='MS User Dictionary Toolkit')
    parser.add_argument('--dat_file', default=None, required=False, help='Path to the DAT file')
    parser.add_argument('--output_file', default=None, required=False, help='Path to the output file')
    return parser.parse_args()

def main():
    args = parse_args()
    df = pd.read_csv('char.csv')
    df_pair = pd.read_csv('char-pair.csv')
    if args.dat_file is None:
        input_user_dict = None
    else:
        input_user_dict = UserDict.from_dat_file(args.dat_file)        
    if args.output_file is None:
        output_file = 'user_dict.dat'
    else:
        output_file = args.output_file
    user_dict = UserDict()
    user_dict.utctimestamp = int(datetime.now().timestamp())
    if input_user_dict:
        for item in input_user_dict.items():
            if item['pinyin'].startswith('i'): continue # we define i as the special character
            user_dict.add_item(item['pinyin'], item['phrase'], item['i_candidate'])
    for i, row in df.iterrows():
        char = row['符号']
        shorts = [short.strip('.').lower() for short in row['简称'].split('/')]
        for short in shorts:
            user_dict.add_item('i'+short, char, 1)
    for i, row in df_pair.iterrows():
        chars = row['符号']
        shorts = [short.strip('.').lower() for short in row['简称'].split('/')]
        for short in shorts:
            user_dict.add_item('i'+short, chars, 1)
            user_dict.add_item('i'+short, chars[0], 2)
            user_dict.add_item('i'+short, chars[1], 3)
            user_dict.add_item('il'+short, chars[0], 1)
            user_dict.add_item('ir'+short, chars[1], 1)
    user_dict.to_dat_file(output_file)

if __name__ == '__main__':
    main()