import streamlit as st
import pandas as pd
import os
import html
from datetime import date

# ====== 基本設定 ======
MAX_LESSONS = 100
GRID_SIZE = 10
DATA_FILE = "lessons.csv"

st.set_page_config(
    page_title="French B1 までの 100 マストラッカー",
    page_icon="📚",
    layout="centered",
)

# ====== ちょっと可愛い CSS ======
st.markdown(
    """
<style>
:root {
    --bg: #fff6fb;
    --card: #ffeef8;
    --accent: #ff8fab;
    --accent-soft: #ffd6e8;
    --text-main: #4a4a4a;
    --text-soft: #7b7b7b;
}

body {
    background: var(--bg);
}

.main > div {
    padding-top: 1rem;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.tracker-card {
    background: var(--card);
    border-radius: 24px;
    padding: 20px 24px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.05);
    border: 1px solid rgba(255,255,255,0.7);
}

.tracker-title {
    font-size: 1.4rem;
    font-weight: 700;
    color: var(--text-main);
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.tracker-sub {
    font-size: 0.9rem;
    color: var(--text-soft);
}

.badge-soft {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    font-size: 0.8rem;
    padding: 4px 10px;
    border-radius: 999px;
    background: rgba(255,143,171,0.12);
    color: #d94c6d;
}

.grid-wrapper {
    margin-top: 1rem;
    padding: 14px;
    border-radius: 20px;
    background: rgba(255,255,255,0.8);
    border: 1px dashed rgba(255,143,171,0.3);
}

.grid {
    display: flex;
    flex-direction: column;
    gap: 6px;
    justify-content: center;
    align-items: center;
}

.grid-row {
    display: flex;
    flex-direction: row;
    gap: 6px;
}

.cell {
    width: 26px;
    height: 26px;
    border-radius: 10px;
    border: 1px solid rgba(255,143,171,0.35);
    background: #ffeefa;
    box-sizing: border-box;
    cursor: default;
}

.cell.empty {
    background: rgba(255,255,255,0.9);
    border-style: dashed;
    opacity: 0.6;
}

.cell.filled {
    box-shadow: 0 0 0 1px rgba(255,255,255,0.5) inset;
}

.progress-label {
    font-size: 0.9rem;
    color: var(--text-soft);
}

strong.big-number {
    font-size: 1.4rem;
    color: var(--accent);
}

.b1-label {
    font-weight: 600;
}

.footer-note {
    font-size: 0.8rem;
    color: var(--text-soft);
    text-align: right;
    margin-top: 0.5rem;
}
</style>
""",
    unsafe_allow_html=True,
)

# ====== データ読み込み／初期化 ======
def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
    else:
        df = pd.DataFrame(columns=["id", "date", "teacher", "color", "note"])
    # idでソートしておく
    if not df.empty:
        df = df.sort_values("id").reset_index(drop=True)
    return df


def save_data(df):
    df.to_csv(DATA_FILE, index=False, encoding="utf-8")


df = load_data()
current_count = len(df)
remaining = max(0, MAX_LESSONS - current_count)

# ====== 上部カード ======
st.markdown(
    """
<div class="tracker-card">
  <div class="tracker-title">
    <span>📚 Mon parcours de 100 leçons de français</span>
    <span class="badge-soft">Objectif : niveau B1</span>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

st.write("")

# 進捗表示
col1, col2 = st.columns([2, 1])
with col1:
    st.markdown(
        f"""
**Progression actuelle：**  
<strong class="big-number">{current_count}</strong> / {MAX_LESSONS} leçons
""",
        unsafe_allow_html=True,
    )
    st.progress(min(current_count / MAX_LESSONS, 1.0))
with col2:
    st.markdown(
        f"""
**Avant le niveau B1：**  
<b class="b1-label">{remaining}</b> leçons
""",
        unsafe_allow_html=True,
    )

if current_count >= MAX_LESSONS:
    st.success("🎉 100 マス全部埋まった！B1 レベル到達おめでとう！！")


st.write("")

# ====== 100 マスグリッド ======
st.markdown("### 🎨 Mon tableau aux 100 cases")

def build_grid_html(df):
    cells_html = ""

    for row in range(GRID_SIZE):
        cells_html += '<div class="grid-row">'
        for col in range(GRID_SIZE):
            idx = row * GRID_SIZE + col
            if idx < len(df):
                r = df.iloc[idx]
                color = (
                    r["color"]
                    if isinstance(r["color"], str) and r["color"]
                    else "#FFB3C8"
                )
                note = r["note"] if isinstance(r["note"], str) else ""
                teacher = r["teacher"] if isinstance(r["teacher"], str) else "先生"
                date_str = r["date"]

                tooltip = f"{int(r['id'])} 回目 | {date_str} | {teacher}"
                if note:
                    tooltip += f" | {note}"

                tooltip = html.escape(tooltip, quote=True)

                cells_html += (
                    f'<div class="cell filled" '
                    f'style="background-color:{color};" '
                    f'title="{tooltip}"></div>'
                )
            else:
                cells_html += '<div class="cell empty"></div>'
        cells_html += "</div>"

    return f'<div class="grid-wrapper"><div class="grid">{cells_html}</div></div>'


st.markdown(build_grid_html(df), unsafe_allow_html=True)
st.markdown(
    '<p class="footer-note">※ 色付きマスにマウスを乗せるとメモが見えるよ。</p>',
    unsafe_allow_html=True,
)

st.write("")
st.write("---")

# ====== レッスン追加フォーム ======
st.markdown("### ✏️ 新しいレッスンを 1 マス追加")

if current_count >= MAX_LESSONS:
    st.warning("もう 100 マス全部埋まってるよ！新しく追加するには CSV を整理してね。")
else:
    with st.form("add_lesson_form"):
        col_a, col_b = st.columns(2)
        with col_a:
            lesson_date = st.date_input("レッスン日", value=date.today())
            teacher = st.text_input("先生の名前（任意）", placeholder="例）Marie / Lucas など")
        with col_b:
            default_color = "#FFB3C8"
            color = st.color_picker("このマスの色", value=default_color)

        note = st.text_area("メモ（任意）", placeholder="発音練習 / 文法ポイント / 感想 など")

        submitted = st.form_submit_button("🎀 1 マス塗る")

        if submitted:
            new_id = current_count + 1
            new_row = {
                "id": new_id,
                "date": lesson_date.isoformat(),
                "teacher": teacher.strip(),
                "color": color,
                "note": note.strip(),
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(df)

            st.success(f"{new_id} マス目を塗ったよ！")
            st.balloons()
            # 再描画のため
            st.rerun()


# ====== 簡単な履歴表示 ======
if not df.empty:
    st.write("")
    st.markdown("### 📝 最近のレッスン履歴（最新 10 件）")
    show_df = df.sort_values("id", ascending=False).head(10)
    show_df = show_df[["id", "date", "teacher", "note"]]
    show_df.columns = ["#", "日付", "先生", "メモ"]
    st.dataframe(show_df, use_container_width=True)
