import requests
from urllib.parse import urlparse
from collections import defaultdict
from bs4 import BeautifulSoup
import re
import time

url_import_tags={
	'href':['a','area','base','link'],
	'action':['form'],
	'src':['audio','embed','iframe','img','input','script','source','track','video'],
	'target':['a','area','base','form'],
	'form': ['button','fieldset','input','label','meter','object','output','select','textarea']
}
file_extension=['png', 'mp4', 'css', 'svg', 'pdf', 'jpg']

class URL_Crawler(object):
	def __init__(self, main_url, rate_limit):
		self.main_url=main_url[:-1] if main_url[-1] == '/' else main_url
		self.rate_limit = 3
		self.depth=0
		self.main_processing=urlparse(self.main_url)
		self.scheme=self.main_processing.scheme
		self.domain=self.main_processing.netloc.replace('www.','').split('.')[0]
		self.dot='.'.join(self.main_processing.netloc.replace('www.','').split('.')[1:])
		self.url_path=set()
		self.url_pull_path_query=defaultdict(list)
		self.unidentified_url= set([self.main_url])
		self.identified_url=list()
		self.no_important_url=set()
		self.error_url=list()
	def Get_Html(self, url):
		try:
			r=requests.get(url, timeout=1)
		except:
			return None
		return r.text

	def Html_Processing(self, html, url):
		def check_path(attr_str, url):
			if attr_str == '/' or attr_str.startswith('#') or attr_str.startswith('_blank') or attr_str.startswith('_tml') \
				or attr_str.startswith('javascript:') or attr_str.startswith('tel:') or attr_str_startswith('mailto') or attr_str.startswith \
					or not attr_str:
				return False
			parsing = urlparse(attr_str)
			if parsing.scheme:
				if self.domain in parsing.netloc.replace('www', ''):
					pass
				else:
					return False
			if not attr_str.startswith("/"):
				_=url.split('/')[-1].split('?')[0]
				attr_str=urlparse(url).path.replace(_, attr_str)
			processing_path=re.sub("\/+", "/", attr_str)
			path=re.findall("(\/.*\/)", processing_path)
			full_path=self.scheme + "://" + self.domain+'.'+self.dot+processing_path
			if parsing.query:
				_=self.scheme+"://"+self.domain+'.'+self.dot+processing_path.split('?')[0]
				self.url_pull_path_query[_].append(parsing.query)
			if path:
				self.url_path=self.url_path.union([path][0])
			return full_path
		soup=BeautifulSoup(html,'html.parser')
		url_sets=set()
		for attr, tags in url_import_tags.items():
			for tag in tags:
				for find_tag in soup.find_all(tag, {attr: True}):
					attr_str=find_tag[attr]
					_=check_path(attr_str,url)
					if _:
						url_sets=url_sets.union([_])
		return url_sets

	def Rrl_Processing(self, url_sets):
		for url in url_sets:
			if '.' in url:
				if url.split('.')[-1] in file_extension:
					self.no_important_url=self.no_important_url.union([url])
				else:
					self.unidentified_url=self.unidentified_url.union([url])
			else:
				self.url_path=self.url_path.union([url])

	def Crawler(self,url):
		html=self.Get_Html([url])
		i=0
		while i < self.rate_limit:
			if html:
				time.sleep(0.1)
				url_sets=self.Html_Processing(html,url)
				self.Rrl_Processing(url_sets)
				return True
			else:
				time.sleep(1)
				print("URL {} TIMEOUT[{}/{}]".format(url,1+1,self.rate_limit))
			i+=1
		return False

	def Worker(self):
		i=1
		while i<100:
			url=self.unidentified_url.pop()
			if url in self.identified_url:
				continue
			print("URL {} | {} -> depth : {}".format(url,len(self.unidentified_url),i))
			if self.Crawler(url):
				self.identified_url.append(url)
			else:
				print("URL {} Error".format(url))
				self.error_url.append(url)
			i+=1
		print("Information Get End")
		self.Saved_To_Html()
		return

	def Saved_To_Html(self):
		with open('result.html','w')as f:
			f.write("<h1>URL PATH</h1>")
			for url_path in self.url_path:
				f.write('<li><a href="{}">{}</a></li>'.format(url_path,url_path))
			f.write("<br><br>")
			f.write("<h1>URL LIST</h1>")
			for url in self.identified_url:
				f.write('<li><a href="{}">{}</a></li>'.format(url,url))
			f.write("<br></br>")
			f.write("<h1>URL Query</h1>")
			for url,query_list in self.url_pull_path_query.items():
				f.write("<br>")
				f.write("<h2>{}</h2>".format(url))
				for query in query_list:
					f.write('<li><a href="{}">{}</a></li>'.format(url+'?'+query,query))
			f.write("<br><br>")

if __name__=="__main__":
	crawler=URL_Crawler("https://webhacking.kr",3)   #INSERT URL
	crawler.Worker()
