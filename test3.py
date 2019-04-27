
import os
import sys
import urllib.request
import json
import xlsxwriter
import pandas as pd
from bs4 import BeautifulSoup
'''
$ tail -n 1 $HOME/.bash_profile
export PATH="$HOME/miniconda3/bin:$PATH"
$ source $HOME/.bash_profile

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
def news(query, start=1,display=100,sort='date'):
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
		print(response_body.decode('utf-8'))
		return response_body
	else:
		print("Error Code:" + rescode)
		return 0

def remove_html_tag(string):
	a = BeautifulSoup(string, 'html.parser')
	return a.get_text()


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
			title.append(remove_html_tag(items['title']))
			link.append(items['link'])
			originallink.append(items['originallink'])
			description.append(remove_html_tag(items['description']))
			pubDate.append(items['pubDate'])
			if items['originallink'].find('news.chosun.com') >= 0:
				company.append('조선일보')
			elif items['originallink'].find('edaily.co.kr') >= 0:
				company.append('이데일리')
			elif items['originallink'].find('hankyung.com') >= 0:
				company.append('한경')
			else:
				company.append(' ')
			
			
	d = {'Title' : title,'Company':company,'pubDate':pubDate,'Description':description,'Link':link,'OriginalLink':originallink}
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