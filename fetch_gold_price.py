import os
import json
import datetime
import requests

DATA_FILE = 'gold_price_trend.json'

def get_today_gold_price():
    # 1. 从 GitHub Secrets 中安全读取 API Key
    api_key = os.environ.get("GOLD_API_KEY")
    if not api_key:
        print("❌ 未找到 GOLD_API_KEY，请检查 GitHub Secrets 配置。")
        return None

    # 2. 配置真实 API 地址
    # ⚠️ 注意：这里以“极速数据”的品牌黄金接口为例。
    # 如果你用的是聚合数据或其他平台，请根据官方文档替换 URL 和解析逻辑！
    url = f"http://web.juhe.cn/finance/gold/shgold?key={api_key}"

    try:
        print("正在请求真实黄金 API...")
        response = requests.get(url, timeout=10)
        data = response.json()

        # 3. 解析 JSON 数据 (以下逻辑需根据你实际使用的 API 文档调整)
        if data.get("status") == 0 or data.get("msg") == "ok":
            brand_list = data.get("result", [])
            
            # 遍历寻找你需要的品牌，比如“周大福”
            for item in brand_list:
                if item.get("brand") == "周大福":
                    # 获取最新报价（通常是个字符串，需要转成浮点数）
                    price_str = item.get("price")
                    print(f"✅ 成功获取周大福金价: {price_str} 元/克")
                    return float(price_str)
            
            print("❌ 在返回数据中没有找到指定的品牌。")
            return None
        else:
            print(f"❌ API 请求失败，服务商返回: {data.get('msg')}")
            return None

    except Exception as e:
        print(f"❌ 网络请求异常: {e}")
        return None

def main():
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    today_price = get_today_gold_price()
    
    if today_price is None:
        print("获取金价失败，今日数据不更新。")
        return

    # 读取已有的历史数据
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
    print("✅ 真实数据保存成功！")

if __name__ == "__main__":
    main()
