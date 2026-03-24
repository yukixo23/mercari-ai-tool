import streamlit as st 
from dotenv import load_dotenv 
from openai import OpenAI 
import base64 

load_dotenv() 

client = OpenAI() 

st.title("メルカリAI出品サポート") 


# 初期化
if "result" not in st.session_state:
    st.session_state.result = ""

# 画像アップ
uploaded_file = st.file_uploader("商品画像", type=["jpg", "png"])

# 画像プレビュー
if uploaded_file is not None:
    st.image(uploaded_file, caption="アップロード画像", use_container_width=True)

# 商品状態
condition = st.selectbox(
    "商品の状態",
    ["選択してください", "新品・未使用", "未使用に近い", "目立った傷や汚れなし", "やや傷や汚れあり", "傷や汚れあり"]
)

# 補足情報
note = st.text_area(
    "補足情報",
    placeholder="例: 小さな傷あり / 箱なし / 2022年購入 / サイズM"
)

st.divider()

# AI生成ボタン
if st.button("AIで出品文章生成"):

    image_data = None

    if uploaded_file is not None:
        image_bytes = uploaded_file.read()
        image_data = base64.b64encode(image_bytes).decode()

    prompt = f"""
    この商品画像を分析してください。

    まず画像から商品を推定してください。
    そのあとメルカリ出品用の情報を作成してください。

    商品状態: {condition}
    補足情報: {note}

    以下の形式で出力してください。

    【商品推定】

    【おすすめタイトル（5個）】
    メルカリで検索されやすいキーワードを入れてください。
    30文字以内。
    1.
    2.
    3.
    4.
    5.

    【カテゴリ】

    【商品説明】

    【注意事項】
    """

    messages = [
        {
            "role": "user",
            "content": [{"type": "text", "text": prompt}],
        }
    ]

    if image_data:
        messages[0]["content"].append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{image_data}"
            }
        })

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages
    )

    st.session_state.result = response.choices[0].message.content

# 結果表示
if st.session_state.result != "":
    st.subheader("AI生成結果")

    st.text_area(
        "メルカリ出品用テキスト",
        st.session_state.result,
        height=300
    )

    st.subheader("コピー用")
    st.code(st.session_state.result)
