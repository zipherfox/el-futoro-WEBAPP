import streamlit as st
from score import FacultyScoreCalculator, chula_data, kmitl_data  # Import your class and data
import score_range

st.title("Faculty Score Calculator")

# University Selection
university = st.selectbox("Select University", FacultyScoreCalculator.available_universities())

# Faculty Selection
calculator = FacultyScoreCalculator(university, None)  # Create instance for faculty list
faculty = st.selectbox("Select Faculty", calculator.available_faculties())

# Sub-major Selection (Conditional)
sub_major = None
if university == "chula" and faculty in chula_data and isinstance(chula_data[faculty], dict):
    sub_major = st.selectbox("Select Sub-Major", list(chula_data[faculty].keys()))
elif university == "kmitl" and faculty in kmitl_data and isinstance(kmitl_data[faculty], dict):
    sub_major = st.selectbox("Select Sub-Major", list(kmitl_data[faculty].keys()))

# Create Calculator Instance
calculator = FacultyScoreCalculator(university, faculty, sub_major)

# GPAX Input (with check)
gpax_required = calculator.criteria.get("GPAX")
if gpax_required is not None:
    gpax = st.number_input(f"Enter your GPAX (Minimum required: {gpax_required}, Maximum allowed: 4.0)", min_value=0.0, max_value=4.0, step=0.01)
    if gpax < gpax_required:
        st.error(f"Your GPAX must be at least {gpax_required}. You cannot enter this faculty.")
        st.stop()  # Stop execution if GPAX is too low
    elif gpax > 4.0:
        st.error("GPAX cannot be greater than 4.0")
        st.stop()
    else:
        calculator.scores["GPAX"] = gpax


# Score Inputs
for subject, weight in calculator.criteria.items():
    if subject != "GPAX":
        score = st.number_input(f"Enter score for {subject} (0-100):", min_value=0.0, max_value=100.0, step=0.1, key=subject)
        calculator.scores[subject] = score

# Calculate Score
if st.button("Calculate Score"):
    result = calculator.calculate_score()

    if result is not None:
        st.success(f"Calculated score for {faculty} ({sub_major if sub_major else ''}) at {university}: {result}")
        # --- Integrate score_range check ---
        status = score_range.check_score(university, faculty, sub_major, result)
        if status == "Pass":
            st.success("Your score is within the acceptable range.")
        elif status == "Fail":
            st.error("Your score is NOT within the acceptable range.")
        elif status == "Excellent":
            st.success("Your score is above the maximum accepted score. Congratulations!")
        else:
            st.warning("Score range data not found.")

    else:
        st.error("Unable to calculate score due to invalid data.")