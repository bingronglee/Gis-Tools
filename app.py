import streamlit as st
import pandas as pd
import numpy as np
from scipy.interpolate import griddata, NearestNDInterpolator

# 將 CSV 文件內容存入變數
source_data_csv = """
"序號","經度 (Longitude)","緯度 (Latitude)","高程 (Elevation)"
"1","188296.7706","2503596.8361","16.67"
"2","188273.3722","2503607.5433","16.38"
"3","188268.7322","2503564.7209","16.51"
"4","188307.2595","2503680.3125","16.34"
"""

points_data_csv = """
"序號","經度 (Longitude)","緯度 (Latitude)"
"1","188271.1833","2503600.9952",""
"""

# 設定頁面
st.set_page_config(
    page_title="地理數據插值工具",
    page_icon="🌍",
    layout="wide"
)

# 添加標題和說明
st.title("地理數據插值工具 🌍")
st.markdown("""
    此工具用於地理數據的插值計算。
    
    使用說明：
    1. 選擇插值方法
    2. 執行插值計算並查看結果
""")

# 側邊欄配置
with st.sidebar:
    st.header("設定")
    method = st.selectbox(
        "選擇插值方法",
        ["nearest", "linear", "cubic"],
        help="nearest: 最近鄰插值\nlinear: 線性插值\ncubic: 三次方插值"
    )

# 讀取數據
source_data = pd.read_csv(io.StringIO(source_data_csv))
points_data = pd.read_csv(io.StringIO(points_data_csv))

# 顯示數據預覽
st.subheader("數據預覽")
col1, col2 = st.columns(2)

with col1:
    st.write("原始數據：")
    st.dataframe(source_data.head())
    
with col2:
    st.write("待插值位置：")
    st.dataframe(points_data.head())

# 執行插值計算
if st.button("執行插值計算", type="primary"):
    with st.spinner('計算中...'):
        try:
            # 準備數據
            lons = source_data['經度 (Longitude)'].values
            lats = source_data['緯度 (Latitude)'].values
            elevations = source_data['高程 (Elevation)'].values
            
            lons_new = points_data['經度 (Longitude)'].values
            lats_new = points_data['緯度 (Latitude)'].values
            
            # 執行插值
            if method == "nearest":
                interpolator = NearestNDInterpolator(
                    list(zip(lons, lats)), 
                    elevations
                )
                elevations_new = interpolator(lons_new, lats_new)
            else:
                elevations_new = griddata(
                    (lons, lats),
                    elevations,
                    (lons_new, lats_new),
                    method=method,
                    fill_value=np.nan
                )
            
            # 更新結果
            points_data['高程 (Elevation)'] = elevations_new
            
            # 顯示結果
            st.subheader("計算結果")
            st.dataframe(points_data)
            
            # 提供下載
            csv = points_data.to_csv(index=False)
            st.download_button(
                label="下載結果CSV檔案",
                data=csv,
                file_name="interpolation_result.csv",
                mime="text/csv"
            )
            
        except Exception as e:
            st.error(f'計算過程發生錯誤：{str(e)}')

# 添加頁尾
st.markdown("---")
st.markdown("開發者：秉融 | 版本：1.0.0")
