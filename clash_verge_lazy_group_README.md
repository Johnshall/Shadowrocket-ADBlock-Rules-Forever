# Clash Verge Rev 国内直连 / 国外代理配置

本配置把 `lazy_group.conf` 的分流思路转换成 Clash Verge Rev 使用的 Mihomo 规则：

- 局域网、中国大陆域名和中国大陆 IP：`DIRECT`
- 国外常用服务及未命中流量：`🚀 节点选择`
- AI、YouTube、Netflix、Disney+、Max、Spotify、Telegram 等保留独立策略组
- DNS 按国内外分流，国外 DNS 查询按规则走代理
- 不写入机场订阅地址或私人节点，可安全放在公开仓库

## 文件

- `clash_verge_lazy_group.js`：Clash Verge Rev 全局扩展脚本，可套用到现有任意 Clash/Mihomo 节点订阅。

## 使用方法

1. 先在 Clash Verge Rev 的“订阅/配置”页导入并更新你的机场订阅，确认能够看到节点。
2. 打开“设置”中的“全局扩展脚本（Global Script）”。
3. 新建脚本，把 `clash_verge_lazy_group.js` 的全部内容粘贴进去并保存、启用。
4. 回到订阅页，更新并启用原订阅；在“代理”页选择 `🚀 节点选择` 或 `♻️ 自动选择`。
5. Windows 上建议开启“系统代理”；需要让 UWP、游戏或其他非系统代理程序也分流时，再开启 TUN 模式。

> 注意：这是“订阅增强脚本”，不是节点订阅本身。公开配置无法替你保存私人订阅 URL；脚本会复用你已经导入的节点。

## 路由顺序

1. 局域网直连。
2. 常用境外服务进入各自策略组。
3. 国内常用服务直连。
4. 已知国外域名走代理，已知中国域名和中国 IP 直连。
5. 其余未命中流量统一走代理。

## 验证要点

- `baidu.com`、`qq.com`、国内 APP：应显示 `DIRECT`。
- `google.com`、`youtube.com`、`github.com`：应显示对应服务组或 `🚀 节点选择`。
- `ip111.cn` 可辅助检查国内外出口，但网站显示结果也受浏览器缓存、DNS 缓存和节点能力影响。
- 若启用脚本后提示“没有代理节点”，先更新原订阅；这代表订阅内容为空，不是规则语法错误。

## 规则来源

服务规则使用 `blackmatrix7/ios_rule_script` 的 Clash YAML 规则集，每 24 小时由 Mihomo 自动检查更新。总体分流仍保持原 `lazy_group.conf` 的目标：国内直连、国外代理。
