import requests
import sys

# Constants
BASE_URL = "http://127.0.0.1:8006"
LOGIN_URL = f"{BASE_URL}/login/"
FORM_URL = f"{BASE_URL}/requests/new/"
USERNAME = "testuser"
PASSWORD = "password"

session = requests.Session()

# Get Login Page -> CSRF
try:
    response = session.get(LOGIN_URL)
    response.raise_for_status()
    if 'csrftoken' in session.cookies:
        csrf_token = session.cookies['csrftoken']
    else:
        # try to parse from hidden input if cookie not set (unlikely for django)
        print("Warning: csrftoken cookie not found, might fail on POST")
        csrf_token = ""
        
    print(f"Got Login Page. Cookie: {session.cookies.get_dict()}")
except Exception as e:
    print(f"Failed to get login page: {e}")
    sys.exit(1)

# Login
login_data = {
    'username': USERNAME,
    'password': PASSWORD,
    'csrfmiddlewaretoken': csrf_token,
    'next': '/requests/new/'
}
headers = {'Referer': LOGIN_URL}
try:
    response = session.post(LOGIN_URL, data=login_data, headers=headers)
    response.raise_for_status()
    # Check if redirected or content indicates login success
    if "Log in" in response.text and "Log Out" not in response.text:
       print("Login failed (text 'Log in' found, 'Log Out' not found)")
       # print(response.text[:500])
       sys.exit(1)
    print("Login successful or redirected")
except Exception as e:
    print(f"Failed to login: {e}")
    sys.exit(1)

# Get Request Form
try:
    response = session.get(FORM_URL)
    response.raise_for_status()
    content = response.text
    print(f"Got form page: {response.url}")
except Exception as e:
    print(f"Failed to get form page: {e}")
    sys.exit(1)

# Verify Fields
missing = []
required_inputs = [
    'name="firstname_th"', 
    'name="lastname_th"', 
    'name="firstname_en"', 
    'name="lastname_en"',
    'name="prefix"',
    'name="prefix_other"'
]

for required in required_inputs:
    if required not in content:
        missing.append(required)

if missing:
    print(f"FAILED: Missing fields in form: {missing}")
    sys.exit(1)

print("SUCCESS: All required fields found in form.")
