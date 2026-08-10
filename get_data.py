import akshare as ak
import pandas as pd
from datetime import datetime
import sys

def get_sector_fund_flow(sector_type: str):
    """获取行业或概念板块资金流前10"""
    try:
        # akshare 直接返回 DataFrame，字段包含中文
        if sector_type == "行业板块":
            df = ak.stock_sector_fund_flow_rank(indicator="今日", sector_type="行业板块")
        else:
            df = ak.stock_sector_fund_flow_rank(indicator="今日", sector_type="概念板块")
    except Exception as e:
        print(f"获取{sector_type}数据失败: {e}")
        return None, f"接口调用失败: {e}"

    if df is None or df.empty:
        print(f"警告: {sector_type}数据为空，可能非交易日")
        return None, "今日非交易日或数据暂未更新"

    # 确保需要的列存在
    required_cols = ["名称", "主力净流入", "超大单净流入", "大单净流入", "成交额", "涨跌幅"]
    missing = set(required_cols) - set(df.columns)
    if missing:
        print(f"缺少字段: {missing}")
        return None, f"缺少字段: {missing}"

    # 只保留需要展示的列，并按主力净流入降序排序
    df = df[required_cols].copy()
    df = df.sort_values("主力净流入", ascending=False)

    # 计算主力净流入占比（%）
    df["主力净流入占比"] = (df["主力净流入"] / df["成交额"] * 100).round(2)

    # 取前10
    top10 = df.head(10)
    # 按展示顺序重排列
    display = top10[["名称", "主力净流入", "超大单净流入", "大单净流入", "主力净流入占比", "涨跌幅"]]
    print(f"成功获取{sector_type}前10")
    return display, None

def build_html():
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    ind_df, ind_err = get_sector_fund_flow("行业板块")
    con_df, con_err = get_sector_fund_flow("概念板块")

    # 生成表格或错误信息
    ind_html = f"<p style='color:red;'>❌ 行业板块：{ind_err}</p>" if ind_err else ind_df.to_html(index=False, classes="table", escape=False)
    con_html = f"<p style='color:red;'>❌ 概念板块：{con_err}</p>" if con_err else con_df.to_html(index=False, classes="table", escape=False)

    # 研判提示
    note = ""
    if ind_df is not None and len(ind_df) > 0:
        top_name = ind_df.iloc[0]["名称"]
        top_money = ind_df.iloc[0]["主力净流入"]
        top_pct = ind_df.iloc[0]["主力净流入占比"]
        note = f"<p><b>研判提示：</b>主力净流入金额最大行业为 <b>{top_name}</b>（{top_money:.2f} 亿），占比 {top_pct}%，日内表现强势，请关注明日量能配合情况。</p>"

    html = f"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<title>A股板块资金日报 {now_str}</title>
<style>
  body {{ font-family: 'Microsoft YaHei', sans-serif; margin: 30px; }}
  h1 {{ color: #333; }}
  .table {{ border-collapse: collapse; width: 100%; margin-bottom: 30px; }}
  .table th, .table td {{ border: 1px solid #ddd; padding: 8px; text-align: center; }}
  .table th {{ background-color: #4CAF50; color: white; }}
  tr:nth-child(even) {{ background-color: #f2f2f2; }}
  .note {{ color: #666; margin-top: 20px; }}
</style>
</head>
<body>
<h1>📊 A股板块资金流向监控</h1>
<p>更新时间：{now_str} （每个交易日 14:30 自动更新）</p>
<h2>🔥 行业板块主力净流入 Top 10</h2>
{ind_html}
<h2>💡 概念板块主力净流入 Top 10</h2>
{con_html}
<div class="note">
{note}
<p>数据来源：东方财富（通过 akshare） | 自动生成</p>
</div>
</body>
</html>"""
    return html

if __name__ == "__main__":
    try:
        page = build_html()
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(page)
        print("✅ 报告已生成 -> index.html")
    except Exception as e:
        print(f"❌ 生成报告失败: {e}")
        sys.exit(1)
