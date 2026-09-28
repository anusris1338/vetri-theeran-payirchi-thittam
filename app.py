import streamlit as st
from google import genai
from dotenv import load_dotenv
import os
import time
import json

load_dotenv()

st.set_page_config(
    page_title="EduGenie",
    page_icon="🎓",
    layout="centered"
)

st.title("🎓 EduGenie")
st.subheader("Your AI Learning Assistant")

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("Gemini API key is not configured.")
    st.stop()

client = genai.Client(api_key=api_key)

# ---------------- SIDEBAR ----------------

st.sidebar.header("⚙️ Learning Settings")

subject = st.sidebar.selectbox(
    "📚 Subject",
    [
        "Python",
        "Java",
        "C Programming",
        "DBMS",
        "Data Structures",
        "Software Engineering",
        "Computer Networks",
        "Other"
    ]
)

level = st.sidebar.selectbox(
    "🎯 Difficulty",
    ["Easy", "Medium", "Hard"]
)

# ---------------- TABS ----------------

tab1, tab2 = st.tabs(["📖 Learn", "📝 Quiz"])

# =====================================================
# LEARNING SECTION
# =====================================================

with tab1:

    st.write("Ask any academic question and learn in simple words.")

    question = st.text_area(
        "❓ Ask your question:",
        placeholder="Example: Explain Python variable in simple words"
    )

    if st.button("🚀 Ask EduGenie"):

        if not question.strip():
            st.warning("Please enter a question.")

        else:

            with st.spinner("EduGenie is thinking..."):

                prompt = f"""
You are EduGenie, an AI learning assistant for college students.

Subject: {subject}
Difficulty: {level}

Student question:
{question}

Give a clear and easy-to-understand answer.
Use examples when useful.
"""

                try:

                    response = None

                    for attempt in range(3):
                        try:
                            response = client.models.generate_content(
                                model="gemini-3.5-flash",
                                contents=prompt
                            )
                            break

                        except Exception as e:
                            if "503" in str(e) and attempt < 2:
                                time.sleep(5 * (attempt + 1))
                            else:
                                raise e

                    st.markdown("### 📚 AI Answer")
                    st.write(response.text)

                except Exception as e:
                    st.error(f"Something went wrong: {e}")


# =====================================================
# QUIZ SECTION
# =====================================================

with tab2:

    st.write("Generate an AI-powered quiz based on your selected subject.")

    quiz_topic = st.text_input(
        "📌 Quiz topic",
        placeholder="Example: Python variables"
    )

    number_of_questions = st.selectbox(
        "🔢 Number of questions",
        [5, 10]
    )

    if st.button("📝 Generate Quiz"):

        if not quiz_topic.strip():
            st.warning("Please enter a quiz topic.")

        else:

            with st.spinner("Generating your quiz..."):

                quiz_prompt = f"""
Create a multiple-choice quiz for college students.

Subject: {subject}
Topic: {quiz_topic}
Difficulty: {level}
Number of questions: {number_of_questions}

Return ONLY valid JSON.

Use exactly this structure:

{{
  "questions": [
    {{
      "question": "Question text",
      "options": [
        "Option A",
        "Option B",
        "Option C",
        "Option D"
      ],
      "answer": 0
    }}
  ]
}}

Important:
- answer must be the option index.
- 0 means Option A.
- 1 means Option B.
- 2 means Option C.
- 3 means Option D.
- Create exactly {number_of_questions} questions.
"""

                try:

                    response = None

                    for attempt in range(3):
                        try:
                            response = client.models.generate_content(
                                model="gemini-3.5-flash",
                                contents=quiz_prompt
                            )
                            break

                        except Exception as e:
                            if "503" in str(e) and attempt < 2:
                                time.sleep(5 * (attempt + 1))
                            else:
                                raise e

                    quiz_text = response.text.strip()

                    # Remove markdown code fences if Gemini adds them
                    if quiz_text.startswith("```"):
                        quiz_text = quiz_text.replace("```json", "")
                        quiz_text = quiz_text.replace("```", "")
                        quiz_text = quiz_text.strip()

                    quiz_data = json.loads(quiz_text)

                    st.session_state.quiz_data = quiz_data
                    st.session_state.quiz_topic = quiz_topic

                    st.success("✅ Quiz generated successfully!")

                except Exception as e:
                    st.error(f"Quiz generation failed: {e}")


# =====================================================
# DISPLAY QUIZ
# =====================================================

if "quiz_data" in st.session_state:

    st.markdown("---")
    st.markdown(
        f"## 📝 Quiz: {st.session_state.quiz_topic}"
    )

    quiz = st.session_state.quiz_data["questions"]

    # Store answers
    answers = []

    for i, q in enumerate(quiz):

        st.markdown(
            f"### Q{i + 1}. {q['question']}"
        )

        selected = st.radio(
            "Choose your answer:",
            q["options"],
            key=f"question_{i}"
        )

        answers.append(selected)

    if st.button("✅ Submit Quiz"):

        score = 0

        for i, q in enumerate(quiz):

            correct_index = q["answer"]
            correct_answer = q["options"][correct_index]

            if answers[i] == correct_answer:
                score += 1

        total = len(quiz)

        st.markdown("---")
        st.markdown("## 🏆 Quiz Result")

        st.success(
            f"You scored {score} / {total}"
        )

        percentage = (score / total) * 100

        st.progress(percentage / 100)

        st.write(f"📊 Score: {percentage:.0f}%")

        if percentage >= 80:
            st.balloons()
            st.success("Excellent work! 🎉")

        elif percentage >= 50:
            st.info("Good job! Keep practicing. 👍")

        else:
            st.warning("Keep learning and try again! 💪")