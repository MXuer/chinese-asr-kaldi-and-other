- [chinese-asr-kaldi-and-other](#chinese-asr-kaldi-and-other)
- [features to test](#features-to-test)
- [Reference Blogs](#reference-blogs)
- [About datasets](#about-datasets)
- [about detecting language](#about-detecting-language)

# chinese-asr-kaldi-and-other

From now, first build a model by kaldi for chinese from commonvoice, then use keras to build end2end model, keep updating

# features to test

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
5. Another problem occured during the preprocessing data, it is a chinese words, "別怕", I don't know what's the difference between "別怕" and "别怕", we can see the part of "别" is different. But I am still confused... I listened to the wav, it's "bie2 pa4", so I changed "別怕" to "别怕". The according audio file is `common_voice_zh-CN_18597886.wav`, the text is `别怕就只是个超人`。

# about detecting language

From the blog [用Python进行语言检测](https://zhuanlan.zhihu.com/p/84625185), we know that:

|  Language | RE                               |
|   :----:  | :----:                           |
| English   | u"[a-zA-Z]"                      |
| Chinese   | u"[\u4e00-\u9fa5]+"              |
| Korea     | u"[\uac00-\ud7ff]+"              |
| Japanese  | u"[\u30a0-\u30ff\u3040-\u309f]+" |
