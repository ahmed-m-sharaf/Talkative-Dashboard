import os
import sys
import time
import subprocess
import requests
import pytest

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_URL = "http://127.0.0.1:8005"
API_PROCESS = None

def start_api_server():
    global API_PROCESS
    # Check if already running
    try:
        r = requests.get(f"{BASE_URL}/api/health", timeout=1)
        if r.status_code == 200:
            print("API server is already running on port 8005.")
            return
    except requests.RequestException:
        pass

    print("Starting API server dynamically...")
    env = os.environ.copy()
    API_PROCESS = subprocess.Popen(
        ["/home/sharaf/enviroments/ai_latest/bin/python", "-m", "uvicorn", "api:app", "--port", "8005", "--host", "127.0.0.1"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    # Wait for server to be ready
    for _ in range(10):
        time.sleep(1)
        try:
            r = requests.get(f"{BASE_URL}/api/health", timeout=1)
            if r.status_code == 200:
                print("API server successfully started.")
                return
        except requests.RequestException:
            pass
    raise RuntimeError("Failed to start FastAPI API server on port 8005.")

def stop_api_server():
    global API_PROCESS
    if API_PROCESS:
        print("Stopping API server...")
        API_PROCESS.terminate()
        API_PROCESS.wait()
        API_PROCESS = None
        print("API server stopped.")

@pytest.fixture(scope="module", autouse=True)
def manage_server():
    start_api_server()
    yield
    stop_api_server()

def test_health_check():
    """Verify GET /api/health works correctly."""
    response = requests.get(f"{BASE_URL}/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_valid_request():
    """Verify POST /api/chat with a valid recruitment prompt works."""
    payload = {"prompt": "average age of Software Engineers"}
    response = requests.post(f"{BASE_URL}/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "metadata" in data
    assert "intent_mapping" in data
    assert "execution_result" in data
    assert data["intent_mapping"]["target_endpoint"] == "average_age"

def test_invalid_request_empty():
    """Verify POST /api/chat with empty prompt returns 400 error."""
    payload = {"prompt": ""}
    response = requests.post(f"{BASE_URL}/api/chat", json=payload)
    assert response.status_code == 400
    assert "detail" in response.json()

def test_invalid_json():
    """Verify POST /api/chat with malformed JSON returns 422 validation error."""
    headers = {"Content-Type": "application/json"}
    bad_data = "{prompt: average age of software engineers"  # malformed JSON
    response = requests.post(f"{BASE_URL}/api/chat", data=bad_data, headers=headers)
    assert response.status_code == 422

def test_unsupported_prompt():
    """Verify POST /api/chat with unsupported prompt returns unknown intent response."""
    payload = {"prompt": "who won the soccer world cup?"}
    response = requests.post(f"{BASE_URL}/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["intent_mapping"]["target_endpoint"] == "unknown"
    assert data["execution_result"]["status"] == "UNKNOWN_INTENT"

def test_missing_parameters():
    """Verify POST /api/chat with missing intent parameters (missing job role) returns prompt error."""
    payload = {"prompt": "what is the average age?"}
    response = requests.post(f"{BASE_URL}/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    # Missing required parameters yields UNKNOWN_INTENT/Clarification or a warning
    assert "validation" in data["execution_result"]["status"].lower() or "unknown" in data["intent_mapping"]["target_endpoint"].lower()
