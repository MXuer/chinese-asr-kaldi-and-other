"""data.py: Processing data for training."""

__author__      = "Hu Du"
__copyright__   = "Copyright 2019, Planet Mar"

import os
import re
import sys
import sox
import csv
import jieba
import thulac
import random
import argparse
import json
import codecs
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

from glob import glob
from tqdm import tqdm
# from multiprocessing import Pool
from logbook import Logger, StreamHandler
from pathos.multiprocessing import ProcessPool as Pool

'''
There are 8 items for the chinese common voice datasets.
-------------------------------------------------------
client_id path sentence up_votes down_votes age gender accent
-------------------------------------------------------
in this version of data we won't foucs on gender and accent.
we show some data analysis for this dataset.
The initial distribution of train, dev and test is not that 
resonable for me, so I add a choice of if we want to redistribute
the data whose rate is decided by ourselves. I set it to 0.8, 0.1 and 0.1
'''

StreamHandler(sys.stdout).push_application()
log = Logger('*DataProcessing*')


punc = u'[\'，。！？（）《》【】‘’“”、·「」：；"・‧…『』?〈〉·,."?;:<>\[\]!\'－／-]'
illegal = u'[×̃̌ΛεμИТит—─□]'
use_th = False
if use_th:
    thu = thulac.thulac(seg_only=True)
trad_ch = {"妳":"你", "別":"别", "寀":"采", "専":"专", '崁': '坎',}

def text_normalization(text):
    for tr_c in trad_ch:
        if tr_c in text:
            text = text.replace(tr_c, trad_ch[tr_c])
    text = re.sub(punc, '', text)
    if use_th:
        text = thu.cut(text, text=True)
    else:
        text = list(jieba.cut(text))
        text = " ".join(text)
    text = re.sub(punc, '', text)
    return text
def mp3_to_wav(p1, p2):
    tfm = sox.Transformer()
    try:
        tfm.build(p1, p2)
    except Exception as e:
        log.error("Transforming {} to {} with Error {}".format(p1, p2, e))

def dataset_split(tsv_file, path, split_rate=[0.8, 0.1, 0.1]):
    FIELDNAMES=['path', 'sentence']
    all_data = []
    new_path = os.path.join(path, 'redistribute')
    if not os.path.exists(new_path):
        os.mkdir(new_path)
    new_train = os.path.join(new_path, 'train.tsv')
    new_dev = os.path.join(new_path, 'dev.tsv')
    new_test = os.path.join(new_path, 'test.tsv')
    if os.path.exists(new_train) and os.path.exists(new_dev) and os.path.exists(new_test):
        return new_path
    with open(tsv_file, 'r', encoding='utf-8') as f, \
        open(new_train, 'w', encoding='utf-8') as trainf, \
        open(new_dev, 'w', encoding='utf-8') as devf, \
        open(new_test, 'w', encoding='utf-8') as testf:
        reader = csv.DictReader(f, delimiter='\t')
        train_writer = csv.DictWriter(trainf, fieldnames=FIELDNAMES, delimiter='\t')
        dev_writer = csv.DictWriter(devf, fieldnames=FIELDNAMES, delimiter='\t')
        test_writer = csv.DictWriter(testf, fieldnames=FIELDNAMES, delimiter='\t')
        dict_per_sample = {}
        for c in reader:
            dict_per_sample['sentence'] = c['sentence']
            dict_per_sample['path'] = c['path']
            all_data.append(dict_per_sample)
            dict_per_sample = {}
        log.info('All number of sample is {}'.format(len(all_data)))
        num_testset = int(len(all_data)*split_rate[-1])
        test_samples = random.sample(all_data, num_testset)
        num_devset = int(len(all_data)*split_rate[1])
        log.info("Num of trainset: {}".format(len(all_data)-num_devset-num_testset))
        log.info("Num of devset: {}".format(num_devset))
        log.info("Num of testset: {}".format(num_testset))  
        test_writer.writeheader()
        for sample in test_samples:
            test_writer.writerow({'sentence':sample['sentence'], 'path':sample['path']})
            all_data.remove(sample)
        dev_samples = random.sample(all_data, num_devset)      
        dev_writer.writeheader()
        for sample in dev_samples:
            dev_writer.writerow({'sentence':sample['sentence'], 'path':sample['path']})
            all_data.remove(sample)
        train_writer.writeheader()
        for sample in all_data:
            train_writer.writerow({'sentence':sample['sentence'], 'path':sample['path']})
        return new_path

def each_tsv(path, clips_dir, target_dir):     
    log.info("Processing with ".format(path))   
    set_name = os.path.basename(path).split('.tsv')[0]
    targ_dir = os.path.join(target_dir, set_name)
    wav_path = os.path.join(target_dir, 'wav')
    if not os.path.exists(wav_path):
        os.makedirs(wav_path)
    if not os.path.exists(targ_dir):
        os.mkdir(targ_dir)
    wavfile = os.path.join(targ_dir, 'wav.scp')
    text = os.path.join(targ_dir, 'text')
    spk2utt = os.path.join(targ_dir, 'spk2utt')
    utt2spk = os.path.join(targ_dir, 'utt2spk')
    with open(path, 'r', encoding='utf-8') as pf, \
        open(text, 'w', encoding='utf-8') as textf, \
        open(wavfile, 'w', encoding='utf-8') as wavf, \
        open(spk2utt, 'w', encoding='utf-8') as spkf, \
        open(utt2spk, 'w', encoding='utf-8') as uttf:
        reader = csv.DictReader(pf, delimiter='\t')
        for i, c in enumerate(reader):
            sentence = c['sentence']
            check_ill = re.findall(u"[\u30a0-\u30ff\u3040-\u309f×̃̌ΛεμИТит—─□]+", sentence)
            mp3name = c['path']
            if check_ill:
                log.info("Utterance {}: {} with illegal characters {}".format(mp3name, sentence, check_ill))
                continue
            wavname = mp3name.replace('.mp3', '.wav')
            mp3_dir = os.path.join(clips_dir, mp3name)
            wav_dir = os.path.join(wav_path, wavname)
            if not os.path.exists(wav_dir):
                mp3_to_wav(mp3_dir, wav_dir)
            sentence = text_normalization(sentence)
            index = "%010d"%(i)+"-"+set_name[:3]
            textf.write(index+" "+sentence+"\n")
            wavf.write(index+" "+wav_dir+"\n")
            spk = index+"-"+"s0"
            spkf.write(spk+" "+index+"\n")
            uttf.write(index+" "+spk+"\n")

def main(args):
    log.info('----------start processing---------')
    clips_dir = os.path.join(args.source_dir, 'clips')
    if args.follow:
        datasets_file = glob(args.source_dir+'/*.tsv')
    else:
        validated_tsv = args.source_dir+'/validated.tsv'
        new_path = dataset_split(validated_tsv, args.source_dir)
        datasets_file = glob(new_path+'/*.tsv')
    if args.num_process==1:
        for tsv in tqdm(datasets_file):
            each_tsv(tsv, clips_dir, args.target_dir)
    else:
        targets = [args.target_dir]*len(datasets_file)
        clips_dirs = [clips_dir]*len(datasets_file)
        pool = Pool(args.num_process)
        pool.map(each_tsv, datasets_file, clips_dirs, targets)
        pool.close()
        pool.join()




if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--source_dir', default='/home/duhu/chinese-asr-kaldi-and-other/datasets/chinese')
    parser.add_argument('--target_dir', default='/home/duhu/chinese-asr-kaldi-and-other/datasets/chinese/dataset')
    parser.add_argument('--follow', default=False)
    parser.add_argument('--num_process', default=8, type=int)
    args = parser.parse_args()
    for para in args._get_kwargs():
        log.info("ParamsName:{} Value:{}".format(para[0], para[1]))
    main(args)