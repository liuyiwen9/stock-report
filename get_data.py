import requests
import pandas as pd
from datetime import datetime
import sys

def get_ef_sector_fund_flow(sector_type: str):
    print(f"正在获取{sector_type}数据...")
    if sector_type == "行业板块":
        fs_param = "m:90+t:2"
    else:
        fs_param = "m:90+t:3"
    
    url = "https://push2.eastmoney.com/api/qt/clist/get"
    params = {
        "pn": "1",
        "pz": "500",
        "po": "1",
        "np": "1",
        "ut": "bd1d9ddb04089700cf9c27f6f7426281",
        "fltt": "2",
        "invt": "2",
        "fid": "f62",
        "fs": fs_param,
        "fields": "f12,f14,f2,f3,f62,f184,f66,f69,f72,f75,f78,f81,f84,f87,f204,f205",
    }
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        print(f"请求失败: {e}")
        return None, f"请求失败: {e}"
    
    data = resp.json()
    print(f"接口返回状态码: {resp.status_code}")
    
    if data.get("data") is None or data["data"].get("diff") is None:
        print(f"警告: {sector_type}数据为空，可能是非交易日")
        return None, "今日非交易日或数据暂未更新"
    
    items = data["data"]["diff"]
    if not items:
        print(f"警告: {sector_type}列表为空")
        return None, "板块列表为空"
    
    df = pd.DataFrame(items)
    col_map = {
        "f12": "代码", "f14": "名称", "f2": "最新价", "f3": "涨跌幅",
        "f62": "主力净流入", "f184": "超大单净流入", "f66": "大单净流入",
        "f69": "中单净流入", "f72": "小单净流入", "f204": "成交额",
    }
    # 只保留存在的列
    existing_cols = [c for c in col_map.keys() if c in df.columns]
    df = df[existing_cols].rename(columns={k: col_map[k] for k in existing_cols})
    
    # 转换金额为亿
    money_cols = ["主力净流入", "超大单净流入", "大单净流入", "中单净流入", "小单净流入", "成交额"]
    for col in money_cols:
        if col in df.columns:
            df[col] = (df[col].astype(float) / 1e8).round(2)
    
    if "涨跌幅" in df.columns:
        df["涨跌幅"] = df["涨跌幅"].astype(float)
        # 东方财富的涨跌幅可能是乘以100后的值（如2.5表示2.5%），需要判断
        if df["涨跌幅"].max() > 10:
            df["涨跌幅"] = (df["涨跌幅"] / 100).round(2)
    
    if "主力净流入" in df.columns and "成交额" in df.columns:
        df["主力净流入占比"] = (df["主力净流入"] / df["成交额"] * 100).round(2)
    
    # 排序
    df = df.sort_values("主力净流入", ascending=False)
    
    # 选前10，只展示关键列
    display_cols = ["名称", "主力净流入", "超大单净流入", "大单净流入", "主力净流入占比", "涨跌幅"]
    available = [c for c in display_cols if c in df.columns]
    print(f"成功获取{sector_type}数据，共{len(df)}条")
    return df[available].head(10), None

def build_html():
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    ind_df, ind_error = get_ef_sector_fund_flow("行业板块")
    con_df, con_error = get_ef_sector_fund_flow("概念板块")
    
    # 生成行业板块表格
    if ind_error:
        ind_html = f"<p style='color:red;'>行业板块数据获取失败：{ind_error}</p>"
    else:
        ind_html = ind_df.to_html(index=False, classes="table", escape=False)
    
    # 生成概念板块表格
    if con_error:
        con_html = f"<p style='color:red;'>概念板块数据获取失败：{con_error}</p>"
    else:
        con_html = con_df.to_html(index=False, classes="table", escape=False)
    
    # 研判提示（如果有数据）
    note = ""
    if ind_df is not None and len(ind_df) > 0:
        top_name = ind_df.iloc[0]["名称"]
        top_money = ind_df.iloc[0]["主力净流入"]
        note = f"<p><b>研判提示：</b>主力净流入金额最大行业为 <b>{top_name}</b>（{top_money:.2f} 亿），"
        if "主力净流入占比" in ind_df.columns:
            note += f"主力净流入占比 {ind_df.iloc[0]['主力净流入占比']}%，"
        note += "日内强势。超大单与涨跌幅协同情况请查看表格。</p>"
    
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
<p>数据来源：东方财富 | 自动生成</p>
</div>
</body>
</html>"""
    return html

if __name__ == "__main__":
    try:
        page = build_html()
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(page)
        print("报告已生成 -> index.html")
    except Exception as e:
        print(f"生成报告失败: {e}")
        sys.exit(1)
