
import os
import sys
from urllib.request import urlopen
import json
import xlsxwriter
import pandas as pd
from bs4 import BeautifulSoup
import csv
import requests
import urllib.request
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
'''
$ tail -n 1 $HOME/.bash_profile
export PATH="$HOME/miniconda3/bin:$PATH"
$ source $HOME/.bash_profile
#
#chrome version 74.0.3729.131(64비트)
# chrome driver version 74.0.3729.6
# 
#
#
#
#1 base
#2 news_venv
#
# To activate this environment, use:
# > conda activate news_venv
#
# To deactivate an active environment, use:
# > conda deactivate
#
#python3 test3.py


'''

def remove_space(my_content):
	result = ""
	for i in my_content.splitlines():
		if i.strip() == "":
			pass
		else:
			x = " ".join(i.split())
			result += x
			result += "\n"
	return result


def news(query, start=1,display=50,sort='date'):
	client_id = "9wcMaQNSaihKmYkZwR0d"
	client_secret = "O5XwiLjhif"
	if sort not in ['sim','date']:
		print("error not sort")

	url = 'https://openapi.naver.com/v1/search/news.json?query={0}&display={1}&start={2}&sort={3}'.format(urllib.parse.quote(query), display, start, sort)
	request = urllib.request.Request(url)
	request.add_header("X-Naver-Client-Id",client_id)
	request.add_header("X-Naver-Client-Secret",client_secret)
	response = urllib.request.urlopen(request)
	rescode = response.getcode()
	if(rescode==200):
		response_body = response.read()
		return response_body
	else:
		print("Error Code:" + rescode)
		return 0

def remove_html_tag(string):
	a = BeautifulSoup(string, 'html.parser')
	return a.get_text()


def run_csv(keyword):
	with open("naver_news_%s.csv" % keyword, 'w' , encoding='utf-8') as csvoutput:
		csv_writer = csv.writer(csvoutput)
		for start_i in range(1, 4):
			tmp = news(keyword, start_i)
			json_res = json.loads(tmp, encoding='utf-8')
			for items in json_res['items']:
				ra = []
				ra.append(remove_html_tag(items['title']))
				ra.append(items['link'])
				ra.append(items['originallink'])
				ra.append(remove_html_tag(items['description']))
				ra.append(items['pubDate'])
				csv_writer.writerow(ra)


DRIVER = None
def get_description(url):
	global DRIVER
	if DRIVER == None:
		DRIVER = webdriver.Chrome(executable_path='./chromedriver')	


	DRIVER.get(url)
	time.sleep(2)
	html = DRIVER.page_source
	current_url = DRIVER.current_url
	bs = BeautifulSoup(html, "html.parser")
	
	
	if current_url.find("entertain.naver.com") >= 0:
		find_id = "articeBody"
	elif current_url.find("news.naver.com") >= 0:
		find_id = "articleBodyContents"
	elif current_url.find("topstarnews.net") >=0:
		find_id = "adnmore_inImage"
	else:
		find_id = "none"
	#ententain용 contents2=soup.find_all("div", {"id":"articeBody"})for item in main_result:
	main_result = bs.find(id=find_id)

	if main_result != None:
		for script in main_result.find_all('script'):
			script.decompose()
		content = main_result.get_text("\n")
		content = remove_space(content)
		
	
	return content



def run_search(keyword):
	writer = pd.ExcelWriter('naver_news_%s.xlsx' % keyword, engine='xlsxwriter')
	#for문으로 페이지별 추가 가능
	title= []
	link= []
	originallink= []
	description= []
	pubDate= []
	company=[]
	for start_i in range(1,4):#1~3시작위치
		tmp = news(keyword,start_i)
		json_res = json.loads(tmp,encoding='utf-8')

		for items in json_res['items']:	
			#print("\n*******************************************\n")
			#print(items)
			title.append(remove_html_tag(items['title']))
			link.append(items['link'])
			originallink.append(items['originallink'])
			#description.append(remove_html_tag(items['description']))
			
			pubDate.append(items['pubDate'])
			if items["link"].find("news.naver.com") >= 0:
				description.append(get_description(items["link"]))
			else:
				description.append('')
				pass

			
	d = {'Title' : title,'pubDate':pubDate,'Description':description,'Link':link,'OriginalLink':originallink}
	df = pd.DataFrame(d)
	df.to_excel(writer,'Sheet1')
	writer.save()



'''
from apscheduler.schedulers.blocking import BlockingScheduler
def schedule(keyword):
	sched = BlockingScheduler()
	# 예약방식 interval로 설정, 1시간마다 한번 실행
	sched.add_job(run_search(keyword), 'interval', seconds=3600)
	sched.start()

'''
#schedule("버닝썬")



run_search("버닝썬")

