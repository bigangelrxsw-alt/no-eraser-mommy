import streamlit as st
import cv2
import numpy as np
import zipfile
import os
import time
from pdf2image import convert_from_bytes
import streamlit.components.v1 as components

# ====================================================
# 🔒 網頁來源限制（Python 後端金鑰驗證 - 徹底堵死白嫖漏洞）
# ====================================================
# 檢查網址參數中是否包含正確的授權金鑰
query_params = st.query_params
is_authorized = query_params.get("from") == "nomummy"

# 如果不是從官方網站管道（未帶正確金鑰），且不是本地開發環境，直接硬性阻斷
if not is_authorized:
    # 允許本地開發測試
    import urllib.parse
    is_localhost = False
    try:
        # 額外檢查是否為本地執行
        if "localhost" in st.context.headers.get("Host", "") or "127.0.0.1" in st.context.headers.get("Host", ""):
            is_localhost = True
    except:
        pass
        
    if not is_localhost:
        st.set_page_config(page_title="存取被拒絕", layout="centered")
        st.error("⚠️ 存取被拒絕：此工具僅授權在 https://nomummy.com 內使用。")
        st.info("請前往官方網站使用本工具：[https://nomummy.com](https://nomummy.com)")
        st.stop()  # 🚫 徹底終止 Python 執行，不渲染任何工具 UI

# ====================================================
# 🗂️ 處理 ads.txt 路由（讓 Google AdSense 能夠直接驗證）
# ====================================================
import urllib.parse
query_params = st.query_params
if "page" in query_params and query_params["page"] == "ads.txt":
    st.write("google.com, pub-6074839973481448, DIRECT, f08c47fec0942fa0")
    st.stop()

# ====================================================
# ✨ 媽咪感 UI 設定：全域色調與風格
# ====================================================
MOMMY_PEACH = "#FFE6D9"  # 溫暖的柔和粉橘背景
MOMMY_ORANGE = "#FF8C61" # 活力、溫暖的按鈕/標題色
MOMMY_BROWN = "#6A4F3B"  # 溫和的文字咖啡色
MOMMY_WHITE = "#FFFFFF"  # 乾淨的米白卡片背景

# 改為 wide 佈局以提供完美的左右對比預覽
st.set_page_config(page_title="唔使媽咪擦 NoEraserMommy - 家長專用", layout="wide")

# 這裡為你植入了 Google AdSense 全站自動廣告與驗證代碼
st.markdown("""
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-6074839973481448" crossorigin="anonymous"></script>
""", unsafe_allow_html=True)

st.markdown(f"""
    <style>
    /* 全網頁背景色 */
    .stApp {{
        background-color: {MOMMY_PEACH};
        color: {MOMMY_BROWN};
    }}
    
    /* ✨ 終極防線：全面隱藏右上角 Deploy、工具列，以及右下角 Manage app 按鈕 */
    .stAppToolbar, 
    [data-testid="stAppToolbar"], 
    [data-testid="stAppToolbarContainer"],
    iframe ~ div [class*="stDeployButton"],
    div[data-testid="stManageAppButton"],
    footer,
    #MainMenu {{
        display: none !important;
        opacity: 0 !important;
        visibility: hidden !important;
        height: 0 !important;
        width: 0 !important;
    }}
    
    /* 溫馨的主標題 */
    h1 {{
        color: {MOMMY_ORANGE};
        font-family: 'Helvetica Neue', 'Helvetica', 'Arial', 'cwTeXYen', '微軟正黑體', sans-serif;
        text-align: center;
        border-bottom: 2px dashed {MOMMY_ORANGE};
        padding-bottom: 10px;
        margin-bottom: 20px;
    }}
    
    /* 副標題與小愛心裝飾 */
    h2, h3, .subheader {{
        color: {MOMMY_BROWN};
        font-family: 'cwTeXYen', '微軟正黑體', sans-serif;
    }}
    h3::before {{
        content: '🧡 ';
    }}

    /* 按鈕樣式：圓角、溫暖橘色 */
    .stButton>button {{
        background-color: {MOMMY_ORANGE} !important;
        color: {MOMMY_WHITE} !important;
        border-radius: 20px !important;
        border: none !important;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1) !important;
        font-weight: bold !important;
        width: 100% !important;
        margin-top: 10px;
        transition: all 0.3s ease;
    }}
    .stButton>button:hover {{
        background-color: #ff7f4a !important;
        transform: translateY(-2px);
    }}

    /* 預盛裝飾盒 */
    .preview-box {{
        background-color: {MOMMY_WHITE};
        padding: 12px;
        border-radius: 10px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
        text-align: center;
        font-weight: bold;
        margin-bottom: 10px;
    }}

    /* 隱藏預設的側邊欄背景 */
    [data-testid="stSidebar"] {{
        background-color: #fff9f6;
    }}
    </style>
""", unsafe_allow_html=True)

# ====================================================
# 📢 廣告驗證代碼配置區
# ====================================================
POPUP_AD_CODE = """
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-6074839973481448" crossorigin="anonymous"></script>
<div style="text-align:center; background-color:#fffcf9; padding:15px; border-radius:10px; border:3px dashed #ffc107;">
    <p style="color:#666; font-size:14px; margin:0 0 10px 0;">[ 💖 支持我們提供免費服務 / ADVERTISEMENT ]</p>
    <ins class="adsbygoogle"
         style="display:block"
         data-ad-client="ca-pub-6074839973481448"
         data-ad-slot="default"
         data-ad-format="auto"
         data-full-width-responsive="true"></ins>
    <script>
         (adsbygoogle = window.adsbygoogle || []).push({});
    </script>
    <div style="height:200px; background-color:#e9ecef; display:flex; align-items:center; justify-content:center; color:#999; font-size:14px; margin-top:10px;">
        <b>Google 廣告載入中...</b>
    </div>
</div>
"""

SIDEBAR_AD_CODE = """
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-6074839973481448" crossorigin="anonymous"></script>
<div style="text-align:center; background-color:#fffcf9; padding:10px; border-radius:5px; border:1px solid #ffefe6;">
    <p style="color:#999; font-size:12px; margin:0 0 5px 0;">ADVERTISEMENT</p>
    <ins class="adsbygoogle"
         style="display:block"
         data-ad-client="ca-pub-6074839973481448"
         data-ad-slot="default"
         data-ad-format="auto"
         data-full-width-responsive="true"></ins>
    <script>
         (adsbygoogle = window.adsbygoogle || []).push({});
    </script>
    <div style="height:200px; background-color:#e9ecef; display:flex; align-items:center; justify-content:center; color:#999; font-size:13px; margin-top:10px;">
         <b>Google 側欄廣告</b>
    </div>
</div>
"""

# 溫馨主標題
st.markdown(f"<h1>📝 唔使媽咪擦 NoEraserMommy</h1>", unsafe_allow_html=True)
st.subheader("批量試卷去筆跡工具 - 家長的好幫手")
st.write("上傳帶有手寫答案、批改符號的工作紙（支援圖片或 PDF），一鍵批量導出乾淨的空白題目卷，讓孩子開心複習！")

# 1. 側邊欄廣告
st.sidebar.markdown("### 📢 支持我們")
components.html(SIDEBAR_AD_CODE, height=320)

# ====================================================
# 🖼️ 核心影像處理功能 (免費 OpenCV 去陰影與斷線修復)
# ====================================================
def process_core_image(img, v_val):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_black = np.array([0, 0, 0])
    upper_black = np.array([180, 80, v_val])
    black_mask = cv2.inRange(hsv, lower_black, upper_black)
    extracted = cv2.bitwise_not(black_mask)
    
    if len(extracted.shape) == 3:
        gray = cv2.cvtColor(extracted, cv2.COLOR_BGR2GRAY)
    else:
        gray = extracted
        
    binary = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 21, 10
    )
    
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    final_img = cv2.erode(binary, kernel, iterations=1) 
    
    return final_img

# ====================================================
# 📄 主功能邏輯
# ====================================================

# 調整強度
st.markdown(f"<div style='color:{MOMMY_BROWN}; font-weight:bold; margin-top:20px;'>調整去手寫強度</div>", unsafe_allow_html=True)
v_upper = st.slider("(如果字體碎裂請往左調小，手寫沒除乾淨請往右調大)", 
                    min_value=100, max_value=180, value=140, step=5, label_visibility="collapsed")

# 支援圖片與 PDF 的上傳器
uploaded_files = st.file_uploader("選擇一個或多個工作紙圖片 (PNG, JPG, JPEG) 或 PDF 檔案", 
                                  type=["png", "jpg", "jpeg", "pdf"], 
                                  accept_multiple_files=True)

# 統一儲存解開後的圖片矩陣 [(檔名, cv2_image)]
all_pages_list = []

if uploaded_files:
    for uploaded_file in uploaded_files:
        file_ext = os.path.splitext(uploaded_file.name)[1].lower()
        
        # 處理 PDF 檔案
        if file_ext == '.pdf':
            with st.spinner(f"正在拆解 PDF 頁面: {uploaded_file.name}..."):
                try:
                    pdf_bytes = uploaded_file.read()
                    images = convert_from_bytes(pdf_bytes)
                    for idx, page in enumerate(images):
                        cv_img = np.array(page)
                        cv_img = cv2.cvtColor(cv_img, cv2.COLOR_RGB2BGR)
                        all_pages_list.append((f"{os.path.splitext(uploaded_file.name)[0]}_頁{idx+1}.png", cv_img))
                except Exception as e:
                    st.error(f"PDF 解析失敗，請確認 Mac 是否安裝 poppler 工具。錯誤訊息: {e}")
        # 處理普通圖片
        else:
            file_bytes = np.frombuffer(uploaded_file.read(), np.uint8)
            img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
            all_pages_list.append((uploaded_file.name, img))

    # ====================================================
    # 即時 Before / After 預覽區
    # ====================================================
    if all_pages_list:
        st.markdown("### 👁️ 去筆跡效果即時預覽 (以第一頁為例)")
        preview_name, preview_img = all_pages_list[0]
        
        # 即時運算處理結果
        preview_clean = process_core_image(preview_img, v_upper)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<div class='preview-box' style='color:#6A4F3B;'>📷 原始工作紙檔案</div>", unsafe_allow_html=True)
            st.image(cv2.cvtColor(preview_img, cv2.COLOR_BGR2RGB), use_container_width=True)
        with col2:
            st.markdown("<div class='preview-box' style='color:#FF8C61;'>✨ 去筆跡成果</div>", unsafe_allow_html=True)
            st.image(preview_clean, use_container_width=True)
            
        num_files = len(all_pages_list)
        st.markdown(f"<div style='color:{MOMMY_ORANGE}; font-weight:bold; margin15px 0;'>已成功載入共 {num_files} 頁待處理試卷！</div>", unsafe_allow_html=True)

        # 彈出廣告與批量處理視窗
        @st.dialog("🎁 廣告贊助商（廣告載入中...）", width="large")
        def show_ad_and_process(files_list):
            st.markdown("### 📢 支持我們繼續維持免費服務")
            
            # 動態計時器（依頁數調整）
            base = 15
            extra = max(0, ((len(files_list) - 4) + 1) // 2) * 15
            total_seconds = min(base + extra, 60)

            st.write(f"請稍候 {total_seconds} 秒，讓廣告載入完畢，系統將自動為您生成乾淨試卷。您的支持讓更多家長受惠！")
            
            # 彈窗內載入廣告
            components.html(POPUP_AD_CODE, height=330)
            
            timer_placeholder = st.empty()
            for i in range(total_seconds, 0, -1):
                timer_placeholder.error(f"⏳ 廣告播放中，系統將於 {i} 秒後自動開始處理並打包您的試卷...")
                time.sleep(1)
                
            timer_placeholder.success("✅ 廣告載入完畢！開始處理試卷...")
            time.sleep(0.5)
            
            # 批量處理影像並寫入 ZIP
            zip_path = "cleaned_worksheets.zip"
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                progress_bar = st.progress(0, text="媽咪加油，正在製作中...")
                for index, (name, img_data) in enumerate(files_list):
                    
                    # 執行包含去陰影與修復的影像處理
                    clean_image = process_core_image(img_data, v_upper)
                    
                    out_name = f"cleaned_{name}"
                    _, img_encoded = cv2.imencode('.png', clean_image)
                    zipf.writestr(out_name, img_encoded.tobytes())
                    progress_bar.progress((index + 1) / len(files_list), text=f"正在製作第 {index+1} 張...快好了！")
                    
            st.balloons()
            st.success("✨ 所有試卷處理完畢！")
            
            # 下載區
            st.markdown("### 👇 下載您的乾淨試卷")
            with open(zip_path, "rb") as f:
                st.download_button(
                    label="📥 點擊下載所有乾淨試卷 (ZIP)",
                    data=f,
                    file_name="cleaned_worksheets.zip",
                    mime="application/zip",
                    use_container_width=True
                )
            
            if os.path.exists(zip_path):
                os.remove(zip_path)

        if st.button("🚀 開始批量去手寫處理", use_container_width=True):
            show_ad_and_process(all_pages_list)

st.markdown("---")
# 頁尾
st.markdown(
    f"<p style='text-align:center; color:#a08d7e; font-size:12px;'>© 2026 🤝 唔使媽咪擦 NoEraserMommy. All Rights Reserved.<br>本工具永久免費提供予所有家長使用。</p>", 
    unsafe_allow_html=True
)