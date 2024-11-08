import streamlit as st
import pandas as pd
import numpy as np
from scipy.interpolate import griddata, NearestNDInterpolator

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
    2. 上傳原始數據CSV檔案（需包含：經度、緯度、高程）
    3. 上傳待插值位置CSV檔案
    4. 點擊計算按鈕
""")

# 側邊欄配置
with st.sidebar:
    st.header("設定")
    method = st.selectbox(
        "選擇插值方法",
        ["nearest", "linear", "cubic"],
        help="nearest: 最近鄰插值\nlinear: 線性插值\ncubic: 三次方插值"
    )

# 主要內容
col1, col2 = st.columns(2)

with col1:
    st.subheader("上傳原始數據")
    source_file = st.file_uploader(
        "選擇包含原始數據的CSV檔案",
        type=['csv'],
        help="檔案須包含：經度 (Longitude)、緯度 (Latitude)、高程 (Elevation)"
    )

with col2:
    st.subheader("上傳待插值位置")
    points_file = st.file_uploader(
        "選擇包含待插值位置的CSV檔案",
        type=['csv'],
        help="檔案須包含：經度 (Longitude)、緯度 (Latitude)"
    )

if source_file is not None and points_file is not None:
    try:
        # 讀取數據
        source_data = pd.read_csv(source_file)
        points_data = pd.read_csv(points_file)
        
        # 顯示數據預覽
        st.subheader("數據預覽")
        col3, col4 = st.columns(2)
        
        with col3:
            st.write("原始數據：")
            st.dataframe(source_data.head())
            
        with col4:
            st.write("待插值位置：")
            st.dataframe(points_data.head())
        
        # 添加計算按鈕
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
            
    except Exception as e:
        st.error(f'讀取檔案時發生錯誤：{str(e)}')

# 添加頁尾
st.markdown("---")
st.markdown("開發者：秉融 | 版本：1.0.0")
