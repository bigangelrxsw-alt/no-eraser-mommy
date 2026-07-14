import streamlit as st
import cv2
import numpy as np
import zipfile
import os
import time

st.set_page_config(page_title="唔使媽咪擦 NoEraserMommy", layout="centered")
st.title("📝 唔使媽咪擦 NoEraserMommy")
st.title("批量試卷去筆跡工具 (100% 永久免費)")
st.write("上傳帶有手寫答案、批改符號的工作紙，一鍵批量導出乾淨的空白題目卷！")

# 1. 側邊欄：第一個廣告位/聯盟行銷位
st.sidebar.markdown("### 📢 本週家長推薦 (聯盟推廣)")
st.sidebar.markdown(
    """
    <div style="background-color:#fff3cd; padding:15px; border-radius:8px; border-left:5px solid #ffc107;">
        <h4>🖨️ 推薦家用高效能印表機</h4>
        <p style="font-size:13px; color:#664d03;">印試卷最划算！自動雙面列印，碳粉超便宜。現省 \$200 港幣！</p>
        <a href="你的聯盟行銷網址" target="_blank" style="color:#0d6efd; font-weight:bold; text-decoration:none;">👉 點此領取專屬優惠購買</a>
    </div>
    """, 
    unsafe_allow_html=True
)

v_upper = st.slider("調整去手寫強度 (如果字體碎裂請調大，手寫沒除乾淨請調小)", 
                    min_value=100, max_value=180, value=140, step=5)

uploaded_files = st.file_uploader("選擇一張或多張工作紙圖片 (PNG, JPG, JPEG)", 
                                  type=["png", "jpg", "jpeg"], 
                                  accept_multiple_files=True)

# 彈出廣告視窗
@st.dialog("🎁 廣告贊助商（廣告載入中...）", width="large")
def show_ad_and_process(files, v_val):
    st.markdown("### 📢 支持我們繼續維持免費服務")
    st.write("請稍候 5 秒，讓廣告載入完畢，系統將自動為您生成乾淨試卷。")
    
    # 2. 彈窗內的黃金廣告位 (Google AdSense)
    st.markdown(
        """
        <div style="background-color:#f1f3f5; padding:35px; border-radius:10px; text-align:center; border:2px dashed #adb5bd;">
            <p style="color:#495057; font-size:18px;"><b>[ 這裡放置 Google AdSense 插頁廣告 ]</b></p>
            <p style="color:#868e96; font-size:13px;">點擊廣告支持我們，本站承諾永久免費！</p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    timer_placeholder = st.empty()
    for i in range(5, 0, -1):
        timer_placeholder.error(f"⏳ 廣告播放中，系統將於 {i} 秒後自動開始處理並打包您的試卷...")
        time.sleep(1)
        
    timer_placeholder.success("✅ 廣告載入完畢！開始處理試卷...")
    time.sleep(0.5)
    
    # 開始處理圖片
    zip_path = "cleaned_worksheets.zip"
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        progress_bar = st.progress(0)
        for index, uploaded_file in enumerate(files):
            file_bytes = np.frombuffer(uploaded_file.read(), np.uint8)
            img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
            
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            lower_black = np.array([0, 0, 0])
            upper_black = np.array([180, 80, v_val])
            black_mask = cv2.inRange(hsv, lower_black, upper_black)
            clean_image = cv2.bitwise_not(black_mask)
            
            out_name = f"cleaned_{uploaded_file.name}"
            _, img_encoded = cv2.imencode('.png', clean_image)
            zipf.writestr(out_name, img_encoded.tobytes())
            progress_bar.progress((index + 1) / len(files))
            
    st.balloons()
    st.success("✨ 所有試卷處理完畢！")
    
    # 3. 下載區與「第二個聯盟行銷位」（黃金點擊區）
    st.markdown("### 👇 下載您的乾淨試卷")
    with open(zip_path, "rb") as f:
        st.download_button(
            label="📥 點擊下載所有乾淨試卷 (ZIP)",
            data=f,
            file_name="cleaned_worksheets.zip",
            mime="application/zip",
            use_container_width=True
        )
        
    st.markdown("---")
    st.markdown("### 🎒 複習必備（家長限時特惠）")
    st.write("下載完考卷，不妨看看這些精選學習資源，幫助孩子拿高分：")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("📚 **精選小學數學練習冊**\n港幣 \$50 起！涵蓋各大名校熱門題型，配有詳細解題步驟。\n[👉 點此去淘寶/博客來看看](你的聯盟連結1)")
    with col2:
        st.success("🗣️ **外籍老師 1對1 英文課**\n限時免費領取一節體驗課！提升口語和聽力。\n[👉 點此免費領取體驗課](你的聯盟連結2)")
    
    if os.path.exists(zip_path):
        os.remove(zip_path)

if uploaded_files:
    st.success(f"已成功上傳 {len(uploaded_files)} 張圖片！")
    if st.button("🚀 開始批量去手寫處理", use_container_width=True):
        show_ad_and_process(uploaded_files, v_upper)

st.markdown("---")
st.caption("© 2026 試卷去手寫工具網. All Rights Reserved. 本工具永久免費提供。")