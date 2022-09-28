from googletrans import Translator
import openpyxl
# pip install googletrans==4.0.0rc1  亲测有效
# 实例化
translator = Translator(service_urls=['translate.google.cn'])
workbook = openpyxl.load_workbook('test92.xlsx')
corpus = workbook['sheet1']
data_corpus = corpus['A1':'A14149']
for cnt in range(len(data_corpus)):
    print(cnt)
    if data_corpus[cnt][0].value is not None:
        transed_content = translator.translate(data_corpus[cnt][0].value, dest='zh-CN').text
        corpus['B' + str(cnt + 1)] = transed_content
        workbook.save('test93.xlsx')

