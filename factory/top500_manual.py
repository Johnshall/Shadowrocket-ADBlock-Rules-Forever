# -*- coding: utf-8 -*-

'''
此脚本用于对 top500_manual.list 中网站进行评估，判断需要直连或代理
该脚本应当在内网环境中运行
TODO:并发
'''

import requests
import time

# 读入 top500 列表
domains = [] 
with open("resultant/top500_manual.list", "r", encoding='utf-8') as f:
    for domain in f.readlines():
        if domain[0] == "#":
            continue
        domains.append(domain)

# 判断直连或代理
domains_proxy = []
domains_direct = []

def UrlScaner(domain):
    requests_header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'Cache-Control': 'max-age=0',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-HK;q=0.6,zh-TW;q=0.4,en;q=0.2',
    'Connection': 'keep-alive'
}
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

    print('Proxy %s：%s' % (is_proxy, domain) )

for domain in domains:
    UrlScaner(domain)


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
