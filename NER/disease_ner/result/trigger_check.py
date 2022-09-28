from nltk import pos_tag
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
import nltk

trigger_dict = []
with open("../trigger/trigger_words.txt", 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for cnt, line in enumerate(lines):
        trigger_dict.append(line.strip('\n'))

wnl = WordNetLemmatizer()
x = 0
with open("relation_corpus99999.txt", 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for cnt, line in enumerate(lines):
        if cnt == 0: continue

        data = line.strip('\n').split("\t")[2]
        token = eval(data)['token']
        pos1 = eval(data)['h']['pos']
        pos2 = eval(data)['t']['pos']
        flag = False
        for i in range(min(pos1[1], pos2[1]), max(pos1[0], pos2[0])):
            if wnl.lemmatize(token[i], 'v') in trigger_dict:
                print(cnt, "yes")
                x += 1
                with open("筛选2.txt", 'a', encoding='utf-8') as f2:
                    f2.write('1\n')
                flag = True
                break
        if flag==False:
            with open("筛选2.txt", 'a', encoding='utf-8') as f2:
                f2.write('0\n')
print(x)


# wnl = WordNetLemmatizer()
#
# str1 = evidence[0]
# tokens = nltk.word_tokenize(str1)
# for i in range(0, len(tokens)):
#     wnl.lemmatize(tokens[i], 'v')
# attri = [nltk.pos_tag(tokens)[i][1] for i in range(0, len(nltk.pos_tag(tokens)))]

# # 获取单词的词性
# def get_wordnet_pos(tag):
#     if tag.startswith('J'):
#         return wordnet.ADJ
#     elif tag.startswith('V'):
#         return wordnet.VERB
#     elif tag.startswith('N'):
#         return wordnet.NOUN
#     elif tag.startswith('R'):
#         return wordnet.ADV
#     else:
#         return None
#
#
# # 分别定义需要进行还原的单词与相对应的词性
# words = ['he', 'loves', 'china']
# for i in range(len(words)):
#     print(words[i] + '--' + get_wordnet_pos(pos_tag([words[i]])[0][1]) + '-->' + wnl.lemmatize(words[i],
#                                                                                                get_wordnet_pos(
#                                                                                                    pos_tag([words[i]])[
#                                                                                                        0][1])))
