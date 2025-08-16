import streamlit as st
import requests

st.set_page_config(page_title="AI Question Generator", page_icon="🧠", layout="wide")

st.title("🧠 AI Question Generator & Quiz")

if "quiz" not in st.session_state:
    st.session_state.quiz = []
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "current_question" not in st.session_state:
    st.session_state.current_question = 0

st.sidebar.header("⚙️ Quiz Parameters")
difficulty = st.sidebar.selectbox("Difficulty", ["easy", "medium", "hard"])
topic = st.sidebar.text_input("Topic", "Data Structures")
skill_tags = st.sidebar.text_input("Skill Tags (comma separated)", "algorithms, problem-solving")
question_type = st.sidebar.selectbox("Question Type", ["multiple_choice", "true_false", "fill_blank"])
programming_language = st.sidebar.text_input("Programming Language", "python")
num_questions = st.sidebar.number_input("Number of Questions", min_value=1, max_value=10, value=3)

if st.sidebar.button("🚀 Start Quiz"):
    payload = {
        "difficulty": difficulty,
        "topic": topic,
        "skill_tags": [tag.strip() for tag in skill_tags.split(",") if tag.strip()],
        "question_type": question_type,
        "programming_language": programming_language,
        "num_questions": num_questions,
    }

    with st.spinner("Generating questions..."):
        try:
            response = requests.post("http://localhost:8000/generate_question", json=payload)
            response.raise_for_status()
            data = response.json()
            
            if data["status"] == "success":
                st.session_state.quiz = data["question_data"]
                st.session_state.answers = {}
                st.session_state.submitted = False
                st.session_state.current_question = 0
            else:
                st.error("Failed to generate questions: " + data.get("message", "Unknown error"))
        except Exception as e:
            st.error(f"API request failed: {str(e)}")

if st.session_state.quiz:
    st.header("📝 Quiz")
    
    q_idx = st.session_state.current_question
    q = st.session_state.quiz[q_idx]
    
    st.subheader(f"Q{q_idx+1}. {q['question']}")
    
    if q.get("options"):
        if f"q{q_idx}" not in st.session_state.answers:
            st.session_state.answers[q_idx] = None
            
        choice = st.radio(
            "Select your answer:",
            q["options"],
            key=f"radio_{q_idx}",
            index=None if st.session_state.answers.get(q_idx) is None else q["options"].index(st.session_state.answers[q_idx])
        )
        
        if choice is not None:
            st.session_state.answers[q_idx] = choice
    else:
        answer = st.text_input("Your answer:", key=f"text_{q_idx}", value=st.session_state.answers.get(q_idx, ""))
        st.session_state.answers[q_idx] = answer
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⏮️ Previous", disabled=q_idx == 0):
            st.session_state.current_question -= 1
            st.rerun()
    with col2:
        if q_idx < len(st.session_state.quiz) - 1:
            if st.button("⏭️ Next", disabled=q_idx == len(st.session_state.quiz) - 1):
                st.session_state.current_question += 1
                st.rerun()
        else:
            if st.button("✅ Submit Quiz"):
                st.session_state.submitted = True
                st.rerun()

if st.session_state.submitted:
    st.header("📊 Results")
    score = 0
    total = len(st.session_state.quiz)
    
    for idx, q in enumerate(st.session_state.quiz):
        user_ans = st.session_state.answers.get(idx, "")
        correct_ans = q.get("correct_answer", "")
        
        st.markdown(f"### Q{idx+1}. {q['question']}")
        
        if user_ans == correct_ans:
            st.success(f"✅ Correct! Your answer: {user_ans}")
            score += 1
        else:
            st.error(f"❌ Wrong! Your answer: {user_ans} | Correct answer: {correct_ans}")
        
        if q.get("explanation"):
            st.info(f"💡 Explanation: {q['explanation']}")
        
        st.write("---")
    
    percentage = (score / total) * 100
    st.subheader(f"🏆 Final Score: {score} / {total} ({percentage:.1f}%)")
    
    if percentage >= 80:
        st.balloons()
        st.success("🎉 Excellent work!")
    elif percentage >= 60:
        st.success("👍 Good job!")
    else:
        st.warning("💪 Keep practicing!")