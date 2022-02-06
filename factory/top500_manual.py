# -*- coding: utf-8 -*-

'''
此脚本用于对 top500_manual.list 中网站进行评估，判断需要直连或代理
该脚本应当在内网环境中运行
'''

import requests
import time
import threading

# Read top500
domains = [] 
with open("resultant/top500_manual.list", "r", encoding='utf-8') as f:
    for domain in f.readlines():
        if domain[0] == "#":
            continue
        domains.append(domain[:-1])

domains_proxy = []
domains_direct = []
requests_header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'Cache-Control': 'max-age=0',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-HK;q=0.6,zh-TW;q=0.4,en;q=0.2',
    'Connection': 'keep-alive'
}

# thread to judge direct/proxy
class DomainScaner(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
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
            else:
                domains_direct.append(domain)

            print('[Doamins Remain: %d]\tProxy %s：%s' % (len(domains), is_proxy, domain) )


        global scaner_thread_num
        scaner_thread_num -= 1


print('top500 Script Starting...\n\n')

# Start Thread
scaner_thread_num = 0
for i in range(5):
    DomainScaner().start()
    scaner_thread_num += 1

# wait thread done
while scaner_thread_num:
    pass


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
