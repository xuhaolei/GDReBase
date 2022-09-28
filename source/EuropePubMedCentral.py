# http://europepmc.org/abstract/MED/32645325
from selenium import webdriver

from selenium.webdriver.support.ui import WebDriverWait   #显示等待针对元素操作
#EC预期条件类（里面主要有一些判断元素是否出现，弹出框是否出现，以及是否出现新窗口等。）
#EC用的比较多的就是和显示等待一起使用，通过显示等待的方法来循环判断是否元素是否出现
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By#用于元素定位
import time
import re
from bs4 import BeautifulSoup

class EuropePubMedCentral(object):
	"""docstring for EuropePubMedCentral"""
	def __init__(self,url,driver):
		self.url = url
		self.driver = driver
		# self.driver.implicitly_wait(20)#设置隐式等待，等待时间5秒,隐式等待全局生效
		self.text = ''
	def get_text(self):
		try:
			self.driver.get(self.url)
			fulltext = WebDriverWait(self.driver,20,0.5).until(EC.presence_of_element_located((By.ID,'free-full-text')))
			time.sleep(5)
			fulltext.click()
			element=WebDriverWait(self.driver,20,0.5).until(EC.presence_of_element_located((By.ID,'fulltextcontent')))
			html = re.sub(r'<table>.*?</table>','',element.get_attribute("outerHTML"),re.S)
			articleSoup = BeautifulSoup(html,'html.parser').find('div',attrs={'class':'jig-ncbiinpagenav'})
			ps = articleSoup.find_all('p')
			for p in ps:
				self.text += p.get_text().strip()+'\n'
			# for child in articleSoup.children:
			# 	if child.attrs.get('id') == None:
			# 		continue
			# 	if 'sec' not in child.attrs.get('id') and 'abs' not in child.attrs.get('id'):
			# 		continue
			# 	try:
			# 		self.text += child.h2.get_text() + '\n' # 可能没有h2
			# 	except:
			# 		pass
			# 	ps = child.find_all('p')
			# 	for p in ps:
			# 		if p.get_text().strip() == '':
			# 			continue
			# 		self.text += p.get_text().strip() + '\n'
		except Exception as e:
			print(e)
			pass
		return self.text

# driver = webdriver.Chrome()
# try:
# 	print(EuropePubMedCentral("http://europepmc.org/article/MED/33526751",driver).get_text())
# except Exception as e:
# 	print(e)
# finally:
# 	driver.close()
# 	driver.quit()
