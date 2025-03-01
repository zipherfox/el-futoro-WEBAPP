import streamlit as st
import google.generativeai as genai

# --- Configuration ---

st.title("🎓 Major and Career Path Navigator")  # More engaging title
st.write(
    "This AI-powered tool helps you discover potential majors and career paths "
    "based on your interests, skills, and preferences. Powered by Google's Gemini. "
    "Get a Google AI Studio API key [here](https://makersuite.google.com/app/apikey)."
)

# --- API Key Handling (Streamlit Secrets Only) ---

def get_api_key():
    """Gets the API key from Streamlit secrets."""
    try:
        return st.secrets["gemini_api_key"]
    except KeyError:
        st.error("The 'gemini_api_key' variable was not found in secrets.toml. "
                 "Add it to .streamlit/secrets.toml:\n\ngemini_api_key = \"your-api-key\"")
        st.stop()
    except Exception as e:
        st.error(f"Error retrieving API key: {e}")
        st.stop()

google_api_key = get_api_key()
genai.configure(api_key=google_api_key)

# --- Student Information Input (using your friend's questions) ---

with st.form("student_profile"):
    st.subheader("Tell us about yourself:")
    name = st.text_input("Your Name (Optional):", key="name")  # Added key
    q1 = st.text_area("1. What subjects do you like?", key="q1")
    q2 = st.text_area("2. Which environment do you prefer working in (e.g., WFH, customer service, outdoors, office)?", key="q2")
    q3 = st.text_area("3. What activities do you enjoy the most (hobbies)?", key="q3")
    q4 = st.text_area("4. What do people say about your personality? And what do you think about it?", key="q4")
    q5 = st.text_area("5. What activities are you naturally good at?", key="q5")
    q6 = st.text_area("6. Do you prefer working alone or in a team? (If in a team, do you enjoy leading or supporting roles?)", key="q6")
    q7 = st.text_area("7. Are you comfortable with continuous learning and adapting to new trends?", key="q7")

    submitted = st.form_submit_button("Explore My Options!")

# --- Session State (for conversation) ---

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Display Previous Conversation ---

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Initial Prompt (After Form Submission) ---

if submitted:
    if not all([q1, q2, q3, q4, q5, q6, q7]):  # More concise emptiness check
        st.warning("Please answer all the questions to get the best recommendations.")
    else:
        initial_prompt = (
            f"Student Profile:\n"
            f"Name: {name if name else 'A student'}\n\n"  # Optional name
            f"1. Liked Subjects: {q1}\n"
            f"2. Preferred Work Environment: {q2}\n"
            f"3. Hobbies: {q3}\n"
            f"4. Personality (Others' and Self-Perception): {q4}\n"
            f"5. Natural Talents: {q5}\n"
            f"6. Teamwork Preference: {q6}\n"
            f"7. Adaptability to Learning: {q7}\n\n"
            "Based on this comprehensive profile, suggest suitable majors and career paths. "
            "Provide detailed explanations, including:\n"
            "* **Specific Major Recommendations:** (e.g., Computer Science, Psychology, Environmental Engineering)\n"
            "* **Why These Majors Fit:** Connect the student's answers to the major requirements and career outcomes.\n"
            "* **Potential Career Paths:** List specific job titles or career areas for each major (e.g., Software Engineer, Clinical Psychologist, Environmental Consultant).\n"
            "* **Pros and Cons:** Briefly discuss the advantages and disadvantages of each path.\n"
            "* **Further Exploration:** Suggest resources like professional organizations, websites, or books for the student to learn more.\n"
            "* **University/College Suggestions (Optional):** If possible, mention universities known for strong programs in the suggested majors."

        )

        st.session_state.messages.append({"role": "user", "content": initial_prompt})
        with st.chat_message("user"):
            st.markdown(initial_prompt)

        # --- Gemini API Call (Initial Response) ---
        try:
            model = genai.GenerativeModel('gemini-1.5-pro-002')
            chat = model.start_chat(history=[])

            response = chat.send_message(initial_prompt, stream=True)

            with st.chat_message("assistant"):
                full_response = ""
                placeholder = st.empty()
                for chunk in response:
                    full_response += chunk.text
                    placeholder.markdown(full_response + "▌")
                placeholder.markdown(full_response)

            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"An error occurred: {e}")

# --- Subsequent Chat Input (for follow-up questions) ---
if prompt := st.chat_input("Ask a follow-up question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # --- Gemini API Call (Follow-up Response) ---
    try:
        initial_user_message = None
        initial_assistant_message = None
        for i in range(len(st.session_state.messages) - 1):
            if st.session_state.messages[i]['role'] == 'user' and st.session_state.messages[i+1]['role'] == 'assistant':
                initial_user_message = st.session_state.messages[i]
                initial_assistant_message = st.session_state.messages[i+1]
                break

        history = []
        if initial_user_message and initial_assistant_message:
            history.append({"role": initial_user_message["role"], "parts": [initial_user_message["content"]]})
            history.append({"role": initial_assistant_message["role"], "parts": [initial_assistant_message["content"]]})

        for i in range (len(st.session_state.messages) -1):
            if st.session_state.messages[i]['role'] != 'model':
                history.append({"role":st.session_state.messages[i]['role'], "parts":[st.session_state.messages[i]['content']]})


        model = genai.GenerativeModel('gemini-1.5-pro-002')  # Consistent model
        chat = model.start_chat(history=history)
        response = chat.send_message(prompt, stream=True)

        with st.chat_message("assistant"):
            full_response = ""
            placeholder = st.empty()
            for chunk in response:
                full_response += chunk.text
                placeholder.markdown(full_response + "▌")
            placeholder.markdown(full_response)

        st.session_state.messages.append({"role": "assistant", "content": full_response})

    except Exception as e:
        st.error(f"An error occurred: {e}")