import chulaweight  # Import Chula weight data
import kmitlweight

# Convert chulaweight list into a dictionary for easier access
chula_data = {}
for faculty_dict1 in chulaweight.chulaweight:
    chula_data.update(faculty_dict1)

kmitl_data = {}
for faculty_dict2 in kmitlweight.kmitlweight:
    kmitl_data.update(faculty_dict2)

class FacultyScoreCalculator:
    faculty_criteria = {"chula": chula_data,"kmitl": kmitl_data}  

    def __init__(self, university, faculty, sub_major=None):
        self.university = university
        self.faculty = faculty
        self.sub_major = sub_major
        
        if sub_major:
            self.criteria = self.faculty_criteria.get(university, {}).get(faculty, {}).get(sub_major, {})
        else:
            self.criteria = self.faculty_criteria.get(university, {}).get(faculty, {})
        
        self.scores = {}

    def get_valid_score(self, subject):
        while True:
            try:
                score = float(input(f"Enter score for {subject} (0-100): "))
                if 0 <= score <= 100:
                    return score
                else:
                    print("Score must be between 0 and 100.")
            except ValueError:
                print("Invalid input. Please enter a numeric value.")

    def collect_scores(self):
        for subject in self.criteria:
            if subject != "GPAX":  
                self.scores[subject] = self.get_valid_score(subject)

    def check_gpax(self):
        gpax_required = self.criteria.get("GPAX")
        if gpax_required is not None:
            while True:
                try:
                    gpax = float(input(f"Enter your GPAX (Minimum required: {gpax_required}, Maximum allowed: 4.0): "))
                    if gpax < gpax_required:
                        print(f"Your GPAX must be at least {gpax_required}. You cannot enter this faculty.")
                        return False
                    elif gpax > 4.0:
                        print("GPAX cannot be greater than 4.0. Please try again.")
                    else:
                        self.scores["GPAX"] = gpax
                        return True
                except ValueError:
                    print("Invalid input. Please enter a numeric value.")
        return True

    def calculate_score(self):
        if self.criteria:
            total_score = sum(float(self.scores.get(subject, 0)) * weight for subject, weight in self.criteria.items() if subject != "GPAX")
            return round(total_score, 2)
        return None

    @staticmethod
    def available_universities():
        return list(FacultyScoreCalculator.faculty_criteria.keys())

    def available_faculties(self):
        return list(self.faculty_criteria.get(self.university, {}).keys())

def main():
    print("\nAvailable Universities:", ", ".join(FacultyScoreCalculator.available_universities()))
    while True:
        university = input("Enter university: ").strip()
        if university in FacultyScoreCalculator.faculty_criteria:
            break
        print("Invalid university. Please choose from the list.")

    calculator = FacultyScoreCalculator(university, None)
    print("\nAvailable faculties:", ", ".join(calculator.available_faculties()))
    
    while True:
        faculty = input("Enter faculty: ").strip()
        if faculty in calculator.available_faculties():
            break
        print("Invalid faculty. Please choose from the list.")
    
    sub_major = None
    if faculty in chula_data and isinstance(chula_data[faculty], dict):
        print("\nAvailable sub-majors:", ", ".join(chula_data[faculty].keys()))
        while True:
            sub_major = input("Enter your sub-major: ").strip()
            if sub_major in chula_data[faculty]:
                break
            print("Invalid sub-major. Please choose from the list.")
    if faculty in kmitl_data and isinstance(kmitl_data[faculty], dict):
        print("\nAvailable sub-majors:", ", ".join(kmitl_data[faculty].keys()))
        while True:
            sub_major = input("Enter your sub-major: ").strip()
            if sub_major in kmitl_data[faculty]:
                break
            print("Invalid sub-major. Please choose from the list.")
    
    calculator = FacultyScoreCalculator(university, faculty, sub_major)
    if not calculator.check_gpax():
        print(f"\nYou cannot enter {faculty} ({sub_major}) at {university}. Exiting...")
        return None, None, None, None  
    
    calculator.collect_scores()
    print("\nEntered Scores:")
    for subject, score in calculator.scores.items():
        print(f"  {subject}: {score}")
    
    result = calculator.calculate_score()
    if result is not None:
        print(f"\nCalculated score for {faculty} ({sub_major}) at {university}: {result}")
        return university, faculty, sub_major, result  
    else:
        print("\nUnable to calculate score due to invalid data.")
        return None, None, None, None