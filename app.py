import streamlit as st 
from dotenv import load_dotenv 
from openai import OpenAI 
import base64 

load_dotenv() 

client = OpenAI() 

def clear_all():
    st.session_state["note"] = ""
    st.session_state["result"] = ""
    st.session_state["condition"] = "選択してください"

st.title("メルカリAI出品サポート") 


# 初期化
if "result" not in st.session_state:
    st.session_state.result = ""

if "signature" not in st.session_state:
    st.session_state["signature"] = "株式会社〇〇"

# 画像アップ
uploaded_files = st.file_uploader(
    "商品画像", 
    type=["jpg", "png"],
    accept_multiple_files=True
    )

# 上限チェック（10枚）
MAX_FILES = 10
if uploaded_files and len(uploaded_files) > MAX_FILES:
    st.warning(f"画像は最大{MAX_FILES}枚までアップロードできます")
    st.stop()

# 枚数表示
if uploaded_files:
    st.write(f"📷 {len(uploaded_files)}枚選択中")

# 画像プレビュー
if uploaded_files :
    for file in uploaded_files:
        st.image(file, caption=file.name, use_container_width=True)

# 商品状態
condition = st.selectbox(
    "商品の状態",
    ["選択してください", "新品・未使用", "未使用に近い", "目立った傷や汚れなし", "やや傷や汚れあり", "傷や汚れあり"],
    key="condition"
)

# 補足情報
note = st.text_area(
    "補足情報",
    placeholder="例: 小さな傷あり / 箱なし / 2022年購入 / サイズM",
    key="note"
)	

# 署名
signature = st.text_input(
    "署名（会社名など）",
    placeholder="例: 株式会社〇〇",
    key="signature"
)

st.divider()

# 生成ボタン・クリアボタンUI
col1, col2 = st.columns([1, 3])

with col1:
    generate = st.button(
        "AIで出品文章生成", 
        key="generate_button",
        disabled=not uploaded_files
        )
with col2:
    st.button("クリア", on_click=clear_all, key="clear_button")

# 生成ボタン処理
if generate:

    if not uploaded_files:
        st.warning("画像をアップロードしてください")
        st.stop()

    results = []

    signature_text = signature if signature else ""

    prompt = f"""
この商品画像を分析してください。

まず画像から商品を推定してください。
そのあとメルカリ出品用の情報を作成してください。

商品状態: {condition}
補足情報: {note}

以下の形式で出力してください。

【商品推定】

【おすすめタイトル（5個）】
1.
2.
3.
4.
5.

【カテゴリ】

【商品説明】

【注意事項】

※出力の一番最後の行に必ず以下の内容をそのまま入れてください。（変更しないでください）
{signature_text}
"""

    progress_text = st.empty()

    with st.spinner(f"{len(uploaded_files)}件を生成中...（1〜2分かかります）"):

        for i, file in enumerate(uploaded_files, start=1):
            progress_text.write(f"{i}/{len(uploaded_files)} 件処理中...")

            image_bytes = file.read()
            image_data = base64.b64encode(image_bytes).decode()

            messages = [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": prompt}],
                }
            ]

            messages[0]["content"].append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image_data}"
                }
            })

            try:
                response = client.chat.completions.create(
                    model="gpt-4.1-mini",
                    messages=messages
                )

                result_text = response.choices[0].message.content
                results.append(f"【{i}枚目：{file.name}】\n{result_text}")

            except Exception as e:
                results.append(f"【{file.name}】エラー: {e}")

    st.session_state.result = "\n\n====================\n\n".join(results)

# 結果表示
if st.session_state.result != "":
    st.subheader("AI生成結果")

    result_list = st.session_state.result.split("\n\n====================\n\n")

    for i, result in enumerate(result_list, start=1):
        st.markdown(f"### {i}件目")

        st.text_area(
            f"結果 {i}",
            result,
            height=200,
            key=f"result_{i}"
        )

        st.code(result)

        st.caption("※右上のコピーアイコンからコピーできます")
