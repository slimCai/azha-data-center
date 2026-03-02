import json
import os
import datetime
import requests

# 1. 设定数据保存的文件路径
DATA_FILE = 'gold_price_trend.json'

def get_today_gold_price():
    """
    这里是你获取金价的核心逻辑。
    为了演示，这里留出了调用 API 的位置。
    国内常用的免费/试用 API 如：聚合数据、RollToolsApi 等。
    """
    # 假设你使用的是某个 API（伪代码）
    # api_url = "https://api.example.com/gold?app_id=YOUR_ID&app_secret=YOUR_SECRET"
    # response = requests.get(api_url).json()
    # current_price = response['data']['price']
    
    # 作为第一步跑通流程，我们先用一个模拟的随机价格（或者你可以自己写爬虫抓取金投网）
    import random
    current_price = round(random.uniform(480.0, 520.0), 2) 
    
    return current_price

def main():
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    today_price = get_today_gold_price()
    
    print(f"获取到今日 ({today_str}) 金价: {today_price}")

    # 2. 读取已有的历史数据（如果存在）
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            try:
                trend_data = json.load(f)
            except json.JSONDecodeError:
                trend_data = []
    else:
        trend_data = []

    # 3. 检查今天是否已经更新过，避免重复添加
    if len(trend_data) > 0 and trend_data[-1]['date'] == today_str:
        print("今日数据已存在，更新价格。")
        trend_data[-1]['price'] = today_price
    else:
        trend_data.append({
            "date": today_str,
            "price": today_price
        })

    # 限制数据长度，比如只保留最近 180 天的数据，避免文件过大
    if len(trend_data) > 180:
        trend_data = trend_data[-180:]

    # 4. 将更新后的数据写回 JSON 文件
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(trend_data, f, ensure_ascii=False, indent=2)
    print("数据保存成功！")

if __name__ == "__main__":
    main()
