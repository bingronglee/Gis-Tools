import streamlit as st
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, Polygon
import ezdxf
import os
from scipy.spatial import cKDTree
import numpy as np
import requests
from io import BytesIO

# Google Drive文件ID映射
REGION_DRIVE_MAP = {
    '台中': "1Zufv-suZeXdbmrDSLyRBAXWAN2TRM9Yw",
    '台南': "1Zufv-suZeXdbmrDSLyRBAXWAN2TRM9Yw",
    '高雄': "1Zufv-suZeXdbmrDSLyRBAXWAN2TRM9Yw",
    '雲林': "1Zufv-suZeXdbmrDSLyRBAXWAN2TRM9Yw"
}

def load_csv_from_drive(file_id):
    url = f"https://drive.google.com/uc?id={file_id}"
    response = requests.get(url)
    return pd.read_csv(BytesIO(response.content))

def analyze_dxf(dxf_file, csv_data):
    # 讀取DXF檔案並轉換為多邊形範圍
    dxf_doc = ezdxf.read(BytesIO(dxf_file))
    msp = dxf_doc.modelspace()
    polygons = []
    for entity in msp.query("LWPOLYLINE"):
        points = [(p[0], p[1]) for p in entity]
        polygons.append(Polygon(points))

    dxf_gdf = gpd.GeoDataFrame(geometry=polygons)

    # 轉換CSV數據為GeoDataFrame
    csv_data['geometry'] = csv_data.apply(lambda row: Point((float(row['X']), float(row['Y']))), axis=1)
    gdf_csv = gpd.GeoDataFrame(csv_data, geometry='geometry')

    # 進行空間交集分析
    intersection = gpd.sjoin(gdf_csv, dxf_gdf, how='inner', predicate='intersects')

    # 提取座標點
    coords = np.array([(geom.x, geom.y) for geom in intersection.geometry])

    # 使用KDTree找出鄰近點
    tree = cKDTree(coords)
    groups = tree.query_ball_tree(tree, r=0.17)

    # 創建點到組的映射
    point_to_group = {}
    for i, group in enumerate(groups):
        for point in group:
            if point not in point_to_group:
                point_to_group[point] = i

    # 添加組信息
    intersection['group'] = [point_to_group[i] for i in range(len(intersection))]
    grouped = intersection.groupby('group').size().reset_index(name='count')

    # 計算各類型建築的統計
    num_houses = int(grouped[grouped['count'] == 1]['count'].sum())
    num_house_buildings = int(grouped[grouped['count'] == 1].shape[0])

    num_apartments = int(grouped[(grouped['count'] >= 2) & (grouped['count'] <= 6)]['count'].sum())
    num_apartment_buildings = int(grouped[(grouped['count'] >= 2) & (grouped['count'] <= 6)].shape[0])

    num_buildings = int(grouped[grouped['count'] >= 7]['count'].sum())
    num_building_structures = int(grouped[grouped['count'] >= 7].shape[0])

    total_houses = num_houses + num_apartments + num_buildings
    total_buildings = num_house_buildings + num_apartment_buildings + num_building_structures

    # 生成含有點位的新DXF
    for idx, row in intersection.iterrows():
        point = row['geometry']
        group_id = row['group']
        count = grouped[grouped['group'] == group_id]['count'].values[0]
        if count == 1:
            color = 7  # 白色
        elif 2 <= count <= 6:
            color = 30  # 橘色
        else:
            color = 3  # 綠色
        msp.add_circle((point.x, point.y), radius=0.5, dxfattribs={'color': color})

    # 將修改後的DXF轉換為bytes
    output = BytesIO()
    dxf_doc.save(output)
    output.seek(0)

    return {
        'num_houses': num_houses,
        'num_house_buildings': num_house_buildings,
        'num_apartments': num_apartments,
        'num_apartment_buildings': num_apartment_buildings,
        'num_buildings': num_buildings,
        'num_building_structures': num_building_structures,
        'total_houses': total_houses,
        'total_buildings': total_buildings
    }, output

def main():
    st.title('建築物分析系統')

    # 選擇地區
    region = st.selectbox('請選擇地區:', list(REGION_DRIVE_MAP.keys()))

    # 上傳DXF文件
    uploaded_file = st.file_uploader("上傳DXF文件", type=['dxf'])

    if uploaded_file is not None:
        # 讀取選定地區的CSV數據
        try:
            csv_data = load_csv_from_drive(REGION_DRIVE_MAP[region])
        except Exception as e:
            st.error(f'無法讀取CSV數據: {str(e)}')
            return

        # 分析數據
        try:
            result, output_dxf = analyze_dxf(uploaded_file.read(), csv_data)

            # 顯示結果
            col1, col2 = st.columns(2)
            with col1:
                st.write("### 透天")
                st.write(f"戶數: {result['num_houses']}")
                st.write(f"棟數: {result['num_house_buildings']}")

                st.write("### 公寓")
                st.write(f"戶數: {result['num_apartments']}")
                st.write(f"棟數: {result['num_apartment_buildings']}")

            with col2:
                st.write("### 大樓")
                st.write(f"戶數: {result['num_buildings']}")
                st.write(f"棟數: {result['num_building_structures']}")

                st.write("### 總計")
                st.write(f"總戶數: {result['total_houses']}")
                st.write(f"總棟數: {result['total_buildings']}")

            # 提供下載修改後的DXF文件
            st.download_button(
                label="下載分析後的DXF文件",
                data=output_dxf,
                file_name="analyzed_output.dxf",
                mime="application/dxf"
            )

        except Exception as e:
            st.error(f'分析過程中發生錯誤: {str(e)}')

if __name__ == '__main__':
    main()
