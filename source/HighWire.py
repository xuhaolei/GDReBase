# HighWire
import time
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait   #显示等待针对元素操作
#EC预期条件类（里面主要有一些判断元素是否出现，弹出框是否出现，以及是否出现新窗口等。）
#EC用的比较多的就是和显示等待一起使用，通过显示等待的方法来循环判断是否元素是否出现
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By#用于元素定位
import requests
class HighWire(object):
	"""docstring for HighWire"""
	def __init__(self,url,driver=None):
		self.url = url
		self.driver = driver
		# self.driver.implicitly_wait(20)#设置隐式等待，等待时间5秒,隐式等待全局生效
		self.text = ''
		self.headers = {
    		"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36"
		}
	def get_text(self):
		try:
			html = requests.get(self.url,headers = self.headers).text
			html = re.sub(r'<a .*?>.*?</a>','',html,flags = re.S)
			# fulltext = WebDriverWait(self.driver,20,0.5).until(EC.presence_of_element_located((By.ID,'artText')))
			html = re.sub(r'<table.*?>.*?</table>','',html,flags = re.S)
			# time.sleep(3)
			articleSoup = BeautifulSoup(html,'html.parser').find('article')
			# print(articleSoup)
			if articleSoup == None:
				articleSoup = BeautifulSoup(html,'html.parser').find('div',attrs={'class':'article'})
				if articleSoup == None:
					raise Exception # 找不到元素
			ps = articleSoup.find_all('p')
			for p in ps:
				self.text += p.get_text() +'\n'
			# print(self.text)
		except Exception as e:
			print(e)
			pass
		# print(self.text)
		return self.text

# https://dx.plos.org/10.1371/journal.pone.0250081
# https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0250081
# driver = webdriver.Chrome()
# try:
# 	print(HighWire("https://bjgp.org/cgi/pmidlookup?view=long&pmid=33753347").get_text())
# except Exception as e:
# 	print(e)
# finally:
# 	# driver.close()
# 	# driver.quit()
# 	pass
