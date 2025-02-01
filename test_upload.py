import requests

def test_upload():
    url = 'http://localhost:5000/upload-resume'
    
    # Replace with path to your test PDF
    files = {'resume': open('path/to/your/resume.pdf', 'rb')}
    
    response = requests.post(url, files=files)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

if __name__ == "__main__":
    test_upload() 