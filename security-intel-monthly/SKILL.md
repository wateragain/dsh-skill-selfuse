---
name: security-intel-monthly
description: 汇总某个月的网络安全、操作系统安全、开源与供应链安全事件，输出含 CVE/CVSS、代价量化和修复版本的分类清单表格。用户说"月度安全情报""这个月有什么漏洞""安全月报""收集某月安全事件"时使用。
whenToUse: 需要按月份盘点安全漏洞、勒索与数据泄露、APT 活动或供应链投毒，并要一张可直接交付的表格时。
---

# 月度安全情报收集

## 0. 先定口径（三问封顶，别猜）

用 ask_user_question 一次问完：覆盖范围（15–20 条要点 / 50+ 条全量 / 三分类各配额）、输出形态（对话内表格 / Markdown / Excel）、附加内容（勒索与 APT / 国内监管政策 / 纯漏洞）。

默认：50+ 条、对话内表格、含勒索与 APT；**监管政策必须显式确认才加**。时间窗默认"本月 1 日～今天"，正文写明"X 月未完"。

## 1. 来源分层

| 层 | 来源 | 用途 |
|---|---|---|
| 一手 | CISA KEV、NVD、微软 MSRC、Apple、Android AOSP、Ubuntu USN、Red Hat、GitLab/curl/PHP 官方公告、GitHub Advisory、CNNVD/CNCERT | CVE、CVSS、影响版本、修复版本 |
| 二手 | BleepingComputer、The Hacker News、SecurityWeek、SecurityAffairs、安全客/FreeBuf、六方云周报、SOCRadar、厂商实验室 | 在野利用、勒索归属、损失金额与数据量 |
| 兜底 | 会话内 rss-digest、Solidot | 只当线索，必须回查一手源 |

完整站点与 query 清单见 `references/sources.md`。

## 2. 检索模板（英文 query 命中率更高）

1. `CISA KEV catalog additions <Month> <Year>` — 拿每周新增，带修复版本与截止日
2. `Microsoft Patch Tuesday <Month> <Year> vulnerabilities CVE` — 补丁总量、严重数、0day 数
3. `<vendor> advisory <Month> <Year>`：Ivanti / Citrix NetScaler / Fortinet / SonicWall / PAN-OS / Atlassian / BeyondTrust / VMware
4. `Android security bulletin <Month> <Year>`、`Apple security content iOS <n>`、`Linux kernel CVE <Month> <Year>`
5. `npm PyPI supply chain attack <Month> <Year>`、`curl security advisory <Month> <Year>`、`GitLab critical patch release <Month> <Year>`
6. 中文侧：`CNCERT <Month>`、`CNNVD 漏洞通报`、`银狐 木马`、`数据泄露 <Month>`
7. **语言运行时（必查，不可省）**：`<lang> security release <Month> <Year>`，逐项跑 `references/sources.md` 里的 12 个语言渠道

每轮 4 个 query 并发，两三轮即可覆盖；拿不准的条目再 web_fetch 原文。语言运行时**不在** CISA/NVD 主流列表里，必须单独扫，否则整类漏掉。

## 3. 筛选与去重

- **收**：有 CVE/CNNVD 编号，或有可量化代价（条数、金额、停机、受害者数）
- **弃**：预测、观点、营销稿、无影响面的"已修复"公告
- 一漏洞多报只留一条，取最权威出处；同一事件的中英文报道算一条
- 每条必须落到"修复版本 / 公告号"，没有就写「无补丁」
- 单一媒体源 → 标「待核」，占比控制在 10% 以内

## 4. 输出模板

六节（第六节可选）：一 在野利用的关键漏洞；二 勒索与数据泄露；三 APT 与攻击活动；四 操作系统；五 **语言运行时与开源供应链**；六 监管政策。

第五节**强制按语言逐项核对**（Java、Python、JavaScript/Node、TypeScript、C#/.NET、C/C++、PHP、Go、Rust、Ruby、Kotlin、Swift），每个语言要么有一条漏洞，要么显式写「本月无」。宁可写"本月无"，也不许整类不出现——否则会出现"Java 一条没有、Python 只写 PyPI"的漏。

表列固定四列：`条目 | 核心漏洞/手法 | 代价 | 修复/状态`。计数写进每节标题（如"19 条"），总数与用户要求对齐。
开头 3 条结论写主线判断（不是罗列），结尾 3 条判断写可执行建议。

## 5. 交付前自检

- [ ] CVSS 与"是否在野"分开写，不混成一句
- [ ] 代价栏是数字或具体后果，不写"造成严重影响"
- [ ] 修复栏是版本号或公告号，不写"请及时更新"
- [ ] 时间窗写在正文；月度未过完写"截至 X 日共 N 条"
- [ ] **12 个热门语言逐一出现**，无漏洞的明确写「本月无」
- [ ] 用户删掉的节，结论里也不再出现对应论断

## 6. 已知坑

- **CVE 年份 ≠ 披露月份**：vCenter CVE-2026-59309 是 7 月编号、10 月仍在野，按公告日/入 KEV 日归档
- **KEV 按入目录日算**：2025 年的 CVE 可以当月才入 KEV，算当月事件
- **搜索结果混旧文**：搜某月的 Okta 会返回 2022 年 Lapsus$ 旧报道，必须核对正文日期
- **厂商口径冲突**：影响版本以厂商公告为准，CISA/NVD 只作旁证（如 BeyondTrust "all versions" vs "≤26.2.3"）
- **web_fetch 偶发 404**（抓取服务端问题）：失败一次即改用搜索摘要，不重试同一 URL
- **补丁量本身是风险**：单月上千条时，按"互联网可未认证触达"排序，不按 CVSS 排序
- **语言运行时不在主流漏洞列表**：OpenJDK 公告、python.org release、nodejs security blog 都不经过 CISA/NVD，必须按 `references/sources.md` 的语言表单独扫
- **CA 事故跨语言连坐**：一次中间 CA 泄露会同时打穿 Java / Python / Node / Go / Rust（换 `blocked.certs`、升 certifi、换 ca-cert 包）。看到任一生态改证书包，横向查其余四个

## 7. 交付后

问一句是否需要 Excel（按类别 / CVSS / 是否在野三列可筛）。用户要求删节时只删对应节，其余表格原样保留，不重写。用户指出漏项（如"某语言没有漏洞吗"）时，先补查再补表，并把漏因写进本节，不要只道歉。
