import requests
import pandas as pd
from datetime import datetime

def get_ef_sector_fund_flow(sector_type: str):
    if sector_type == "行业板块":
        url = "https://push2.eastmoney.com/api/qt/clist/get"
        params = {
            "pn": "1", "pz": "500", "po": "1", "np": "1",
            "ut": "bd1d9ddb04089700cf9c27f6f7426281",
            "fltt": "2", "invt": "2",
            "fid": "f62",
            "fs": "m:90+t:2",
            "fields": "f12,f14,f2,f3,f62,f184,f66,f69,f72,f75,f78,f81,f84,f87,f204,f205",
        }
    else:
        url = "https://push2.eastmoney.com/api/qt/clist/get"
        params = {
            "pn": "1", "pz": "500", "po": "1", "np": "1",
            "ut": "bd1d9ddb04089700cf9c27f6f7426281",
            "fltt": "2", "invt": "2",
            "fid": "f62",
            "fs": "m:90+t:3",
            "fields": "f12,f14,f2,f3,f62,f184,f66,f69,f72,f75,f78,f81,f84,f87,f204,f205",
        }
    resp = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
    data = resp.json()
    items = data["data"]["diff"]
    df = pd.DataFrame(items)
    col_map = {
        "f12": "代码", "f14": "名称", "f2": "最新价", "f3": "涨跌幅",
        "f62": "主力净流入", "f184": "超大单净流入", "f66": "大单净流入",
        "f69": "中单净流入", "f72": "小单净流入", "f204": "成交额",
    }
    df = df[list(col_map.keys())].rename(columns=col_map)
    for col in ["主力净流入", "超大单净流入", "大单净流入", "中单净流入", "小单净流入", "成交额"]:
        df[col] = (df[col] / 1e8).round(2)
    df["涨跌幅"] = (df["涨跌幅"] / 100).round(2) if df["涨跌幅"].max() > 10 else df["涨跌幅"].round(2)
    df["主力净流入占比"] = (df["主力净流入"] / df["成交额"] * 100).round(2)
    df = df.sort_values("主力净流入", ascending=False)
    return df[["名称", "主力净流入", "超大单净流入", "大单净流入", "主力净流入占比", "涨跌幅"]].head(10)

def build_html():
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    ind = get_ef_sector_fund_flow("行业板块")
    con = get_ef_sector_fund_flow("概念板块")
    ind_html = ind.to_html(index=False, classes="table", escape=False)
    con_html = con.to_html(index=False, classes="table", escape=False)
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
<p><b>研判提示：</b>主力净流入金额最大行业为 <b>{ind.iloc[0]['名称']}</b>（{ind.iloc[0]['主力净流入']:.2f} 亿），
主力净流入占比 {ind.iloc[0]['主力净流入占比']}%，日内强势。超大单与涨跌幅协同情况请查看表格。</p>
<p>数据来源：东方财富 | 自动生成</p>
</div>
</body>
</html>"""
    return html

if __name__ == "__main__":
    page = build_html()
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(page)
    print("报告已生成 -> index.html")
