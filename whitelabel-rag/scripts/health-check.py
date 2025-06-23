import requests

def check_health():
    url = "http://localhost:10000/api/health"
    response = None
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("Health check passed:", response.json())
        else:
            print("Health check failed with status code:", response.status_code)
    except Exception as e:
        print("Health check error:", str(e))

if __name__ == "__main__":
    check_health()
