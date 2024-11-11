import streamlit as st

# 應用標題
st.title("簡單 CSV 文件處理應用")

# 文件上傳
uploaded_file = st.file_uploader("上傳 CSV 文件", type="csv")

if uploaded_file:
    # 讀取並顯示文件內容
    st.subheader("文件內容")
    lines = uploaded_file.getvalue().decode("utf-8").splitlines()
    data = [line.split(",") for line in lines]
    
    # 顯示表格
    st.table(data[:10])  # 僅顯示前 10 行

    # 簡單統計：計算行數與列數
    num_rows = len(data) - 1  # 減去表頭
    num_cols = len(data[0])
    st.write(f"行數（不含表頭）：{num_rows}")
    st.write(f"列數：{num_cols}")

    # 列選擇與數據處理
    st.subheader("選擇列進行處理")
    if num_cols > 0:
        # 獲取列標題
        column_names = data[0]
        selected_column = st.selectbox("選擇列", column_names)

        # 查找列索引
        col_index = column_names.index(selected_column)
        
        # 提取該列的數據（跳過表頭）
        column_data = [row[col_index] for row in data[1:]]
        
        # 簡單數值處理
        try:
            column_values = [float(value) for value in column_data]
            st.write(f"列 '{selected_column}' 的統計數據：")
            st.write(f"- 最大值：{max(column_values)}")
            st.write(f"- 最小值：{min(column_values)}")
            st.write(f"- 平均值：{sum(column_values) / len(column_values):.2f}")
        except ValueError:
            st.error(f"列 '{selected_column}' 包含非數字數據，無法計算統計數據。")
