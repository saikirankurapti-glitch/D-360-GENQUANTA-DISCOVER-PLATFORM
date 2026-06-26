import requests

url = "http://localhost:8001/api/v1/auth/login"
data = {
    "email": "admin@analytix.com",
    "password": "AnalytiXDiscover2026!"
}

print(f"Sending request to {url} with data: {data}")
try:
    # FastAPI OAuth2 Password Bearer usually expects Form data (x-www-form-urlencoded)
    response = requests.post(url, data=data, timeout=5)
    print(f"Form-data response status: {response.status_code}")
    print(f"Form-data response body: {response.text}")
except Exception as e:
    print(f"Form-data request failed: {e}")

try:
    # Or JSON payload
    response = requests.post(url, json=data, timeout=5)
    print(f"JSON response status: {response.status_code}")
    print(f"JSON response body: {response.text}")
except Exception as e:
    print(f"JSON request failed: {e}")
