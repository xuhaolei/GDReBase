#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/8/5 22:40
# @Author  : XuHaolei
# @File    : predict.py
import torch
from model.BERT_BiLSTM_CRF import BERT_BiLSTM_CRF
from scripts.config import Config
from scripts.utils import load_vocab
import transformers
from itertools import combinations
from itertools import product
import pandas as pd
import numpy as np
# import xlsxwriter


'''用于识别输入的句子（可以换成批量输入）的命名实体
    <pad>   0
    B-Disease   1
    I-Disease   2
    O       3
    <START> 4
    <EOS>   5
'''
tags = [(1, 2)]

config = Config()
vocab = load_vocab(config.vocab)
label_dic = load_vocab(config.label_file)
tagset_size = len(label_dic)
device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
model = BERT_BiLSTM_CRF(tagset_size,
                        config.bert_embedding,
                        config.rnn_hidden,
                        config.rnn_layer,
                        0,
                        config.pretrain_model_name,
                        device).to(device)
# , map_location=torch.device('cpu')
checkpoint = torch.load(config.checkpoint, map_location=torch.device('cpu'))
model.load_state_dict(checkpoint["model"])
print("模型加载完成")

dictionary = []
with open("bacteria/new_dict.txt", 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for line in lines:
        dictionary.append(line.strip('\n'))
print("细菌字典加载完成")


def judge_long_token(word):
    flag = False
    for dict0 in dictionary:
        if word in dict0:
            flag = True
            break
    return flag

# 菌群匹配
def find_bac(token):
    i = 0
    pos = []
    while i < len(token):
        if token[i] in dictionary:
            start, end = i, i
            if i + 1 < len(token):
                i += 1
                new_word = token[i - 1] + ' ' + token[i]
                while new_word in dictionary:
                    end = i
                    if i + 1 < len(token):
                        i += 1
                        new_word = new_word + ' ' + token[i]
            pos.append((start, end + 1))
            i = end
        elif judge_long_token(token[i]):
            if i + 5 < len(token) and token[i] + ' ' + token[i+1] + ' ' + token[i+2] + ' ' + token[i+3] + ' ' + token[i+4] in dictionary:
                pos.append((i, i + 5))
                i = i + 4
            elif i + 4 < len(token) and token[i] + ' ' + token[i+1] + ' ' + token[i+2] + ' ' + token[i+3] in dictionary:
                pos.append((i, i + 4))
                i = i + 3
            elif i + 3 < len(token) and token[i] + ' ' + token[i+1] + ' ' + token[i+2] in dictionary:
                pos.append((i, i + 3))
                i = i + 2
            elif i + 2 < len(token) and token[i] + ' ' + token[i+1] in dictionary:
                pos.append((i, i + 2))
                i = i + 1
        i += 1
    return pos


def predict(input_seq, max_length=180):
    '''
    :param input_seq: 输入一句话
    :return:
    '''
    # 构造输入
    input_list = []
    for i in range(len(input_seq)):
        input_list.append(input_seq[i])

    if len(input_list) > max_length - 2:
        input_list = input_list[0:(max_length - 2)]
    input_list = ['[CLS]'] + input_list + ['[SEP]']

    input_ids = [int(vocab[word]) if word in vocab else int(vocab['[UNK]']) for word in input_list]
    input_mask = [1] * len(input_ids)

    if len(input_ids) < max_length:
        input_ids.extend([0] * (max_length - len(input_ids)))
        input_mask.extend([0] * (max_length - len(input_mask)))
    assert len(input_ids) == max_length
    assert len(input_mask) == max_length

    # 变为tensor并放到GPU上, 二维, 这里mask在CRF中必须为unit8类型或者bool类型
    input_ids = torch.LongTensor([input_ids]).to(device)
    input_mask = torch.ByteTensor([input_mask]).to(device)

    feats = model(input_ids, input_mask)
    # out_path是一条预测路径（数字列表）, [1:-1]表示去掉一头一尾, <START>和<EOS>标志
    out_path = model.predict(feats, input_mask)[0][1:-1]
    res = find_all_tag(out_path)
    disease = []
    for name in res:
        if name == 1:
            for i in res[name]:
                disease.append(input_seq[i[0]:(i[0] + i[1])])

    return res


def find_tag(out_path, B_label_id=1, I_label_id=2):
    '''
    找到指定的label
    :param out_path: 模型预测输出的路径 shape = [1, rel_seq_len]
    :param B_label_id:
    :param I_label_id:
    :return:
    '''
    global start_pos
    sentence_tag = []
    for num in range(len(out_path)):
        if out_path[num] == B_label_id:
            start_pos = num
        if out_path[num] == I_label_id and out_path[num - 1] == B_label_id:
            length = 2
            for num2 in range(num, len(out_path)):
                if out_path[num2] == I_label_id and out_path[num2 - 1] == I_label_id:
                    length += 1
                    if num2 == len(out_path) - 1:  # 如果已经到达了句子末尾
                        sentence_tag.append((start_pos, length))
                        return sentence_tag
                if out_path[num2] == 3:
                    sentence_tag.append((start_pos, length))
                    break
    return sentence_tag


def find_all_tag(out_path):
    num = 1
    result = {}
    for tag in tags:
        res = find_tag(out_path, B_label_id=tag[0], I_label_id=tag[1])
        result[num] = res
        num += 1
    return result


def find_disease(input_seq):
    text = input_seq.split(' ')
    new_text = []
    for cnt, word in enumerate(text):
        word_piece = tokenizer.tokenize(word)
        new_text += word_piece
    token = []
    cnt = 0
    while cnt < len(new_text):
        if new_text[cnt][0:2] != '##':
            token.append(new_text[cnt])
        else:
            token[-1] += new_text[cnt][2:]
        cnt += 1
    if len(token) > 0 and token[-1] != '.':
        token.append('.')
    pos = []
    start = 0
    last_len = 0
    for cnt, word in enumerate(token):
        word_piece = tokenizer.tokenize(word)
        if cnt == 0:
            start = 0
            last_len = len(word_piece)
        else:
            start = start + last_len
            last_len = len(word_piece)
        pos.append((start, len(word_piece)))
    res = predict(new_text)
    # 根据pos和res找预测结果在token中的位置
    result = []
    for name in res:
        if name == 1:
            for i in res[name]:
                # 实体开始i[0],下一个实体开始i[0]+i[1]
                begin, end, flag, start = 0, 0, False, False
                for cnt, item in enumerate(pos):
                    if item[0] == i[0]:
                        begin = cnt
                        start = True
                    if item[0] == i[0] + i[1]:
                        end = cnt
                        flag = True
                if start and flag:
                    result.append((begin, end))
    return token, result


def judge(p):
    for p0 in p:
        if max(p0[0][0], p0[1][0]) <= min(p0[0][1], p0[1][1]) - 1:
            print("有交集")
            if p0[0][0] == p0[1][0] and p0[0][1] == p0[1][1]:
                print("相同")
                if p0[0] in disease_pos:
                    disease_pos.remove(p0[0])
                    continue
            if p0[1][0] >= p0[0][0] and p0[1][1] <= p0[0][1]:
                print("包含")
                if p0[1] in bacteria_pos:
                    bacteria_pos.remove(p0[1])
            elif p0[1][0] <= p0[0][0] and p0[1][1] >= p0[0][1]:
                print("包含")
                if p0[0] in disease_pos:
                    disease_pos.remove(p0[0])
            else:
                print("相交")
                if p0[0] in disease_pos:
                    disease_pos.remove(p0[0])
                if p0[1] in bacteria_pos:
                    bacteria_pos.remove(p0[1])


if __name__ == "__main__":
    tokenizer = transformers.BertTokenizer.from_pretrained("../dataset/bert/alvaroalon2biobert_diseases_ner")
    with open("relation_corpus.txt", 'w', encoding='utf-8') as f:
        f.write("paper_id" + '\t' + 'evidence' + '\t' + 'json_train' + '\t' + "disease" + '\t' + 'bacteria' + '\n')
    data = pd.DataFrame(pd.read_excel('tb_papers.xlsx', 'tb_papers(1)', header=None)).loc[0:, 5:5]
    data = np.array(data).tolist()
    for cnt, data0 in enumerate(data):
        paper_id = cnt + 1
        paper_abstract = data0[0]
        if type(paper_abstract) != str:
            continue
        seq = paper_abstract.split('.')
        print(cnt)
        for input_seq in seq:
            token, disease_pos = find_disease(input_seq)
            bacteria_pos = find_bac(token)
            # 去重
            p = product(disease_pos, bacteria_pos)
            judge(p)
            if len(disease_pos) >= 1 and len(bacteria_pos) >= 1:
                p = product(disease_pos, bacteria_pos)
                with open('relation_corpus.txt', 'a', encoding='utf-8') as f2:
                    for e in p:
                        print(e)
                        evidence = ' '.join(token)
                        f2.write(str(paper_id) + '\t' + evidence + '\t' + "{'token': " + str(
                            token) + ", 'relation': 'Entity-Destination(e1,e2)', 'h': {'pos': [" + str(
                            e[0][0]) + ', ' + str(e[0][1]) + "]}, 't': {'pos': [" + str(e[1][0]) + ', ' + str(
                            e[1][1]) + "]}}" + '\t' + ' '.join(token[e[0][0]: e[0][1]]) + '\t' + ' '.join(token[e[1][0]: e[1][1]]) + '\n')
