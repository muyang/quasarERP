# Quasar ERP — 企业资源管理系统

**版本**: 1.0.0  
**基于**: Frappe v15 + ERPNext v15  
**发布日期**: 2026-04-29

---

## 目录

1. [产品简介](#1-产品简介)
2. [系统架构](#2-系统架构)
3. [安装说明](#3-安装说明)
4. [快速开始](#4-快速开始)
5. [功能模块](#5-功能模块)
6. [操作指南](#6-操作指南)
7. [常见问题](#7-常见问题)
8. [技术支持](#8-技术支持)

---

## 1. 产品简介

Quasar ERP 是一款面向中小型制造企业的企业资源管理系统，基于全球领先的开源 ERP 框架 **ERPNext v15** 二次开发。系统覆盖销售、采购、库存、生产、人力资源五大核心业务领域，并针对中国本土化管理需求进行了深度定制。

### 核心特性

| 特性 | 说明 |
|------|------|
| **信用风险管控** | 销售订单自动校验客户信用额度，80%预警、100%拦截，支持特批角色放行 |
| **应付账款预测** | 采购订单提交后自动生成付款计划，按供应商汇总未来 N 天应付预测 |
| **批次全程追溯** | 条码扫描即可追溯物料从采购到生产的完整链路，支持 PDF 导出 |
| **物料齐套检查** | 生产工单提交前自动校验 BOM 物料库存，缺料一键生成采购申请 |
| **请假薪资联动** | 请假审批后自动生成薪资扣款记录，无缝对接薪资计算公式 |

### 适用行业

- 电子元器件制造 · 机械加工与装配 · 食品饮料加工 · 服装纺织 · 一般离散制造业

---

## 2. 系统架构

```
┌─────────────────────────────────────────────────────┐
│                   Nginx (80/443)                     │
│                 反向代理 / 静态文件                    │
└─────────────────────┬───────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────┐
│              Frappe Web (8000)                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐             │
│  │ Quasar   │ │ ERPNext  │ │  hrms    │             │
│  │ 定制模块  │ │ 核心ERP  │ │ 人力资源  │             │
│  └──────────┘ └──────────┘ └──────────┘             │
├─────────────────────────────────────────────────────┤
│  Redis Cache (13000)  │  Redis Queue (11000)         │
│  Socket.IO (9000)     │  Background Workers          │
├─────────────────────────────────────────────────────┤
│               MariaDB 10.11 (3306)                   │
└─────────────────────────────────────────────────────┘
```

**技术栈**: Python 3.12 · Frappe Framework v15 · JavaScript (Frappe UI) · MariaDB 10.11 · Redis 7 · Nginx + Gunicorn

---

## 3. 安装说明

### 3.1 环境要求

| 组件 | 最低版本 | 推荐版本 |
|------|---------|---------|
| 操作系统 | macOS 12 / Windows 10 / Ubuntu 22.04 | macOS 14 / Windows 11 / Ubuntu 24.04 |
| CPU | 2 核 | 4 核+ |
| 内存 | 4 GB | 8 GB+ |
| 磁盘 | 20 GB | 50 GB+ SSD |

### 3.2 macOS 安装

**方式一：一键安装（推荐）**

```bash
# 解压并运行安装脚本
tar xzf quasar-erp-1.0.0-macos.tar.gz
cd quasar-erp-1.0.0
bash deploy/install-macos.sh

# 启动系统
cd ~/quasar-erp
bench start

# 浏览器访问 http://localhost:8000
```

安装脚本自动完成: Homebrew → Python 3.12 + Node 18 → MariaDB + Redis → Frappe Bench → ERPNext + hrms + Quasar → 站点创建

**方式二：Docker 部署**

```bash
# 安装 Docker Desktop 后
tar xzf quasar-erp-1.0.0-macos.tar.gz
cd quasar-erp-1.0.0
docker compose up -d
# 访问 http://localhost
```

### 3.3 Windows 安装

```powershell
# 1. 安装 Docker Desktop: https://www.docker.com/products/docker-desktop/
# 2. 解压 quasar-erp-1.0.0-windows.zip
# 3. 以管理员身份运行 PowerShell
cd quasar-erp-1.0.0
.\deploy\install-windows.ps1
# 4. 访问 http://localhost
```

或使用 WSL2 原生安装: `wsl --install` → 在 Ubuntu 终端中执行 `bash deploy/install-macos.sh`

### 3.4 现有环境安装（插件方式）

```bash
tar xzf quasar-app-1.0.0.tar.gz
cp -r quasar ~/frappe-bench/apps/quasar
cd ~/frappe-bench
bench --site your-site.local install-app quasar
bench build && bench restart
```

---

## 4. 快速开始

### 4.1 首次登录

- 浏览器访问 `http://localhost:8000`
- 默认管理员: **Administrator** / **admin**
- 首次登录后建议立即修改密码：设置 → 我的设置 → 修改密码

### 4.2 基础设置向导

| 步骤 | 菜单路径 | 说明 |
|------|---------|------|
| 1 | 设置 → 公司 | 创建公司信息、币种、时区 |
| 2 | 设置 → 会计科目表 | 导入中国会计科目模板 |
| 3 | 设置 → 仓库 | 创建原材料仓、半成品仓、成品仓 |
| 4 | 采购 → 供应商 | 导入供应商主数据 |
| 5 | 销售 → 客户 | 导入客户主数据，设置信用额度 |
| 6 | 制造 → 物料 | 创建物料主数据 |
| 7 | 制造 → BOM | 创建物料清单 |

---

## 5. 功能模块

### 5.1 销售信用额度控制

**业务流程**：销售订单 → 校验客户信用 →
- 应收账款 < 80% 额度 → 正常提交
- 80% ≤ 应收账款 < 100% → 预警提示，仍可提交
- 应收账款 ≥ 100% → 阻止提交，拥有"超额度审批角色"的用户可确认放行

**设置**: 客户 → 信用额度 / 超额度审批角色（选择可突破额度限制的角色）

### 5.2 采购付款计划

**自动生成**: 采购订单提交后，读取付款条款（Payment Terms），按比例和天数生成分期付款计划

**状态流转**: Pending（待付款）→ Paid（已付款）/ Cancelled（PO取消自动取消）

**应付账款预测报表**: Quasar → 应付账款预测，支持按未来天数、供应商、日期范围筛选，供应商汇总柱状图 + 明细列表，可导出 Excel/CSV

### 5.3 批次追溯看板

**功能**: 输入批次号 / 扫码枪扫描 → 查询 Stock Ledger Entry →

- 🔺 向上追溯（来源，绿色时间线）: 采购收货、外协入库、库存调整
- 🔻 向下追溯（去向，橙色时间线）: 生产工单、委外发料、销售发货

点击凭证号跳转原始单据，支持导出 PDF 追溯报告。

**入口**: Quasar → 批次追溯看板

### 5.4 物料齐套检查

**检查逻辑**: 遍历工单 BOM 物料 → 所需数量 = BOM 需求 - 已调拨量 → 可用库存 = 实际库存 - 已预留量 → 可用 < 所需即记录缺料

**操作流程**: 生产工单提交 → 物料齐全则通过 → 有缺料则阻止提交，自动生成缺料清单 → 在缺料清单上点击"一键生成采购申请"按钮 → 自动创建 Material Request (类型: 采购)

### 5.5 请假薪资扣款

**设置**: HR → Leave Type → 勾选 "Is Deductible" → 设置 "Deduction Rate"（如 100% 事假全额扣、50% 病假半额扣）

**自动流程**: 请假单审批提交 → 检查 Leave Type 可扣款标记 → 自动生成 Extra Deduction（员工、请假单号、天数、扣款比例、归属月份）→ 薪资公式调用 `get_monthly_deduction(employee, month)` 读取扣款总额

**扣款明细报表**: Quasar → 扣款明细，按薪资月份汇总，柱状图展示，支持 Excel 导出

---

## 6. 操作指南

### 6.1 核心业务流程

```
销售订单 → 信用校验 → 发货单 → 应收账款 → 收款单

采购申请 ← 缺料清单 ← 生产工单
   ↓                    ↓
采购订单 → 付款计划    生产领料（批次号）
   ↓                    ↓
采购收货（批次号）     生产完工 → 成品入库

请假单 → 审批提交 → 自动扣款 → 薪资核算
```

### 6.2 角色权限矩阵

| 功能 | 销售员 | 销售经理 | 采购员 | 仓管员 | 生产主管 | HR | 管理员 |
|------|:------:|:------:|:------:|:------:|:------:|:------:|:------:|
| 信用额度设置 | — | ✓ | — | — | — | — | ✓ |
| 超额度审批 | — | ✓ | — | — | — | — | ✓ |
| 批次追溯 | — | ✓ | ✓ | ✓ | ✓ | — | ✓ |
| 缺料清单处理 | — | — | ✓ | — | ✓ | — | ✓ |
| 请假审批 | — | — | — | — | — | ✓ | — |
| 扣款报表 | — | — | — | — | — | ✓ | ✓ |

### 6.3 快捷键

| 快捷键 | 功能 |
|--------|------|
| `Ctrl + S` | 保存当前文档 |
| `Ctrl + Enter` | 提交当前文档 |
| `Ctrl + J` | 全局搜索 |

---

## 7. 常见问题

**Q: 信用额度检查没有触发？**
确认客户已设置信用额度，且 hooks.py 中 doc_events 配置正确，执行了 `bench build`

**Q: 采购订单没有生成付款计划？**
确认采购订单中已配置「付款条款」（Payment Terms），条款中包含分期计划

**Q: 批次追溯查不到数据？**
确认物料启用了批次管理（Has Batch No = Yes），且收货时录入了批次号

**Q: 请假扣款没有自动生成？**
确认 hrms 已安装，Leave Type 的 custom_is_deductible 已勾选，请假单已审批提交

**Q: 性能优化**
- 大报表查询慢 → 缩小日期范围筛选
- 页面加载慢 → `bench clear-cache`
- 数据库 → 调整 innodb_buffer_pool_size（建议物理内存 50%）

---

## 8. 技术支持

### 日常运维命令

```bash
bench --site erp.local backup --with-files    # 数据备份
bench --site erp.local migrate && bench build  # 应用更新
bench restart                                  # 重启服务
bench clear-cache                             # 清理缓存
```

### 定时备份（crontab）

```
0 2 * * * cd ~/quasar-erp && bench --site erp.local backup --with-files
```

### 升级步骤

```bash
# 1. 备份 → 2. 拉取代码 → 3. 迁移 → 4. 构建 → 5. 重启
bench --site erp.local backup --with-files
cd apps/quasar && git pull && cd ../..
bench --site erp.local migrate
bench build
bench restart
```

---

**© 2026 Quasar Team. All rights reserved.**  
*基于 ERPNext v15 构建 | Frappe Framework v15*
