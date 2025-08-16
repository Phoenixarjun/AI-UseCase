import streamlit as st
import requests

st.set_page_config(page_title="AI Question Generator", page_icon="🧠", layout="wide")

st.title("🧠 AI Question Generator & Quiz")

def initialize_session_state():
    defaults = {
        "quiz": [],
        "answers": {},
        "submitted": False,
        "current_question": 0,
        "app_state": "initial",
        "review_questions": [],
        "quiz_params": {}
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

initialize_session_state()

def generate_questions():
    payload = {
        "difficulty": st.session_state.quiz_params["difficulty"],
        "topic": st.session_state.quiz_params["topic"],
        "skill_tags": st.session_state.quiz_params["skill_tags"],
        "question_type": st.session_state.quiz_params["question_type"],
        "programming_language": st.session_state.quiz_params["programming_language"],
        "num_questions": st.session_state.quiz_params["num_questions"],
    }
    with st.spinner("Generating new questions..."):
        try:
            response = requests.post("http://localhost:8000/generate_question", json=payload)
            response.raise_for_status()
            data = response.json()
            if data.get("status") == "success":
                st.session_state.review_questions = data["question_data"]
                st.session_state.app_state = "reviewing"
            else:
                st.error("Failed to generate questions: " + data.get("message", "Unknown error"))
                st.session_state.app_state = "initial"
        except Exception as e:
            st.error(f"API request failed: {str(e)}")
            st.session_state.app_state = "initial"

st.sidebar.header("⚙️ Quiz Parameters")
difficulty = st.sidebar.selectbox("Difficulty", ["easy", "medium", "hard"])
topic = st.sidebar.text_input("Topic", "Data Structures")
skill_tags = st.sidebar.text_input("Skill Tags (comma separated)", "algorithms, problem-solving")
question_type = st.sidebar.selectbox("Question Type", ["multiple_choice", "true_false", "fill_in_blank"])
programming_language = st.sidebar.text_input("Programming Language", "python")
num_questions = st.sidebar.number_input("Number of Questions", min_value=1, max_value=10, value=3)

if st.sidebar.button("🚀 Generate Questions for Review"):
    st.session_state.quiz_params = {
        "difficulty": difficulty,
        "topic": topic,
        "skill_tags": [tag.strip() for tag in skill_tags.split(",") if tag.strip()],
        "question_type": question_type,
        "programming_language": programming_language,
        "num_questions": num_questions,
    }
    generate_questions()
    st.rerun()

if st.session_state.app_state == "initial":
    st.info("Please use the sidebar to set your parameters and generate questions for review.")

elif st.session_state.app_state == "reviewing":
    st.header("🔍 SME Review Dashboard")
    st.warning("Please review the AI-generated questions below. You can edit any field before approving.")

    for i, q in enumerate(st.session_state.review_questions):
        with st.expander(f"**Question {i+1}:** {q['question'][:80]}...", expanded=True):
            q['question'] = st.text_area("Question Text", q['question'], key=f"q_text_{i}")
            
            if 'options' in q and q['options']:
                options = q['options']
                new_options = []
                for j, opt in enumerate(options):
                    new_opt = st.text_input(f"Option {j+1}", opt, key=f"opt_{i}_{j}")
                    new_options.append(new_opt)
                q['options'] = new_options
                
                try:
                    correct_index = options.index(q['correct_answer'])
                except ValueError:
                    correct_index = 0
                
                q['correct_answer'] = st.radio(
                    "Select Correct Answer", 
                    options, 
                    index=correct_index, 
                    key=f"ca_{i}"
                )
            else:
                q['correct_answer'] = st.text_input("Correct Answer", q.get('correct_answer', ''), key=f"ca_{i}")

            q['explanation'] = st.text_area("Explanation", q.get('explanation', ''), key=f"exp_{i}")

    st.write("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Approve & Start Quiz", use_container_width=True):
            st.session_state.quiz = st.session_state.review_questions
            st.session_state.answers = {}
            st.session_state.submitted = False
            st.session_state.current_question = 0
            st.session_state.app_state = "taking_quiz"
            st.rerun()
    with col2:
        if st.button("❌ Decline & Regenerate", type="primary", use_container_width=True):
            generate_questions()
            st.rerun()

elif st.session_state.app_state == "taking_quiz" and st.session_state.quiz:
    if st.session_state.submitted:
        st.session_state.app_state = "results"
        st.rerun()

    st.header("📝 Quiz")
    q_idx = st.session_state.current_question
    q = st.session_state.quiz[q_idx]
    
    st.subheader(f"Q{q_idx+1}. {q['question']}")
    
    if q.get("options"):
        choice = st.radio(
            "Select your answer:", q["options"], 
            key=f"radio_{q_idx}", 
            index=None
        )
        if choice is not None:
            st.session_state.answers[q_idx] = choice
    else:
        answer = st.text_input("Your answer:", key=f"text_{q_idx}")
        st.session_state.answers[q_idx] = answer
    
    st.write("---")
    col1, col2, col3 = st.columns([1, 6, 1])
    with col1:
        if st.button("⏮️ Previous", disabled=q_idx == 0):
            st.session_state.current_question -= 1
            st.rerun()
    with col3:
        if q_idx < len(st.session_state.quiz) - 1:
            if st.button("Next ⏭️"):
                st.session_state.current_question += 1
                st.rerun()
        else:
            if st.button("✅ Submit Quiz"):
                st.session_state.submitted = True
                st.rerun()

elif st.session_state.app_state == "results":
    st.header("📊 Results")
    score = 0
    total = len(st.session_state.quiz)
    
    for idx, q in enumerate(st.session_state.quiz):
        user_ans = st.session_state.answers.get(idx, "Not Answered")
        correct_ans = q.get("correct_answer", "")
        
        st.markdown(f"### Q{idx+1}. {q['question']}")
        
        is_correct = str(user_ans).strip().lower() == str(correct_ans).strip().lower()
        if is_correct:
            st.success(f"✅ Correct! Your answer: {user_ans}")
            score += 1
        else:
            st.error(f"❌ Wrong! Your answer: {user_ans} | Correct answer: {correct_ans}")
        
        if q.get("explanation"):
            st.info(f"💡 Explanation: {q['explanation']}")
        
        st.write("---")
    
    percentage = (score / total) * 100 if total > 0 else 0
    st.subheader(f"🏆 Final Score: {score} / {total} ({percentage:.1f}%)")
    
    if percentage >= 80:
        st.balloons()
        st.success("🎉 Excellent work!")
    elif percentage >= 60:
        st.success("👍 Good job!")
    else:
        st.warning("💪 Keep practicing!")
    
    if st.button("🔄 Take Another Quiz"):
        st.session_state.app_state = "initial"
        st.session_state.quiz = []
        st.rerun()