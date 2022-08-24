# -*- coding: utf-8 -*-

#
# 下载并解析最新版本的 GFWList
# 对于混合性质的网站，尽量走代理（忽略了所有的@@指令）
#
# 从 https://github.com/Johnshall/cn-blocked-domain 中获取GFWList的补充
# 感谢 https://github.com/Loyalsoldier/cn-blocked-domain
#


import time
import requests
import re
import base64


unhandle_rules = []

# ruleType for raw or base64
def get_rule(rules_url, ruleType='raw'):
    success = False
    try_times = 0
    r = None
    while try_times < 5 and not success:
        r = requests.get(rules_url)
        if r.status_code != 200:
            time.sleep(1)
            try_times = try_times + 1
        else:
            success = True
            break

    if not success:
        raise Exception('error in request %s\n\treturn code: %d' % (rules_url, r.status_code) )

    if ruleType == 'base64':
        rule = base64.b64decode(r.text) \
                .decode("utf-8") \
                .replace('\\n', '\n')
    else:
        rule = r.text

    return rule


def clear_format(rule):
    rules = []

    rule = rule.split('\n')
    for row in rule:
        row = row.strip()

        # 注释 直接跳过
        if row == '' or row.startswith('!') or row.startswith('@@') or row.startswith('[AutoProxy'):
            continue

        # 清除前缀
        row = re.sub(r'^\|?https?://', '', row)
        row = re.sub(r'^\|\|', '', row)
        row = row.lstrip('.*')

        # 清除后缀
        row = row.rstrip('/^*')

        rules.append(row)

    return rules


def filtrate_rules(rules, excludes=[]):
    ret = []

    for rule in rules:
        rule0 = rule

        # only hostname
        if '/' in rule:
            split_ret = rule.split('/')
            rule = split_ret[0]

        if not re.match('^[\w.-]+$', rule):
            unhandle_rules.append(rule0)
            continue

        if rule in excludes:
            continue

        ret.append(rule)

    ret = list( set(ret) )
    ret.sort()

    return ret

def getURLs(url):
    r = requests.get(url)
    return r.text.split("\n")[:-1]

# main

rule = get_rule(rules_url='https://raw.githubusercontent.com/gfwlist/gfwlist/master/gfwlist.txt', ruleType='base64')
# 从 https://github.com/Johnshall/cn-blocked-domain 中获取GFWList的补充
rule += get_rule('https://raw.githubusercontent.com/Johnshall/cn-blocked-domain/release/domains.txt')

rules = clear_format(rule)

excludes = []
with open('manual_gfwlist_excludes.txt', 'r', encoding='utf-8') as f:
    for line in f.readlines():
        if line[0] == "#" or line == "\n":
            continue
        excludes.append(line.strip())

rules = filtrate_rules(rules, excludes)

rules = list( set(rules) )

open('resultant/gfw.list', 'w', encoding='utf-8') \
    .write('\n'.join(rules))

open('resultant/gfw_unhandle.log', 'w', encoding='utf-8') \
    .write('\n'.join(unhandle_rules))
