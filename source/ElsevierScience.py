# # https://linkinghub.elsevier.com/retrieve/pii/S0092-8674(20)31012-6
from selenium import webdriver

from selenium.webdriver.support.ui import WebDriverWait   #显示等待针对元素操作
#EC预期条件类（里面主要有一些判断元素是否出现，弹出框是否出现，以及是否出现新窗口等。）
#EC用的比较多的就是和显示等待一起使用，通过显示等待的方法来循环判断是否元素是否出现
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By#用于元素定位
import time
import re
from bs4 import BeautifulSoup

class ElsevierScience(object):
	"""docstring for ElsevierScience"""
	def __init__(self,url,driver):
		self.url = url
		self.driver = driver
		# self.driver.implicitly_wait(20)#设置隐式等待，等待时间5秒,隐式等待全局生效
		self.text = ''
	def get_text(self):
		try:
			self.driver.get(self.url)
			# element=WebDriverWait(self.driver,20,0.5).until(EC.presence_of_element_located((By.ID,'body')))
			time.sleep(5)
			html = re.sub(r'<table>.*?</table>','',element.get_attribute("outerHTML"),re.S)
			articleSoup = BeautifulSoup(element.get_attribute("outerHTML"),'html.parser')
			ps = articleSoup.find_all('p')
			for p in ps:
				self.text += p.get_text() + '\n'
		except:
			pass
		return self.text

# driver = webdriver.Chrome()
# try:
# 	ElsevierScience("https://linkinghub.elsevier.com/retrieve/pii/S0092-8674(20)30811-4",driver)
# except Exception as e:
# 	print(e)
# finally:
# 	driver.close()
# 	driver.quit()


# 下面这段代码是显示等待
# from selenium import webdriver
# from time import sleep
# from selenium.webdriver.support.ui import WebDriverWait   #显示等待针对元素操作
# #EC预期条件类（里面主要有一些判断元素是否出现，弹出框是否出现，以及是否出现新窗口等。）
# #EC用的比较多的就是和显示等待一起使用，通过显示等待的方法来循环判断是否元素是否出现
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.by import By#用于元素定位

# dr=webdriver.Chrome()
# dr.get("https://www.baidu.com/")
# dr.maximize_window()
# sleep(2)
# dr.find_element_by_css_selector('#kw').send_keys(u'测试')
# sleep(2)
# element=WebDriverWait(dr,5,0.5).until(EC.presence_of_element_located((By.ID,'su')))
# #显示等待，判断搜索按钮是否存在，每隔0.5秒刷新一次，5秒内没找到报异常
# element.click()
# sleep(2)
# dr.quit()