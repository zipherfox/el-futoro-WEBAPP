import streamlit as st
from score import FacultyScoreCalculator, chula_data, kmitl_data
import score_range

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

# st.set_page_config(page_title="Faculty Score Calculator", page_icon="🎓", layout="wide")  # REMOVE THIS LINE

st.title("🎓 Faculty Score Calculator")
st.write("Calculate your chances of getting into your dream faculty!")

# --- Sidebar for University and Faculty Selection ---

with st.sidebar:
    st.header("⚙️ Settings")
    university = st.selectbox("Select University", FacultyScoreCalculator.available_universities(),  index=0)
    # --- Removed print here ---

    # Create instance for faculty list
    calculator = FacultyScoreCalculator(university, None)
    faculty = st.selectbox("Select Faculty", calculator.available_faculties(), index=0)
    # --- Removed print here ---


    # Sub-major Selection (Conditional)
    sub_major = None
    if university == "chula" and faculty in chula_data and isinstance(chula_data[faculty], dict):
        sub_major = st.selectbox("Select Sub-Major", list(chula_data[faculty].keys()))
    elif university == "kmitl" and faculty in kmitl_data and isinstance(kmitl_data[faculty], dict):
        sub_major = st.selectbox("Select Sub-Major", list(kmitl_data[faculty].keys()))

    # --- Removed print here ---

    # Create Calculator Instance (after faculty and sub-major selection)
    calculator = FacultyScoreCalculator(university, faculty, sub_major)
    # --- Removed print here ---


# --- Main Content Area ---

# --- GPAX Input ---
gpax_required = calculator.criteria.get("GPAX")
if gpax_required is not None:
    with st.expander("GPAX", expanded=True):  # Use an expander
        gpax_col, help_col = st.columns([3,1])
        with gpax_col:
          gpax = st.number_input(
              f"Enter your GPAX (Minimum: {gpax_required}, Maximum: 4.0)",
              min_value=0.0,
              max_value=4.0,
              step=0.01,  # Keep step at 0.01 for GPAX
              format="%.2f",
              key="gpax_input",  # Add key for clarity
          )
        with help_col:
            st.info(f"Minimum required: {gpax_required}")

        # --- Removed print here ---

        if gpax < gpax_required:
            st.error(f"Your GPAX must be at least {gpax_required}.")
            st.stop()  # Stop execution if GPAX is too low
        elif gpax > 4.0:
            st.error("GPAX cannot be greater than 4.0")
            st.stop()
        else:
            calculator.scores["GPAX"] = gpax

# --- Score Inputs (Dynamic) ---
st.subheader("📝 Enter Your Scores")
score_inputs_container = st.container() #Create a container
with score_inputs_container:
    score_cols = st.columns(len(calculator.criteria) - (1 if gpax_required is not None else 0)) #number of subject input, exclude gpax
    col_index = 0
    for subject, weight in calculator.criteria.items():
        if subject != "GPAX":
            with score_cols[col_index]:
                # --- ADJUST STEP HERE ---
                step_value = 1.0  # Default step
                if subject in ("TGAT1", "TGAT2", "TGAT3", "TPAT1", "TPAT2", "TPAT3", "TPAT4", "TPAT5"):
                    step_value = 5.0  # Larger step for these subjects
                elif subject.startswith("A-Level"):  # Example for A-Level subjects
                    step_value = 2.0 # Different step for A-Level
                # Add more conditions as needed for different subject types

                score = st.number_input(
                    f"{subject} (0-100)",
                    min_value=0.0,
                    max_value=100.0,
                    step=step_value,  # Use the determined step value
                    format="%.1f",
                    key=f"{subject}_score",
                )
                calculator.scores[subject] = score
                print(f"Entered score for {subject}: {score}")
                col_index = (col_index + 1) % len(score_cols)


# --- Calculate Button and Results ---
calculate_button_col, result_col = st.columns([1, 3]) #columns for the button and for the result
with calculate_button_col:
    if st.button("Calculate Score", type="primary", use_container_width=True):
        # --- All debug prints moved inside the button's if block ---
        print(f"Selected University: {university}")
        print(f"Selected Faculty: {faculty}")
        if sub_major:
            print(f"Selected Sub-Major: {sub_major}")
        print(f"Calculator criteria: {calculator.criteria}")
        print(f"Entered GPAX: {gpax}")
        for subject, score in calculator.scores.items():
            if subject != "GPAX":
                 print(f"Entered score for {subject}: {score}")

        result = calculator.calculate_score()
        print(f"Calculated Score: {result}")  # Debug print

        if result is not None:
            with result_col:
                st.metric(
                    label=f"Calculated Score for {faculty} ({sub_major if sub_major else ''}) at {university}",
                    value=f"{result:.2f}",  # Format the result
                )
            # --- Integrate score_range check ---
            status = score_range.check_score(university, faculty, sub_major, result)
            print(f"Score Check Status: {status}")  # Debug print
            message, message_type = get_score_status_message(status)
            with result_col:
                if message_type == "success":
                    st.success(message)
                elif message_type == "error":
                    st.error(message)
                else:
                    st.warning(message)

        else:
          with result_col:
            st.error("Unable to calculate score due to invalid data.")