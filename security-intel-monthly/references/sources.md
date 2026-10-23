# 月度安全情报：源清单与 query 库

配套 `../SKILL.md`。只记"哪些站点出什么料"，不缓存具体漏洞数据（每月都变）。

## 一手源（定事实）

| 领域 | 站点 | 取什么 |
|---|---|---|
| 在野利用 | https://www.cisa.gov/known-exploited-vulnerabilities-catalog | 每周新增、截止日、勒索使用标记；镜像 `/security-news/cisa-kev-additions-*` 类站点会整理成表 |
| 漏洞库 | https://nvd.nist.gov/、https://vuldb.com/、https://vulnerability.circl.lu/ | CVSS、影响版本、修复版本 |
| 微软 | https://msrc.microsoft.com/update-guide | 补丁总量、严重级别、0day 标记、停更公告 |
| Apple | https://support.apple.com/en-us/100100（安全更新索引） | CVE 列表、受影响机型 |
| Android | https://source.android.com/docs/security/bulletin | Framework 严重项、补丁级别 |
| Linux | https://ubuntu.com/security/notices、https://access.redhat.com/security | USN/RHSA 编号、子系统 |
| 开源项目 | curl.se/docs/、docs.gitlab.com/releases/patches/、php.net/archive、github.com/advisories | 项目自己的 CVE 页最准 |
| 国内 | https://www.cert.org.cn/、CNNVD、https://www.gov.cn/ | 通报、风险提示、法规施行 |

## 二手源（定量化与归属）

- BleepingComputer / The Hacker News / SecurityWeek / SecurityAffairs / CyberWire — 在野细节
- SOCRadar `socradar.io/data-breach/` — 勒索团伙受害者、数据量、行业
- 六方云安全态势周刊（`6cloudtech.com/portal/article/index/id/`）— 中文侧周度汇总，含 CNCERT/CNNVD 转述
- 安全客 / FreeBuf / Solidot — 中文线索
- 厂商实验室：Kaspersky GReAT、Volexity、Rapid7、Elastic Security Labs、StepSecurity — APT 归属与供应链

## query 库（按主题复制）

**漏动与补丁**
```
CISA KEV catalog additions <Month> <Year>
Microsoft Patch Tuesday <Month> <Year> vulnerabilities CVE
<vendor> advisory <Month> <Year>          # Ivanti / Citrix / Fortinet / SonicWall / PAN-OS / Atlassian / BeyondTrust / VMware
Oracle Critical Patch Update <Month> <Year>
```

**操作系统**
```
Android security bulletin <Month> <Year>
Apple security content iOS <n> <Month> <Year>
macOS <name> security update CVE <Month> <Year>
Linux kernel CVE <Month> <Year> privilege escalation
Ubuntu USN kernel <Month> <Year>
HarmonyOS 安全公告 <Month> <Year>
```

**开源与供应链**
```
npm PyPI supply chain attack <Month> <Year>
curl security advisory <Month> <Year>
GitLab critical patch release <Month> <Year>
WordPress plugin vulnerability <Month> <Year> exploited
open source project critical vulnerability <Month> <Year>
```

**勒索与泄露**
```
ransomware <Month> <Year> claimed victims
<company> data breach <Month> <Year>
数据泄露 <Month> <Year> 亿条
勒索软件 <Month> <Year> 医院 学校
```

**APT 与国内**
```
APT campaign <Month> <Year>
零日漏洞 <Month> <Year> 在野利用
CNCERT <Month> <Year>
CNNVD 漏洞通报 <Month>
银狐 木马 <Month>
```

## 语言运行时渠道（每月必查 12 项）

这些渠道**都不经过** CISA/NVD 主流列表，必须单独扫。

| 语言 | 官方渠道 | query |
|---|---|---|
| Java | `openjdk.org/groups/vulnerability/advisories/` + Oracle CPU | `OpenJDK vulnerability advisory <Month> <Year>` |
| Python | `python.org/downloads/` release 页 + devguide 安全策略 | `CPython security release <Month> <Year>` |
| JavaScript / Node | `nodejs.org/en/blog/vulnerability/` | `Node.js security releases <Month> <Year>` |
| TypeScript | 无独立运行时，随 Node 与 npm advisory | 归入 npm 生态 |
| C# / .NET | MSRC update guide + dotnet/core 发布 | `dotnet security release <Month> <Year>` |
| C / C++ | glibc、GCC、LLVM 公告，发行版 RHSA/ALSA | `glibc vulnerability <Month> <Year>` |
| PHP | `php.net/releases` + php-src GHSA | `PHP security release <Month> <Year>` |
| Go | `go.dev/security` + golang-announce | `Go security release <Month> <Year>` |
| Rust | `rustsec.org/advisories` + blog.rust-lang.org | `RustSec advisory <Month> <Year>` |
| Ruby | `ruby-lang.org/en/news` 安全栏 + RubySec | `Ruby security release <Month> <Year>` |
| Kotlin | GitHub Advisory + Maven 生态 | `Kotlin vulnerability <Month> <Year>` |
| Swift | `forums.swift.org` Server / Security Updates | `Swift security update <Month> <Year>` |

有余力再扫：Dart/Flutter（pub.dev advisory）、Scala、Perl、Elixir、Deno/Bun、R。

**跨语言连坐规则**：出现 `blocked.certs`（Java）、certifi 升级（Python）、ca-cert 换包（Node）、证书移除发版（Go）、rustls-webpki 公告（Rust）任一项，其余四个立刻横向查——2026-10 的 eMudhra / emSign 中间 CA 泄露就是五生态同时中招。

## 2026-10 基线（输出形状参考）

60 条 = 在野利用 17 + 勒索泄露 12 + APT 6 + 操作系统 13 + 开源供应链 12。

该月三条主线：边缘设备 0day 集中爆发（Ivanti / BeyondTrust / Citrix / FortiMail / PAN-OS）；供应链从投毒包升级为自传播蠕虫 + CI 身份劫持（Shai-Hulud/ChainDrop）；Windows 单月 1407 个补丁使漏修率成为主风险指标。
