import os
import re
import sys
import shutil
import argparse
from collections import defaultdict

def main(args):
    if not os.path.exists(args.target_dir):
        os.mkdir(args.target_dir)
    source_dir = os.path.dirname(args.source_lex)
    shutil.copy(source_dir+"/pinyin_to_phone.txt", args.target_dir)
    cons = open(args.source_lex).readlines()
    all_characters = defaultdict(set)
    for c in cons:
        word = c.strip().split()[0]
        pronous = " ".join(c.strip().split()[1:])
        is_eng = re.findall('[0-9a-zA-Z]', word)
        if is_eng:
            continue
        pronous = pronous.split(';')
        for pronou in pronous:
            prs = pronou.split()
            for ch, pr in zip(word, prs):
                all_characters[ch].add(pr)
    
    target_word2_pin_file = os.path.join(args.target_dir, 'word_to_pinyin.txt')
    with open(target_word2_pin_file, 'w', encoding='utf-8') as f:
        for ch in all_characters.keys():
            sing_ch_pro = all_characters[ch]
            f.write(ch+"\t"+";".join(sing_ch_pro)+"\n")
        for c in cons:
            if c.split('\t')[0] in all_characters.keys():
                continue
            f.write(c)
    
                    
        
        


if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--source_lex', default='tools/BigCiDian/CN/word_to_pinyin.txt', type=str)
    parser.add_argument('--target_dir', default='tools/CiDian', type=str)
    args = parser.parse_args()
    main(args)