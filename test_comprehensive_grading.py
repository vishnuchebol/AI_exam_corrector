import urllib.request
import urllib.error
import os
import glob
import json
import uuid

# Configuration
BASE_URL = "http://127.0.0.1:8000/api/grade/"
TEST_DATA_DIR = "/Users/vc/Library/CloudStorage/OneDrive-BIRLAINSTITUTEOFTECHNOLOGYandSCIENCE/Documents/coding/AI_exam_corrector/comprehensive_test_data"

def encode_multipart_formdata(files):
    boundary = uuid.uuid4().hex
    crlf = b'\r\n'
    data = []

    for name, (filename, content, content_type) in files:
        data.append(f'--{boundary}'.encode())
        data.append(f'Content-Disposition: form-data; name="{name}"; filename="{filename}"'.encode())
        data.append(f'Content-Type: {content_type}'.encode())
        data.append(b'')
        data.append(content)
    
    data.append(f'--{boundary}--'.encode())
    data.append(b'')
    
    body = crlf.join(data)
    content_type = f'multipart/form-data; boundary={boundary}'
    return content_type, body

def test_comprehensive_batch_grading():
    solution_path = os.path.join(TEST_DATA_DIR, "solution_key.txt")
    student_files = glob.glob(os.path.join(TEST_DATA_DIR, "student_*.txt"))
    # Also include the image files if present and testable, but currently view only handles text
    # The requirement was about student answers in text files.
    
    if not os.path.exists(solution_path):
        print(f"Error: Solution file not found at {solution_path}")
        return

    print(f"Found {len(student_files)} student files.")

    # Prepare files list
    # Format: (field_name, (filename, content_bytes, content_type))
    files_to_send = []
    
    with open(solution_path, 'rb') as f:
        files_to_send.append(('solutionKey', ('solution_key.txt', f.read(), 'text/plain')))

    for s_path in student_files:
        with open(s_path, 'rb') as f:
            files_to_send.append(('studentSheet', (os.path.basename(s_path), f.read(), 'text/plain')))

    print(f"Sending request to {BASE_URL}...")
    
    try:
        content_type, body = encode_multipart_formdata(files_to_send)
        req = urllib.request.Request(BASE_URL, data=body, headers={'Content-Type': content_type})
        
        with urllib.request.urlopen(req) as response:
            print(f"Status Code: {response.getcode()}")
            response_body = response.read()
            
            if response.getcode() == 200:
                data = json.loads(response_body)
                print("\n--- Response Data ---")
                print(f"Total Processed: {data.get('total_processed')}")
                print(f"Success Count: {data.get('success_count')}")
                print(f"Error Count: {data.get('error_count')}")
                
                if data.get('error_count') > 0:
                    print("\nErrors:")
                    for err in data.get('errors', []):
                        print(f"- {err}")

                print("\nResults:")
                results = data.get('results', [])
                results.sort(key=lambda x: x.get('filename'))
                
                for res in results:
                    print(f"Student: {res.get('filename'):<30} | Score: {res.get('total_score')}")
            else:
                print("Request failed.")
                print(response_body.decode())

    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} {e.reason}")
        print(e.read().decode())
    except urllib.error.URLError as e:
        print(f"URL Error: {e.reason}")
        print("Make sure the Django server is running on port 8000.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    test_comprehensive_batch_grading()
