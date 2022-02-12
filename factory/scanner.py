# -*- coding: utf-8 -*-

# 简单的扫描直连/代理工具

import requests
import threading

domains = []
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

# Start Thread
scaner_thread_num = 0
for i in range(5):
    DomainScaner().start()
    scaner_thread_num += 1

# wait thread done
while scaner_thread_num:
    pass

print('domains_proxy:\t',domains_proxy)
print('domains_direct:\t',domains_direct)
