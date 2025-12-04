import requests
import os

# Configuration
BASE_URL = "http://127.0.0.1:8000/api/grade/"
TEST_DATA_DIR = "/Users/vc/Library/CloudStorage/OneDrive-BIRLAINSTITUTEOFTECHNOLOGYandSCIENCE/Documents/coding/AI_exam_corrector/test_data"

def test_batch_grading():
    solution_path = os.path.join(TEST_DATA_DIR, "solution key.txt")
    student1_path = os.path.join(TEST_DATA_DIR, "ans_sheet.txt")
    student2_path = os.path.join(TEST_DATA_DIR, "ans_sheet2.txt")

    if not all(os.path.exists(p) for p in [solution_path, student1_path, student2_path]):
        print("Error: Test files not found.")
        return

    files = [
        ('solutionKey', ('solution key.txt', open(solution_path, 'rb'), 'text/plain')),
        ('studentSheet', ('ans_sheet.txt', open(student1_path, 'rb'), 'text/plain')),
        ('studentSheet', ('ans_sheet2.txt', open(student2_path, 'rb'), 'text/plain')),
    ]

    print(f"Sending request to {BASE_URL} with 1 solution key and 2 student sheets...")
    
    try:
        response = requests.post(BASE_URL, files=files)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n--- Response Data ---")
            print(f"Total Processed: {data.get('total_processed')}")
            print(f"Success Count: {data.get('success_count')}")
            print(f"Error Count: {data.get('error_count')}")
            
            results = data.get('results', [])
            for res in results:
                print(f"\nStudent: {res.get('filename')}")
                print(f"Total Score: {res.get('total_score')}")
                # print(f"Details: {res.get('graded_questions')}") # Too verbose
        else:
            print("Request failed.")
            print(response.text)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        for _, file_tuple in files:
            file_tuple[1].close()

if __name__ == "__main__":
    test_batch_grading()
