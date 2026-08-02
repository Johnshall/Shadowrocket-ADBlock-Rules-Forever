import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";

const source = fs.readFileSync(new URL("../clash_verge_lazy_group.js", import.meta.url), "utf8");
const context = vm.createContext({});
vm.runInContext(`${source}\nthis.__main = main;`, context, {
  filename: "clash_verge_lazy_group.js",
});

const input = {
  proxies: [
    {
      name: "测试节点",
      type: "ss",
      server: "127.0.0.1",
      port: 8388,
      cipher: "aes-128-gcm",
      password: "test-only",
    },
  ],
  rules: ["MATCH,DIRECT"],
};

const output = context.__main(input);
const groupNames = output["proxy-groups"].map((group) => group.name);
const providerNames = Object.keys(output["rule-providers"]);

assert.equal(output.mode, "rule");
assert.equal(output.rules.at(-1), "MATCH,🚀 节点选择");
assert(output.rules.includes("RULE-SET,china,DIRECT"));
assert(output.rules.includes("GEOIP,CN,DIRECT,no-resolve"));
assert(output.rules.indexOf("RULE-SET,global,🚀 节点选择") < output.rules.indexOf("RULE-SET,china,DIRECT"));
assert(groupNames.includes("🚀 节点选择"));
assert(groupNames.includes("♻️ 自动选择"));
assert(providerNames.includes("global"));
assert(providerNames.includes("china"));
assert(providerNames.includes("lan"));
assert.equal(output.dns["respect-rules"], true);
assert.throws(() => context.__main({}), /没有代理节点/);

const outputPath = process.argv.find((argument) => argument.endsWith(".json"));
if (outputPath) {
  fs.writeFileSync(outputPath, JSON.stringify(output, null, 2));
}

if (process.argv.includes("--network")) {
  const checks = await Promise.all(
    Object.entries(output["rule-providers"]).map(async ([name, provider]) => {
      const response = await fetch(provider.url, { method: "HEAD" });
      return { name, status: response.status, ok: response.ok };
    }),
  );
  const failed = checks.filter((check) => !check.ok);
  assert.deepEqual(failed, [], `失效规则集: ${JSON.stringify(failed)}`);
  console.log(`OK: ${checks.length} remote rule-provider URLs returned HTTP 2xx`);
}

console.log(`OK: ${output.rules.length} rules, ${groupNames.length} groups, ${providerNames.length} providers`);
