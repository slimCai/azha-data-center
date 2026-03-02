import os
import json
import datetime
import requests

DATA_FILE = 'gold_price_trend.json'

def get_today_gold_price():
    # 1. 从 GitHub Secrets 获取 API Key
    api_key = os.environ.get("GOLD_API_KEY")
    if not api_key:
        print("❌ 未找到 GOLD_API_KEY，请检查 GitHub Secrets 配置。")
        return None

    # 2. 聚合数据 - 上海黄金交易所接口
    url = 'http://web.juhe.cn/finance/gold/shgold'
    params = {
        'key': api_key,
        'v': '1'  # 保持官方参数格式
    }

    try:
        print("正在请求聚合数据 (上海黄金交易所) API...")
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        # 将接口返回的原始数据完整打印出来，方便在 GitHub Actions 日志中排查问题
        print("API 原始返回数据:", json.dumps(data, ensure_ascii=False))

        # 3. 聚合数据的成功状态码是 error_code == 0
        if str(data.get("error_code")) == "0":
            # 获取结果列表
            results = data.get("result", [])
            
            # 聚合数据的结构有时嵌套在一层列表中，有时嵌套在字典中
            # 我们直接提取 "Au99.99" (纯度 99.99% 的黄金) 的最新报价
            if isinstance(results, list) and len(results) > 0:
                first_item = results[0]
                
                # 遍历寻找 Au99.99
                items_to_search = first_item.values() if isinstance(first_item, dict) else results
                
                for item in items_to_search:
                    if isinstance(item, dict):
                        # 获取品种名称
                        variety = item.get("variety", "")
                        if variety == "Au99.99" or "Au99.99" in variety:
                            # 获取最新价
                            latest_price = item.get("latestpri")
                            print(f"✅ 成功获取 {variety} 最新大盘金价: {latest_price} 元/克")
                            return float(latest_price)
            
            print("❌ 没有在返回数据中找到 Au99.99 的价格，请检查上方打印的原始数据格式。")
            return None
        else:
            print(f"❌ API 请求失败，错误码: {data.get('error_code')}，原因: {data.get('reason')}")
            return None

    except Exception as e:
        print(f"❌ 网络请求或解析异常: {e}")
        return None

def main():
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    today_price = get_today_gold_price()
    
    if today_price is None:
        print("获取金价失败，今日数据不更新。")
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
        print("今日数据已存在，更新最新价格。")
        trend_data[-1]['price'] = today_price
    else:
        trend_data.append({
            "date": today_str,
            "price": today_price
        })

    # 保留最近 180 天的数据
    if len(trend_data) > 180:
        trend_data = trend_data[-180:]

    # 写回 JSON 文件
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(trend_data, f, ensure_ascii=False, indent=2)
    print("✅ 真实大盘金价数据保存成功！")

if __name__ == "__main__":
    main()
