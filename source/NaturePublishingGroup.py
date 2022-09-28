# https://www.NaturePublishingGroup.com/articles/s41586-021-03392-8
from selenium import webdriver

from selenium.webdriver.support.ui import WebDriverWait   #显示等待针对元素操作
#EC预期条件类（里面主要有一些判断元素是否出现，弹出框是否出现，以及是否出现新窗口等。）
#EC用的比较多的就是和显示等待一起使用，通过显示等待的方法来循环判断是否元素是否出现
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By#用于元素定位
import time
import re
from bs4 import BeautifulSoup

class NaturePublishingGroup(object):
	"""docstring for NaturePublishingGroup"""
	def __init__(self,url,driver):
		self.url = url
		self.driver = driver
		# self.driver.implicitly_wait(20)#设置隐式等待，等待时间5秒,隐式等待全局生效
		self.text = ''
		print('input')
	def get_text(self):
		try:
			self.driver.get(self.url)
			fulltext = WebDriverWait(self.driver,20,0.5).until(EC.presence_of_element_located((By.CLASS_NAME,'c-article-body')))
			html = re.sub(r'<table>.*?</table>','',fulltext.get_attribute("innerHTML"),re.S)
			articleSoup = BeautifulSoup(html,'html.parser')
			for child in articleSoup.children:
				if child.name != 'section':
					continue
				if child.attrs.get('data-title') == None:
					continue
				data_title = child.attrs.get('data-title')
				if 'Acknowledgements' == data_title or 'Author information' == data_title or \
					'Ethics declarations' == data_title or 'Additional information' == data_title or \
					'Rights and permissions' == data_title or 'About this article' == data_title or 'Comments' == data_title:
					continue
				try:
					self.text += child.h2.get_text() + '\n' # 可能没有h2
				except:
					pass
				ps = child.find_all('p')
				for p in ps:
					if p.get_text().strip() == '':
						continue
					self.text += p.get_text().strip() + '\n'
		except Exception as e:
			print(e)
			pass
		# print(self.text)
		return self.text

# driver = webdriver.Chrome()
# try:
# 	NaturePublishingGroup("https://www.NaturePublishingGroup.com/articles/s41586-021-03392-8",driver)
# except Exception as e:
# 	print(e)
# finally:
# 	driver.close()
# 	driver.quit()
