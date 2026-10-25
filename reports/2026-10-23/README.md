# 全球市场研究与10月26日条件仓位方案

先打开 `global_market_positioning_20261026.html`。这是自包含报告，含15章、38条来源、三个股票模型、三个ETF模型、A/B/C周一起始候选、个股卡片和资金/压力演算。

正式行情统计截至2026-10-22纽约收盘。2026-10-23盘中日线已从统计中剔除；本报告不是周五收盘后的更新。

模型是条件研究方案。当前账户、风险承受、比赛资格、WLS、现金与证券规则仍未核验。不能直接作为合法比赛买单或保证回撤。

## 文件

- `allocation_models.csv`：目标和周一起始比例，可在Excel中查看。CSV不是可提交订单。
- `market_metrics.csv`：48个证券趋势与风险统计。
- `analysis.json`：权重、协方差结果、相关性与完整压力向量。
- `market_raw.json`、`stock_raw.json`、`stock_quotes.json`：本次读取的行情。
- `sources.json`：官方资料和来源边界。
- `validation.json`：数值和视觉核查记录。

## 重算

使用安装有numpy和pandas的Python：

```powershell
python analyze.py
python build_report.py
python validate.py
```

重算读取的是本次保存数据，不自动联网刷新。完整日线过滤上限固定为2026-10-23，更新日期时需要同步修改、重新核验事件和证据，并重新检查结果。现金收益与费用按0；历史组合风险为加权对数收益近似，非精确净值路径。
