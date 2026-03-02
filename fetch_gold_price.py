import os
import json
import datetime
import requests

DATA_FILE = 'gold_price_trend.json'

def get_today_gold_data():
    api_key = os.environ.get("GOLD_API_KEY")
    if not api_key:
        print("❌ 未找到 GOLD_API_KEY，请检查 GitHub Secrets 配置。")
        return None

    url = 'http://web.juhe.cn/finance/gold/shgold'
    params = {
        'key': api_key,
        'v': '1'
    }

    try:
        print("正在请求聚合数据 (上海黄金交易所) API...")
        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if str(data.get("error_code")) == "0":
            results = data.get("result", [])
            # 聚合数据的 result 通常是一个列表，里面包含了一个包含所有品种的大字典
            if isinstance(results, list) and len(results) > 0:
                print("✅ 成功获取完整的大盘行情数据！")
                return results[0] # 返回这个包含了 Au99.99, Ag99.99 等所有字典的集合
            
            print("❌ 数据结构不符合预期，未能提取到完整数据。")
            return None
        else:
            print(f"❌ API 请求失败，错误码: {data.get('error_code')}，原因: {data.get('reason')}")
            return None

    except Exception as e:
        print(f"❌ 网络请求或解析异常: {e}")
        return None

def main():
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    today_data = get_today_gold_data()
    
    if today_data is None:
        print("获取行情失败，今日数据不更新。")
        return

    # 读取已有数据
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            try:
                trend_data = json.load(f)
            except json.JSONDecodeError:
                trend_data = []
    else:
        trend_data = []

    # 检查今天是否已经更新过
    if len(trend_data) > 0 and trend_data[-1]['date'] == today_str:
        print("今日数据已存在，更新最新行情。")
        trend_data[-1]['data'] = today_data
    else:
        # 新的数据结构：包含 date 和完整的 data
        trend_data.append({
            "date": today_str,
            "data": today_data
        })

    # 依然保留最近 180 天的数据
    if len(trend_data) > 180:
        trend_data = trend_data[-180:]

    # 写回 JSON 文件
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(trend_data, f, ensure_ascii=False, indent=2)
    print("✅ 真实原始大盘数据保存成功！")

if __name__ == "__main__":
    main()
