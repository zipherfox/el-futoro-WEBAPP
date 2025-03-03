import pandas as pd

# Load the Excel file containing min/max TCAS scores
file_path = r"Untitled_spreadsheet.xlsx"  # Make sure this path is correct!
try:
    df = pd.read_excel(file_path, engine="openpyxl")  
except FileNotFoundError:
    print(f"Error: File not found at path: {file_path}")
    exit()
except Exception as e:
    print(f"Error loading Excel file: {e}")
    exit()


# Ensure required columns exist
required_columns = ["University", "Faculty", "Submajor", "คะแนนต่ำสุด หลังประมวลผลรอบ 2", "คะแนนสูงสุด หลังประมวลผลรอบ 2"]
missing_columns = [col for col in required_columns if col not in df.columns]

if missing_columns:
    print(f"\nError: The following required columns are missing from the dataset: {missing_columns}")
    exit()

def check_score(university_name, faculty_name, submajor_name, user_score):
    # Filter by university
    filtered_df = df[df["University"].astype(str) == university_name]
    
    if filtered_df.empty:
        print("\nNo matching university found. Please check the name and try again.")
        return
    
    # Filter by faculty
    faculty_filtered_df = filtered_df[filtered_df["Faculty"].astype(str) == faculty_name]
    
    if faculty_filtered_df.empty:
        print("\nNo matching faculty found. Please check the name and try again.")
        return
    
    # Filter by submajor
    submajor_filtered_df = faculty_filtered_df[faculty_filtered_df["Submajor"].astype(str) == submajor_name]
    
    if submajor_filtered_df.empty:
        print("\nNo exact match found for this submajor. Please check the name and try again.")
        return
    
    # Extract min/max scores
    try:
        min_score = float(submajor_filtered_df["คะแนนต่ำสุด หลังประมวลผลรอบ 2"].values[0])
        max_score = float(submajor_filtered_df["คะแนนสูงสุด หลังประมวลผลรอบ 2"].values[0])
    except ValueError:
        print("\nError: Score data is missing or invalid.")
        return

    # Compare TCAS score
    print(f"\nYour TCAS Score: {user_score}")
    print(f"Min Required Score: {min_score}")
    print(f"Max Accepted Score: {max_score}")

    if user_score < min_score:
        print("Result: ❌ No (Below required score)")
        return "Fail"
    elif min_score <= user_score < max_score:
        print("Result: ✅ Yes (Within range)")
        return "Pass"
    else:
        print("Result: 🎉 Yeahhhh (Above max score)")
        return "Excellent"

if __name__ == "__main__":
    print("This script is designed to be called from score.py, not run directly.")
