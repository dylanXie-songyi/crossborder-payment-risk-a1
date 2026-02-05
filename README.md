# Cross-Border Payment Authorization Monitoring 
## 结构
crossborder-payment-risk-a1/
├── README.md
├── notebooks/
│   └── payment_auth_analysis.ipynb
├── dataset/
│   └── payment_auth_data.csv
├── dashboard/
│   ├── auth_rate_trend.png
│   ├── country_payment_heatmap.png
│   └── decline_code_dist.png
└── risk_strategy.md
## 项目背景
在跨境电商业务中，支付授权成功率（Auth Rate）直接影响订单转化与 GMV。
由于不同国家的银行体系、支付方式以及风控规则存在显著差异，
支付成功率在不同国家和支付渠道之间往往表现不一致，并且更容易出现波动。

本 Case 以支付授权成功率（Auth Rate）为核心指标，
构建一套跨境支付链路监控分析框架，
用于识别支付成功率异常波动，并辅助支付与风控策略决策。

## 项目内容与目标
- 识别支付授权成功率（Auth Rate）的异常波动
- 从国家、支付方式及支付服务商（PSP）维度拆解成功率变化来源
- 判断异常波动更可能源于系统/通道问题，还是潜在的风险或欺诈信号

## 数据说明
- 使用 Kaggle 上的跨境支付授权日志数据：
https://www.kaggle.com/datasets/dylanxie1/cross-border-payment-authorization-logs

## 项目产出
- 支付授权监控与分析结果可视化（`dashboard`）
- 支付与风控策略建议总结文档（`risk_strategy.md`）
