// Clash Verge Rev 全局扩展脚本
// 目标：局域网/中国大陆网站直连，国外网站走代理，并保留 lazy_group.conf 的常用服务分组。
// 使用方法见 clash_verge_lazy_group_README.md。

const DIRECT = "DIRECT";
const NODE_SELECT = "🚀 节点选择";
const AUTO_SELECT = "♻️ 自动选择";

const providerCommon = {
  type: "http",
  behavior: "classical",
  format: "yaml",
  interval: 86400,
};

const providerSources = {
  ai_openai: "OpenAI",
  ai_gemini: "Gemini",
  ai_claude: "Claude",
  ai_copilot: "Copilot",
  youtube: "YouTube",
  netflix: "Netflix",
  disney: "Disney",
  hbo: "HBO",
  spotify: "Spotify",
  telegram: "Telegram",
  paypal: "PayPal",
  twitter: "Twitter",
  facebook: "Facebook",
  amazon: "Amazon",
  sony: "Sony",
  nintendo: "Nintendo",
  epic: "Epic",
  steam_cn: "SteamCN",
  steam: "Steam",
  game: "Game",
  github: "GitHub",
  microsoft: "Microsoft",
  google: "Google",
  apple: "Apple",
  bilibili: "BiliBili",
  netease_music: "NetEaseMusic",
  baidu: "Baidu",
  douban: "DouBan",
  wechat: "WeChat",
  sina: "Sina",
  zhihu: "Zhihu",
  xiaohongshu: "XiaoHongShu",
  douyin: "DouYin",
  tiktok: "TikTok",
  global: "Global",
  china: "China",
  lan: "Lan",
};

function makeRuleProviders() {
  const providers = {};
  Object.keys(providerSources).forEach((key) => {
    const source = providerSources[key];
    providers[key] = {
      ...providerCommon,
      url: `https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/${source}/${source}.yaml`,
      path: `./ruleset/blackmatrix7/${key}.yaml`,
    };
  });
  return providers;
}

const proxyChoices = [NODE_SELECT, AUTO_SELECT, DIRECT];
const directChoices = [DIRECT, NODE_SELECT, AUTO_SELECT];

function serviceGroup(name, directFirst) {
  return {
    name,
    type: "select",
    proxies: directFirst ? directChoices : proxyChoices,
  };
}

function makeProxyGroups() {
  return [
    {
      name: NODE_SELECT,
      type: "select",
      proxies: [AUTO_SELECT, DIRECT],
      "include-all": true,
    },
    {
      name: AUTO_SELECT,
      type: "url-test",
      "include-all": true,
      url: "https://www.gstatic.com/generate_204",
      interval: 600,
      timeout: 5000,
      tolerance: 50,
      lazy: true,
    },
    serviceGroup("🤖 AI", false),
    serviceGroup("📹 YouTube", false),
    serviceGroup("🎬 Netflix", false),
    serviceGroup("🏰 Disney+", false),
    serviceGroup("🎞️ Max", false),
    serviceGroup("🎵 Spotify", false),
    serviceGroup("✈️ Telegram", false),
    serviceGroup("🐦 Twitter", false),
    serviceGroup("📘 Facebook", false),
    serviceGroup("💳 PayPal", false),
    serviceGroup("📦 Amazon", false),
    serviceGroup("🍎 苹果服务", true),
    serviceGroup("🔍 谷歌服务", false),
    serviceGroup("🪟 微软服务", true),
    serviceGroup("📺 哔哩哔哩", true),
    serviceGroup("🎮 游戏平台", true),
  ];
}

function makeRules() {
  return [
    // 私有网络优先直连。
    "RULE-SET,lan,DIRECT",

    // lazy_group.conf 中的国外服务分组。
    "RULE-SET,ai_openai,🤖 AI",
    "RULE-SET,ai_gemini,🤖 AI",
    "RULE-SET,ai_claude,🤖 AI",
    "RULE-SET,ai_copilot,🤖 AI",
    "RULE-SET,youtube,📹 YouTube",
    "RULE-SET,netflix,🎬 Netflix",
    "RULE-SET,disney,🏰 Disney+",
    "DOMAIN-SUFFIX,litix.io,🎞️ Max",
    "DOMAIN-SUFFIX,discomax.com,🎞️ Max",
    "DOMAIN-SUFFIX,brightline.tv,🎞️ Max",
    "RULE-SET,hbo,🎞️ Max",
    "RULE-SET,spotify,🎵 Spotify",
    "RULE-SET,telegram,✈️ Telegram",
    "RULE-SET,twitter,🐦 Twitter",
    "RULE-SET,facebook,📘 Facebook",
    "RULE-SET,paypal,💳 PayPal",
    "RULE-SET,amazon,📦 Amazon",
    "RULE-SET,tiktok,🚀 节点选择",

    // 游戏、开发与系统服务。
    "RULE-SET,sony,🎮 游戏平台",
    "RULE-SET,nintendo,🎮 游戏平台",
    "RULE-SET,epic,🎮 游戏平台",
    "RULE-SET,steam_cn,🎮 游戏平台",
    "RULE-SET,steam,🎮 游戏平台",
    "RULE-SET,game,🎮 游戏平台",
    "RULE-SET,github,🚀 节点选择",
    "RULE-SET,microsoft,🪟 微软服务",
    "RULE-SET,google,🔍 谷歌服务",

    // 国内常用服务默认直连。
    "RULE-SET,apple,🍎 苹果服务",
    "RULE-SET,bilibili,📺 哔哩哔哩",
    "RULE-SET,netease_music,DIRECT",
    "RULE-SET,baidu,DIRECT",
    "RULE-SET,douban,DIRECT",
    "RULE-SET,wechat,DIRECT",
    "RULE-SET,sina,DIRECT",
    "RULE-SET,zhihu,DIRECT",
    "RULE-SET,xiaohongshu,DIRECT",
    "RULE-SET,douyin,DIRECT",

    // 国内外总分流：已知国外域名代理，已知中国域名和中国 IP 直连。
    "RULE-SET,global,🚀 节点选择",
    "RULE-SET,china,DIRECT",
    "GEOIP,LAN,DIRECT,no-resolve",
    "GEOIP,CN,DIRECT,no-resolve",

    // 未命中规则的域名/IP 一律代理，避免国外网站漏走直连。
    "MATCH,🚀 节点选择",
  ];
}

function makeDnsConfig() {
  const domesticDns = [
    "https://doh.pub/dns-query",
    "https://dns.alidns.com/dns-query",
  ];
  const foreignDns = [
    "https://1.1.1.1/dns-query#RULES",
    "https://8.8.8.8/dns-query#RULES",
  ];

  return {
    enable: true,
    listen: "0.0.0.0:1053",
    ipv6: true,
    "prefer-h3": false,
    "cache-algorithm": "arc",
    "use-hosts": true,
    "use-system-hosts": true,
    "respect-rules": true,
    "enhanced-mode": "fake-ip",
    "fake-ip-range": "198.18.0.1/16",
    "fake-ip-filter": [
      "*.lan",
      "*.local",
      "+.msftconnecttest.com",
      "+.msftncsi.com",
      "localhost.ptlogin2.qq.com",
      "localhost.sec.qq.com",
      "localhost.work.weixin.qq.com",
      "time.*.com",
      "time.*.gov",
      "pool.ntp.org",
    ],
    "default-nameserver": ["223.5.5.5", "119.29.29.29"],
    nameserver: domesticDns,
    fallback: foreignDns,
    "proxy-server-nameserver": domesticDns,
    "nameserver-policy": {
      "geosite:private,cn,geolocation-cn": domesticDns,
      "geosite:gfw,geolocation-!cn": foreignDns,
    },
    "fallback-filter": {
      geoip: true,
      "geoip-code": "CN",
    },
  };
}

function main(config) {
  const proxyCount = Array.isArray(config.proxies) ? config.proxies.length : 0;
  const providerCount =
    config["proxy-providers"] && typeof config["proxy-providers"] === "object"
      ? Object.keys(config["proxy-providers"]).length
      : 0;

  if (proxyCount === 0 && providerCount === 0) {
    throw new Error("订阅配置中没有代理节点或 proxy-providers，请先导入可用的节点订阅。");
  }

  config.mode = "rule";
  config["unified-delay"] = true;
  config["tcp-concurrent"] = true;
  config.dns = makeDnsConfig();
  config["rule-providers"] = makeRuleProviders();
  config["proxy-groups"] = makeProxyGroups();
  config.rules = makeRules();

  return config;
}
