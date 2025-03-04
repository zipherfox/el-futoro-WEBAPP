import streamlit as st
import google.generativeai as genai
import re  # Import the regular expression library

# --- Configuration ---

st.title("🎓 Major and Career Path Navigator")
st.write(
    "This AI-powered tool helps you discover potential majors and career paths "
    "based on your interests, skills, and preferences. Powered by Google's Gemini. "
    "Get a Google AI Studio API key [here](https://makersuite.google.com/app/apikey)."
)

# --- API Key Handling (Streamlit Secrets OR User Input) ---

def get_api_key():
    """Gets the API key from Streamlit secrets (trial) or user input."""
    api_key_source = st.radio(
        "Choose API Key Source:",
        ("Use my own API Key", "Use a Trial API Key (limited usage)"),
        index=1,  # Default to the trial key
        horizontal=True,
    )

    if api_key_source == "Use my own API Key":
        user_api_key = st.text_input("Enter your Google AI Studio API Key:", type="password")
        if user_api_key:
            return user_api_key
        else:
            st.warning("Please enter your API key.")
            st.stop()  # Stop if the user doesn't enter their key
    else:  # Use the trial key
        try:
            return st.secrets["gemini_api_key"]  # Try to get from secrets.toml
        except KeyError:
            st.error(
                    "The 'gemini_api_key' variable was not found in secrets.toml.  "
                    "For the trial to work, you need to add a valid key to your Streamlit secrets.  "
                    "Add it to .streamlit/secrets.toml:\n\n`gemini_api_key = \"your-trial-api-key\"`\n\n"
                    "Alternatively, choose 'Use my own API Key' and enter your personal key."
                )
            st.stop()
        except Exception as e:
            st.error(f"Error retrieving trial API key: {e}")
            st.stop()


google_api_key = get_api_key()
genai.configure(api_key=google_api_key)

# --- Input Validation Function ---

def is_gibberish(text, min_words=3, gibberish_threshold=0.6):
    """
    Checks if the input text is likely gibberish.

    Args:
        text: The input text string.
        min_words: Minimum number of words expected.
        gibberish_threshold:  The proportion of "words" that need to be
            non-alphanumeric to be considered gibberish.

    Returns:
        True if the text is likely gibberish, False otherwise.
    """
    text = text.strip()
    if not text:  # Empty string is considered gibberish
        return True

    words = text.split()
    if len(words) < min_words:  # Check for minimum word count
        return True

    non_alphanumeric_count = 0
    for word in words:
        # Remove punctuation for a more accurate check
        word = re.sub(r'[^\w\s]', '', word)
        if not word.isalnum():
            non_alphanumeric_count += 1

    # Calculate the proportion of non-alphanumeric "words"
    gibberish_proportion = non_alphanumeric_count / len(words)
    return gibberish_proportion > gibberish_threshold


# --- Premade Answers ---
PREMADE_ANSWERS = {
    "name": "Alex",
    "q1": "I enjoy math, physics, and computer science.",
    "q2": "I prefer a hybrid work environment, combining WFH and office time.",
    "q3": "I like playing video games, coding small projects, and hiking.",
    "q4": "People say I'm analytical, detail-oriented, and a good problem-solver. I agree with that.",
    "q5": "I'm good at logical reasoning, programming, and learning new technical concepts.",
    "q6": "I prefer working in a team and enjoy both leading and supporting roles.",
    "q7": "Yes, I am very comfortable with continuous learning and adapting to new trends.",
}

# --- Initialize Session State ---  THIS IS THE KEY PART
if "messages" not in st.session_state:
    st.session_state.messages = []

if "premade_applied" not in st.session_state:
    st.session_state.premade_applied = False

# Initialize form input values in session state *if they don't exist*
for key in PREMADE_ANSWERS:
    if key not in st.session_state:
        st.session_state[key] = ""

# --- Load Demo Data Function --- (Keep the function definition!)
def apply_premade_answers():
    """Applies the premade answers to the session state."""
    st.session_state.premade_applied = True
    for key, value in PREMADE_ANSWERS.items():
        st.session_state[key] = value

# --- Clear Chat Function ---  (Keep the function definition!)
def clear_chat():
    """Clears the chat history in session state."""
    st.session_state.messages = []
    for key in PREMADE_ANSWERS:
        st.session_state[key] = ""
    st.session_state.premade_applied = False

# --- Buttons (Truly side-by-side) ---
st.write(" ")  # Add a small space for visual separation if needed.
button_container = st.container() # Create a container

with button_container:
    load_button, clear_button = st.columns([.5, .5]) # Use columns, but *inside* the container

    with load_button:
        if st.button("Load Demo Data", use_container_width=True):
            apply_premade_answers()

    with clear_button:
        if st.button("Clear Chat", use_container_width=True):
            clear_chat()

with st.form("student_profile"):
    st.subheader("Tell us about yourself:")

    name = st.text_input("Your Name (Optional):", key="name")
    q1 = st.text_area("1. What subjects do you like?", key="q1")
    q2 = st.text_area("2. Which environment do you prefer working in?", key="q2")
    q3 = st.text_area("3. What activities do you enjoy the most (hobbies)?", key="q3")
    q4 = st.text_area("4. What do people say about your personality?", key="q4")
    q5 = st.text_area("5. What activities are you naturally good at?", key="q5")
    q6 = st.text_area("6. Do you prefer working alone or in a team?", key="q6")
    q7 = st.text_area("7. Are you comfortable with continuous learning?", key="q7")

    submitted = st.form_submit_button("Explore My Options!")


# --- Display Previous Conversation ---

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Initial Prompt (After Form Submission) ---
if submitted:
    inputs = [st.session_state.q1, st.session_state.q2, st.session_state.q3, st.session_state.q4, st.session_state.q5, st.session_state.q6, st.session_state.q7]
    if not all(inputs):
        st.warning("Please answer all the questions.")
    else:
        gibberish_detected = False
        for i, input_text in enumerate(inputs):
            if is_gibberish(input_text):
                st.error(f"Your answer to question {i+1} seems unclear.  Please provide a more detailed and meaningful response.")
                gibberish_detected = True
                break

        if not gibberish_detected:
            initial_prompt = (
                f"Student Profile:\n"
                f"Name: {st.session_state.name if st.session_state.name else 'A student'}\n\n"
                f"1. Liked Subjects: {st.session_state.q1}\n"
                f"2. Preferred Work Environment: {st.session_state.q2}\n"
                f"3. Hobbies: {st.session_state.q3}\n"
                f"4. Personality (Others' and Self-Perception): {st.session_state.q4}\n"
                f"5. Natural Talents: {st.session_state.q5}\n"
                f"6. Teamwork Preference: {st.session_state.q6}\n"
                f"7. Adaptability to Learning: {st.session_state.q7}\n\n"
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

# --- Subsequent Chat Input ---

if prompt := st.chat_input("Ask a follow-up question..."):
    if is_gibberish(prompt):
        st.error("Please enter a clear and meaningful question in the navigational section.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            initial_user_message = None
            initial_assistant_message = None
            for i in range(len(st.session_state.messages) - 1):
                if st.session_state.messages[i]['role'] == 'user' and st.session_state.messages[i + 1]['role'] == 'assistant':
                    initial_user_message = st.session_state.messages[i]
                    initial_assistant_message = st.session_state.messages[i + 1]
                    break

            history = []
            if initial_user_message and initial_assistant_message:
                history.append({"role": initial_user_message["role"], "parts": [initial_user_message["content"]]})
                history.append({"role": initial_assistant_message["role"], "parts": [initial_assistant_message["content"]]})
            for i in range(len(st.session_state.messages) - 1):
                if st.session_state.messages[i]['role'] != 'model':
                    history.append({"role": st.session_state.messages[i]['role'], "parts": [st.session_state.messages[i]['content']]})

            model = genai.GenerativeModel('gemini-1.5-pro-002')
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