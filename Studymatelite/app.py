import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="StudyMate Lite", page_icon="📚", layout="wide")

def calculate_d_day(exam_date):
    return (exam_date - date.today()).days

def urgency_score(d_day):
    if d_day <= 2:
        return 5
    elif d_day <= 5:
        return 4
    elif d_day <= 10:
        return 3
    elif d_day <= 20:
        return 2
    else:
        return 1

def calculate_priority(difficulty, weakness, d_day):
    urgency = urgency_score(d_day)
    score = weakness * 0.5 + difficulty * 0.3 + urgency * 0.2
    return round(score, 2)

if "subjects" not in st.session_state:
    st.session_state.subjects = []

st.title("📚 StudyMate Lite")
st.write("과목별 우선순위/난이도에 따라 공부 시간을 배분해드립니다.")

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.header("입력")

    daily_hours = st.number_input(
        "오늘 공부 가능한 시간",
        min_value=0.5,
        max_value=12.0,
        value=3.0,
        step=0.5
    )

    with st.form("subject_form"):
        subject = st.text_input("과목명", placeholder="예: 수학")
        exam_date = st.date_input("시험 날짜", min_value=date.today())
        difficulty = st.slider("난이도", 1, 5, 3)
        weakness = st.slider("취약도", 1, 5, 3)
        weak_unit = st.text_input("취약 단원", placeholder="예: 함수, 문법, 독해")

        submitted = st.form_submit_button("과목 추가")

        if submitted:
            if subject == "" or weak_unit == "":
                st.error("과목명과 취약 단원을 입력하세요.")
            else:
                st.session_state.subjects.append({
                    "과목": subject,
                    "시험 날짜": exam_date,
                    "난이도": difficulty,
                    "취약도": weakness,
                    "취약 단원": weak_unit
                })
                st.success(f"{subject} 과목이 추가되었습니다.")

    if st.button("전체 삭제"):
        st.session_state.subjects = []
        st.success("모든 과목을 삭제했습니다.")

with col2:
    st.header("등록된 과목")

    if len(st.session_state.subjects) == 0:
        st.info("아직 등록된 과목이 없습니다.")
    else:
        table = []

        for s in st.session_state.subjects:
            d_day = calculate_d_day(s["시험 날짜"])

            table.append({
                "과목": s["과목"],
                "시험까지": "D-Day" if d_day == 0 else f"D-{d_day}",
                "난이도": s["난이도"],
                "취약도": s["취약도"],
                "취약 단원": s["취약 단원"]
            })

        st.dataframe(pd.DataFrame(table), hide_index=True)

st.divider()

st.header("오늘의 추천 학습 계획")

if len(st.session_state.subjects) == 0:
    st.warning("과목을 먼저 추가하세요.")
else:
    result = []
    total_minutes = int(daily_hours * 60)

    for s in st.session_state.subjects:
        d_day = calculate_d_day(s["시험 날짜"])
        priority = calculate_priority(s["난이도"], s["취약도"], d_day)

        result.append({
            "과목": s["과목"],
            "시험까지": "D-Day" if d_day == 0 else f"D-{d_day}",
            "우선순위 점수": priority,
            "취약 단원": s["취약 단원"]
        })

    total_priority = sum(r["우선순위 점수"] for r in result)

    for r in result:
        r["추천 공부 시간(분)"] = round(total_minutes * r["우선순위 점수"] / total_priority)
        r["추천 공부 내용"] = r["취약 단원"] + " 개념 정리 + 문제 풀이"

    df = pd.DataFrame(result)
    df = df.sort_values(by="우선순위 점수", ascending=False)

    st.dataframe(df, hide_index=True)

    top = df.iloc[0]
    st.success(
        f"오늘 가장 먼저 공부할 과목은 **{top['과목']}**입니다. "
        f"추천 공부 시간은 **{top['추천 공부 시간(분)']}분**입니다."
    )

    chart_df = df[["과목", "추천 공부 시간(분)"]].set_index("과목")
    st.bar_chart(chart_df)