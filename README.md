# 💰 Finance Vault - 模板版

> 基于 Obsidian + DataviewJS 的个人理财记账系统
> LLM 是财务助手，支持**图片 OCR 识别**和**自然语言**记账

## 📌 重要说明

**这是模板仓库，不包含任何私人数据。**

如果你看到此文件，说明你正在使用 Finance Vault 的开源模板。请按以下步骤开始使用：

1. 复制此仓库到你的本地
2. 删除 `raw/transactions/transactions/index.md` 中的示例数据
3. 告诉 LLM 助手你的第一笔支出/收入

---

## 核心理念

- **LLM 是助手** — 帮你识别图片、记录交易、分析消费
- **图片记账** — 保存付款截图，OCR 自动识别金额/商家/日期
- **对话式记账** — 直接说出消费，AI 自动整理写入
- **本地存储** — 数据完全属于自己，不上传任何服务器
- **Obsidian 可视化** — DataviewJS 渲染图表，实时读取数据

---

## 目录结构

```
finance_vault/
├── CLAUDE.md                           ← LLM 财务助手系统提示
├── README.md                           ← 本文件
│
├── raw/
│   ├── transactions/
│   │   ├── transactions/
│   │   │   └── index.md               ← ⭐ 唯一数据源（YAML 代码块格式）
│   │   └── records/
│   │       └── 2026-04.md             ← 月度 JSON 归档（仅存档用）
│   └── receipts/
│       └── processed/                 ← 已处理的付款截图
│
├── wiki/
│   ├── index.md                       ← 财务总览仪表盘
│   ├── charts.md                      ← 📊 图表中心（支出占比/趋势/收支对比）
│   ├── monthly/
│   │   └── 2026-04.md                 ← 月度报告（交易明细+汇总）
│   └── yearly/
│       └── 2026.md                    ← 年度报告（各月概览卡片）
│
├── budget/
│   └── categories.yaml                ← 支出分类配置
│
├── scripts/
│   ├── ocr_receipt.py                 ← 票据 OCR 识别脚本
│   ├── finance_lint.py                ← 数据一致性检查脚本
│   ├── update_dataview_source.py      ← DataviewJS 数据源更新工具
│   └── test_lint.py                   ← Lint 脚本测试
│
└── e2e_results/                       ← 端到端测试结果
```

---

## 快速开始

### 方式一：自然语言记账（推荐）💬

直接告诉 LLM（WorkBuddy / Claude）：

```
"今天买咖啡花了 45 块"
"网购买了双鞋，130.14 元，微信支付"
"昨天加油 56.46 元，用微信零钱付的"
```

LLM 会自动将记录写入 `raw/transactions/transactions/index.md` 并同步更新所有关联文件。

### 方式二：图片 OCR 记账 🖼️

```bash
# 把付款截图放到 raw/receipts/ 目录，然后告诉 LLM：
"处理一下 raw/receipts/ 里的截图"

# 或者直接用脚本识别：
python scripts/ocr_receipt.py raw/receipts/screenshot.jpg
```

**支持的截图类型：**
- 微信/支付宝支付成功页
- 银行扣款通知短信截图
- 电商订单截图
- 发票照片

### 方式三：查询与分析 📊

在 Obsidian 中打开：
- `wiki/charts.md` — 图表中心，修改顶部 `month:` 切换月份
- `wiki/index.md` — 财务总览
- `wiki/monthly/2026-04.md` — 月度详情
- `wiki/yearly/2026.md` — 年度概览

或直接问 LLM：
```
"我这个月在购物上花了多少？"
"帮我生成4月的月度报告"
"有什么异常支出吗？"
```

---

## 数据格式

交易记录存储在 `raw/transactions/transactions/index.md`，每条记录为一个 YAML 代码块：

```yaml
---
id: 20260421-001
date: 2026-04-21
time: ""
amount: 130.14
type: expense          # expense（已支付）/ income（收入）/ pending（待扣款）
category: 购物
subcategory: 鞋子
merchant: 网络购物
account: 网络支付
status: 已支付
note: 网购鞋子
tags: [shopping, shoes, online]
---
```

---

## 支出分类

| 大类 | 常见子类 |
|------|---------|
| 居住 | 房租、水电、物业、花呗还款 |
| 餐饮 | 早餐、午餐、晚餐、外卖、零食 |
| 交通 | 地铁、打车、停车费、油费、洗车 |
| 购物 | 日用品、服装、鞋子、电子产品 |
| 通信 | 话费、宽带 |
| 运动 | 羽毛球、健身 |
| 医疗 | 门诊、药品、体检 |
| 教育 | 课程、书籍、培训 |

---

## 工具脚本

### 数据一致性检查

```bash
python scripts/finance_lint.py
```

检查内容：
- `records/` 文件数量与 `index.md` 中 JSON 块数量一致
- 两处 id 列表完全匹配
- 金额合计一致
- wiki 中的链接都指向存在的文件

### OCR 识别

```bash
# 需使用虚拟环境 Python
C:\Users\你的用户名\.workbuddy\binaries\python\envs\default\python.exe scripts/ocr_receipt.py <图片路径>
```

---

## charts.md 切换月份

打开 `wiki/charts.md`，修改顶部 frontmatter 的 `month` 字段即可：

```yaml
---
month: 2026-04    ← 改成想看的月份，留空表示全部
---
```

**Ctrl+S 保存后图表自动刷新。**

---

## 隐私说明

- 所有数据存储在本地，不上传任何服务器
- 付款截图保存在 `raw/receipts/processed/`
- 可选配置 Git 同步到私有仓库

---

## 上传到 GitHub

如果你想将此仓库上传到 GitHub 分享，请注意：

1. **删除或替换私人数据** — 示例数据仅供演示
2. **不要上传收据截图** — 放在 `.gitignore` 中
3. **考虑使用私有仓库** — 如果包含敏感财务信息

**.gitignore 建议内容：**
```
raw/receipts/
.raw/
```

---

*由 LLM 财务助手管理 🖼️💰📊*
