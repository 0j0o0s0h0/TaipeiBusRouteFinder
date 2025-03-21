import requests
import streamlit as st
import pandas as pd

# ===== 設定 TDX API =====
CLIENT_ID = "11131234-647af4aa-bb07-47c5"
CLIENT_SECRET = "5c28860a-edb3-421e-bf9d-86d245780e9c"

# 取得 Access Token
token_url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
data = {
    "grant_type": "client_credentials",
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET
}
headers = {"Content-Type": "application/x-www-form-urlencoded"}
response = requests.post(token_url, data=data, headers=headers)
access_token = response.json().get("access_token")

# API Header
api_headers = {"Authorization": f"Bearer {access_token}"}

# 取得台北市公車路線與站點
url_RouteOfStop = "https://tdx.transportdata.tw/api/basic/v2/Bus/StopOfRoute/City/Taipei?%24format=JSON"
response_StopOfRoute = requests.get(url_RouteOfStop, headers=api_headers)
stop_of_route_data = response_StopOfRoute.json()

 #🚨 新增錯誤檢查
try:
    stop_of_route_data = response_StopOfRoute.json()  # 解析 JSON
    if not isinstance(stop_of_route_data, list):  # 確保是列表
        raise ValueError("API 回應格式錯誤！")
except Exception as e:
    st.error(f"❌ 無法獲取公車路線資料，請稍後再試。\n錯誤訊息：{e}")
    st.stop()


# ===== 整理站點與路線資料 =====
route_data = []
stop_to_id = {}

for route in stop_of_route_data:
    RouteID = route["RouteID"]
    RouteName_Zh_tw = route["RouteName"]["Zh_tw"]
    
    Stops = []
    for stop in route["Stops"]:
        StopID = stop["StopID"]
        StopName_Zh_tw = stop["StopName"]["Zh_tw"]
        
        Stops.append({"StopID": StopID, "StopName_Zh_tw": StopName_Zh_tw})
        stop_to_id.setdefault(StopName_Zh_tw, []).append(StopID)

    route_data.append({"RouteID": RouteID, "RouteName_Zh_tw": RouteName_Zh_tw, "Stops": Stops})

# ===== Streamlit UI =====
st.title("🚌 公車路線查詢系統")
st.markdown("輸入 **起點 & 終點站名**，查詢可以搭乘的公車路線！")

# UI 設計
col1, col2 = st.columns(2)
#start_stop_name = col1.text_input("🔵 輸入起點站")
#end_stop_name = col2.text_input("🔴 輸入終點站")

# 建立站點選單
all_stops = sorted(stop_to_id.keys())  # 取得所有站名並排序

# 用 selectbox 讓使用者選擇站點
start_stop_name = col1.selectbox("🔵 選擇起點站", all_stops)
end_stop_name = col2.selectbox("🔴 選擇終點站", all_stops)

# 查詢邏輯
if start_stop_name and end_stop_name:
    start_stop_ids = stop_to_id.get(start_stop_name, [])
    end_stop_ids = stop_to_id.get(end_stop_name, [])

    if not start_stop_ids or not end_stop_ids:
        st.error("❌ 找不到站點，請檢查輸入是否正確！")
    else:
        valid_routes = set()
        for route in route_data:
            stop_ids = {stop["StopID"] for stop in route["Stops"]}
            if any(sid in stop_ids for sid in start_stop_ids) and any(eid in stop_ids for eid in end_stop_ids):
                valid_routes.add(route["RouteName_Zh_tw"])

        if valid_routes:
            st.success(f"✅ 可搭乘的公車路線：\n{', '.join(valid_routes)}")
        else:
            st.warning("⚠️ 沒有找到同時經過這兩站的公車路線。")
