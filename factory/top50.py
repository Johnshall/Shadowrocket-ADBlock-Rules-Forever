# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import threading
import time
import sys
import requests
import re

'''
# 更新说明：

# 由于原引 http://alexa.chinaz.com/Global/index.html 仅提供前 50 榜单，且难以爬取，
# 我们因此改为从 www.similarweb.com 中爬去世界前 50 榜单
# 由于世界前 500 网站列表无法以免费的方式呈现，所以改为较有代表性的前 50 榜单

urls = ['http://alexa.chinaz.com/Global/index.html']
for i in range(2,21):
    urls.append('http://alexa.chinaz.com/Global/index_%d.html'%i)
'''


urls = 'https://www.similarweb.com/zh/top-websites/united-states/?utm_source=addon&utm_medium=chrome&utm_content=overview&utm_campaign=country-rank'

urls_scan_over = False

domains = []

domains_proxy = []
domains_direct = []

requests_header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'Cache-Control': 'max-age=0',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-HK;q=0.6,zh-TW;q=0.4,en;q=0.2',
    'Connection': 'keep-alive'
}


def getTop(urls):
    global requests_header
    r = requests.get(url = 'https://www.similarweb.com/zh/top-websites/united-states/?utm_source=addon&utm_medium=chrome&utm_content=overview&utm_campaign=country-rank', 
    headers=requests_header)
    soup = BeautifulSoup(r.text, "lxml")
    namesDom = soup.select("span.topRankingGrid-titleName")

    for name in namesDom:
        domains.append(name.string)
    
    print('{:-^30}'.format('We get!'))
    print('{:-^30}'.format('Top50 Fetching over'))
    print('\n')
    print('\n\n')


# Start
print('{:-^30}'.format('Top50 Script Starting'))
print('\n')
getTop(urls)

# thread to visit websites
while len(domains):
    domain = domains.pop(0)
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
        print(domain + "is proxy\n")
    else:
        domains_direct.append(domain)
        print(domain + "is direct\n")

    print('[Doamins Remain: %d]\tProxy %s：%s\n' % (len(domains), is_proxy, domain) )


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
file_proxy = open('resultant/top50_proxy.list', 'w', encoding='utf-8')
file_direct = open('resultant/top50_direct.list', 'w', encoding='utf-8')

now_time = time.strftime("%Y-%m-%d %H:%M:%S")
file_proxy.write('# top50 proxy list update time: ' + now_time + '\n')
file_direct.write('# top50 direct list update time: ' + now_time + '\n')

domains_direct = list( set(domains_direct) )
domains_proxy  = list( set(domains_proxy) )
domains_direct.sort()
domains_proxy.sort()

for domain in domains_direct:
    file_direct.write(domain+'\n')
for domain in domains_proxy:
    file_proxy.write(domain+'\n')

print('{:-^30}'.format('Done!'))
