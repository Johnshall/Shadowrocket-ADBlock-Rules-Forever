# 规则文件开发说明

这里是规则文件的生成车间，欢迎访问。


## 规则模板

`template/` 目录下为规则模板，`build_confs.py` 脚本运行时会按照模板生成规则文件。

每个规则对应一个模板，不过 `sr_head.txt` 和 `sr_foot.txt` 是例外，这两个文件是所有模板的公共的头部和尾部。


## 手工配置的文件

**manual_direct.txt**

列表，手动编写。记录走直连的域名或 IP。

**manual_proxy.txt**

列表，手动编写。记录走代理的域名或 IP。

**manual_reject.txt**

列表，手动编写。记录需要屏蔽的域名或 IP。

**manual_gfwlist_excludes.txt**

列表，手动编写。记录 gfwlist 误杀的域名或 IP。

**manual_gfwlist.txt**

GFWList 不能无损转换为 SR 规则，所以这里是对 GFWList 的补充。


## 代码及自动生成的文件

**resultant/top50_direct.list** 

域名列表，由 `top500.py` 自动生成。记录着前 50 网站中所有可直连网站的域名。

**resultant/top50_proxy.list** 

域名列表，由 `top500.py` 自动生成。记录着前 50 网站中无法直连网站的域名。

其中未包括含有 `google` 关键字的域名，并且首页请求时间大于 10 秒也视为无法直连。

**top500.py**

脚本，运行所需时间较长。自动爬取生成 `top500_*.list` 文件。

-----------------------------------

**resultant/ad.list**

广告列表，由 `ad.py` 自动生成。包括所有需要屏蔽的广告服务器的域名和 IP。

**ad.py**

脚本，从指定的 Adblock Rule 中提取广告服务器的域名和 IP 至 `ad.list` 文件。

-----------------------------------

**resultant/gfw.list**

域名列表，由 `gfwlist.py` 自动生成。包含 GFWList 所定义的需要走代理的网站。

**resultant/gfw_unhandle.log**

运行日志，由 `gfwlist.py` 自动生成。GFWList 不能无损转换为 SR 规则，这里记录着未能转换的 GFWList 规则。

每当该文件发生变化，需要对应修改 `manual_gfwlist.txt` 文件。

**gfwlist.py**

脚本。解译最新版本的 GFWList。
