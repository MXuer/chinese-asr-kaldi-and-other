- [Chinese-asr-kaldi-and-other](#chinese-asr-kaldi-and-other)
- [Features to test](#features-to-test)
- [Reference Blogs](#reference-blogs)
- [About datasets](#about-datasets)
- [About detecting language](#about-detecting-language)
- [About Lexicon and text segmentation](#about-lexicon-and-text-segmentation)
- [About Tranditional2Simplyfy](#about-tranditional2simplyfy)
- [Steps of Kaldi](#steps-of-kaldi)

# Chinese-asr-kaldi-and-other

From now, first build a model by kaldi for chinese from commonvoice, then use keras to build end2end model, keep updating

# Features to test

- [specaugment](https://arxiv.org/abs/1904.08779)
- [label smoothing](https://arxiv.org/abs/1906.02629v2)
- [effecient attention](https://arxiv.org/pdf/1812.01243.pdf)

# Reference Blogs

- [Efficient Attention: Attention with Linear Complexities](https://cmsflash.github.io/ai/2019/12/02/efficient-attention.html)
- [When Does Label Smoothing Help?](https://medium.com/@nainaakash012/when-does-label-smoothing-help-89654ec75326)
- [Label Smoothing & Deep Learning: Google Brain explains why it works and when to use (SOTA tips)](https://medium.com/@lessw/label-smoothing-deep-learning-google-brain-explains-why-it-works-and-when-to-use-sota-tips-977733ef020)

# About datasets

1. Some utterances are `not correct`. I found them when I was preprocessing the data, so I deleted it both in `validated.tsv` and `train.csv`. Here is the list:
   - common_voice_zh-CN_18682400.mp3
     - 包应登，字稺升，浙江杭州府钱塘县人，**□籍**，明朝政治人物、进士出身。
     - 包应登，字稺升，浙江杭州府钱塘县人，**籍**，明朝政治人物、进士出身。
2. There are `japanese` in the dataset, I deleted them for I can't process them without lexicon.txt for kaldi, but for end2end ASR model, it does not matter. In addition, I don't think delete them will effect the model performance for there are only few samples with japanese mixed in. I will not show these utterance with Japanese.
3. Some mispronouciation existed in the `Greek Letters`, like `ε`, it's epsilon, but in a utterance, speakers says "ei", so it's deleted. Due to the probabel mistakes like this, I decide to delete all the Greek letters for I don't have time to check it.
4. There are both chinses and english punctuations, so we need to check that.
5. Another problem occured during the preprocessing data, it is a chinese words, "別怕", I don't know what's the difference between "別怕" and "别怕", we can see the part of "别" is different. But I am still confused... I listened to the wav, it's "bie2 pa4", so I changed "別怕" to "别怕". The according audio file is `common_voice_zh-CN_18597886.wav`, the text is `别怕就只是个超人`。Aha, the traditional format of "别" is "別".
6. Some characters does not hava a independent pronouciation while they have pronouciation in words. It's a little bit strange. So I write a program to extract all single characters' prounciation.Example: "忒", "不忒 BU_2 TE_4"
7. Another problem is that there's no corresponding pronouciation for traditional Chinese, 
   1. "妳" ---> "你"
   2. "寀" ---> "采"
   3. "別" ---> "别"

# About detecting language

From the blog [用Python进行语言检测](https://zhuanlan.zhihu.com/p/84625185), we know that:

|  Language | RE                               |
|   :----:  | :----:                           |
| English   | u"[a-zA-Z]"                      |
| Chinese   | u"[\u4e00-\u9fa5]+"              |
| Korea     | u"[\uac00-\ud7ff]+"              |
| Japanese  | u"[\u30a0-\u30ff\u3040-\u309f]+" |

# About Lexicon and text segmentation

- In this repository, we use [`BigCidian`](https://github.com/speech-io/BigCiDian.git) to get the lexicon.
- We use two kind of tools for text segment:
  - [`jieba`](https://github.com/fxsjy/jieba.git)
  - [`thulac`](http://thulac.thunlp.org/)

|  Tools    | Included   | Not Included |  ALL   |
|   :----:  | :----:     | :----:       | :----: |
| jieba     | 15131      |4908          | 20039  |
| thulac    | 12124      |6276          | 18400  |

# About Tranditional2Simplyfy

There are some libs for this kind of task, like:

- [zhconv](https://github.com/gumblex/zhconv.git)
- [hanziconv](https://github.com/berniey/hanziconv.git)

But there is a problem about these libs, for example, they can not transfer "寀" to "采". As to my guess, I think there is no this character in their library. So I follow the [`langconv.py`](https://raw.githubusercontent.com/skydark/nstools/master/zhtools/langconv.py) and [`zh_wiki.py`](https://raw.githubusercontent.com/skydark/nstools/master/zhtools/zh_wiki.py). We can add customized characters into the `zh_wiki.py`, so this seems better.

# Steps of Kaldi

1. Prepare dataset, lexicon and vocab.
   - download the [`BigCidian`](https://github.com/speech-io/BigCiDian.git)
        >git clone <https://github.com/speech-io/BigCiDian.git>
   - Fix some tiny problem with the `word_to_pinyin.txt`, run:
        >python tools/fix_lexicon.py
   - Generate the train, dev and test datasets
        >python data/data.py
   - Prepare the lexicon.txt and vocab.txt
        >python kaldi-script/local/ceate_lex_and_vocab.py