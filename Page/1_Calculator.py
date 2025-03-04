import streamlit as st
from score import FacultyScoreCalculator, chula_data, kmitl_data
import score_range
import streamlit.components.v1 as components

# --- Helper Functions ---

def get_score_status_message(status):
    if status == "Pass":
        return "Your score is within the acceptable range. 👍", "success"
    elif status == "Fail":
        return "Your score is NOT within the acceptable range. 🙁", "error"
    elif status == "Excellent":
        return "Your score is above the maximum accepted score. Congratulations! 🎉", "success"
    else:
        return "Score range data not found. 🤔", "warning"


# --- Streamlit App ---

st.title("🎓 Faculty Score Calculator")
st.write("Calculate your chances of getting into your dream faculty!")

# --- Sidebar for University and Faculty Selection ---

with st.sidebar:
    st.header("⚙️ Settings")
    university = st.selectbox("Select University", FacultyScoreCalculator.available_universities(),  index=0)
    calculator = FacultyScoreCalculator(university, None)
    faculty = st.selectbox("Select Faculty", calculator.available_faculties(), index=0)

    sub_major = None
    if university == "chula" and faculty in chula_data and isinstance(chula_data[faculty], dict):
        sub_major = st.selectbox("Select Sub-Major", list(chula_data[faculty].keys()))
    elif university == "kmitl" and faculty in kmitl_data and isinstance(kmitl_data[faculty], dict):
        sub_major = st.selectbox("Select Sub-Major", list(kmitl_data[faculty].keys()))
    calculator = FacultyScoreCalculator(university, faculty, sub_major)

# --- GPAX Input (Dynamically Updated) ---
gpax_required = calculator.criteria.get("GPAX")
if gpax_required is not None:
    with st.expander("GPAX", expanded=True):
        gpax_col, help_col = st.columns([3,1])
        with gpax_col:
            gpax = st.number_input(
                f"Enter your GPAX (Minimum: {gpax_required}, Maximum: 4.0)",
                min_value=0.0,
                max_value=4.0,
                step=0.01,
                format="%.2f",
                key="gpax_input",   
            )

        # Check if GPAX has been entered *and* is below the minimum.
        if gpax is not None and gpax < gpax_required:
            st.error(f"Your GPAX must be at least {gpax_required}.")
        elif gpax is not None and gpax > 4.0:
            st.error("GPAX cannot exceed 4.0.")
        elif gpax is not None:
            calculator.scores["GPAX"] = gpax

# --- Score Inputs (Dynamic) ---
st.subheader("📝 Enter Your Scores")
score_inputs_container = st.container()
with score_inputs_container:
    score_cols = st.columns(len(calculator.criteria) - (1 if gpax_required is not None else 0))
    col_index = 0
    for subject, weight in calculator.criteria.items():
        if subject != "GPAX":
            with score_cols[col_index]:
                step_value = 1.0
                if subject in ("TGAT1", "TGAT2", "TGAT3", "TPAT1", "TPAT2", "TPAT3", "TPAT4", "TPAT5"):
                    step_value = 5.0
                elif subject.startswith("A-Level"):
                    step_value = 2.0

                score = st.number_input(
                    f"{subject} (0-100)",
                    min_value=0.0,
                    max_value=100.0,
                    step=step_value,
                    format="%.1f",
                    key=f"{subject}_score",
                )
                calculator.scores[subject] = score
                col_index = (col_index + 1) % len(score_cols)

# --- Calculate Button and Results ---
calculate_button_col, result_col = st.columns([1, 3])
with calculate_button_col:
    if st.button("Calculate Score", type="primary", use_container_width=True):
        result = calculator.calculate_score()

        if result is not None:
            with result_col:
                st.metric(
                    label=f"Calculated Score for {faculty} ({sub_major if sub_major else ''}) at {university}",
                    value=f"{result:.2f}",
                )
            status = score_range.check_score(university, faculty, sub_major, result)
            message, message_type = get_score_status_message(status)
            with result_col:
                if message_type == "success":
                    st.success(message)
                elif message_type == "error":
                    st.error(message)
                else:
                    st.warning(message)

            # --- Inject JavaScript for console.log ---
            js_code = f"""
            <script>
            console.log("Calculated Score: {result}");
            console.log("Score Check Status: {status}");
            </script>
            """
            components.html(js_code, height=0)
        else:
            with result_col:
                st.error("Unable to calculate score due to invalid data.")