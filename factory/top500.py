# -*- coding: utf-8 -*-

'''
#警告：
由于站长之家已不再免费提供全球top500名单，此脚本已无法使用
这里仅仅是做备份，待可靠top500名单源时将会重新发布
'''

from bs4 import BeautifulSoup
import threading
import time
import sys
import requests
import re

urls = ['http://alexa.chinaz.com/Global/index.html']
for i in range(2,21):
    urls.append('http://alexa.chinaz.com/Global/index_%d.html'%i)

urls_scan_over = False

domains = []

domains_proxy = []
domains_direct = []


# thread to scan pages in urls
class UrlScaner(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        global urls_scan_over, urls

        done_num = 0

        while len(urls):
            html = self.fetchHTML( urls.pop(0) )
            self.praseHTML(html)

            done_num = done_num + 25
            print('top500 List Got: %d/500'%done_num)

            time.sleep(1)

        urls_scan_over = True
        print('top500 List Fetched Over.')


    def fetchHTML(self, url):
        success = False
        try_times = 0
        r = None
        while try_times < 5 and not success:
            r = requests.get(url)
            if r.status_code != 200:
                time.sleep(1)
                try_times = try_times + 1
            else:
                success = True
                break

        if not success:
            sys.exit('error in request %s\n\treturn code: %d' % (url, r.status_code) )

        r.encoding = 'utf-8'
        return r.text


    def praseHTML(self, html):
        soup = BeautifulSoup(html, "lxml")
        namesDom = soup.select("div.righttxt h3 span")

        for name in namesDom:
            domains.append(name.string)


requests_header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'Cache-Control': 'max-age=0',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-HK;q=0.6,zh-TW;q=0.4,en;q=0.2',
    'Connection': 'keep-alive'
}


# thread to visit websites
class DomainScaner(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while not urls_scan_over or len(domains):
            if len(domains) == 0:
                time.sleep(2)
                continue

            domain = domains.pop(0)

            if domain.endswith('.cn'):
                continue
            if 'google' in domain:
                continue

            is_proxy = False

            try:
                requests.get('http://www.' + domain, timeout=10, headers=requests_header)
            except BaseException:
                try:
                    requests.get('http://' + domain, timeout=10, headers=requests_header)
                except BaseException:
                    is_proxy = True

            if is_proxy:
                domains_proxy.append(domain)
            else:
                domains_direct.append(domain)

            print('[Doamins Remain: %d]\tProxy %s：%s' % (len(domains), is_proxy, domain) )

        global scaner_thread_num
        scaner_thread_num -= 1


print('top500 Script Starting...\n\n')

# Start Thread
UrlScaner().start()
scaner_thread_num = 0
for i in range(3):
    DomainScaner().start()
    scaner_thread_num += 1

# wait thread done
while scaner_thread_num:
    pass

# 将苹果IP加入直连
# 由于本脚本应当运行在内部环境中，可能无法访问Github，故改用staticdn.net提供的CDN节点
# r = requests.get(url="https://raw.githubusercontent.com/felixonmars/dnsmasq-china-list/master/apple.china.conf", headers=requests_header)
print('{:-^30}'.format('将苹果IP加入直连'))
print('\n\n')
r = requests.get(url='https://raw.staticdn.net/felixonmars/dnsmasq-china-list/master/apple.china.conf', headers=requests_header)
for url in r.text.split("\n")[:-1]:
    url = re.sub(r'(server=\/)', '', url)   # 清除前缀
    url = re.sub(r'(/114.114.114.114)', '', url)   # 清除后缀
    domains_direct.append(url)

# write files
file_proxy = open('resultant/top500_proxy.list', 'w', encoding='utf-8')
file_direct = open('resultant/top500_direct.list', 'w', encoding='utf-8')

now_time = time.strftime("%Y-%m-%d %H:%M:%S")
file_proxy.write('# top500 proxy list update time: ' + now_time + '\n')
file_direct.write('# top500 direct list update time: ' + now_time + '\n')

domains_direct = list( set(domains_direct) )
domains_proxy  = list( set(domains_proxy) )
domains_direct.sort()
domains_proxy.sort()

for domain in domains_direct:
    file_direct.write(domain+'\n')
for domain in domains_proxy:
    file_proxy.write(domain+'\n')

print('{:-^30}'.format('Done!'))
