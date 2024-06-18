import requests
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Define the static IP and port of your Flask API
API_BASE_URL = 'http://81.16.12.92:80'

# Register a new user
def register_user(username, password):
    url = f"{API_BASE_URL}/register"
    payload = {
        'UserName': username,
        'Password': password
    }
    response = requests.post(url, json=payload)
    logging.debug(f"Register response: {response.text}")
    if response.status_code == 201:
        print(f"User '{username}' registered successfully.")
    else:
        print(f"Failed to register user '{username}': {response.json()}")

# Login with existing user
def login_user(username, password):
    url = f"{API_BASE_URL}/login"
    payload = {
        'username': username,
        'password': password
    }
    response = requests.post(url, json=payload)
    logging.debug(f"Login response: {response.text}")
    if response.status_code == 200:
        access_token = response.json().get('access_token')
        print(f"User '{username}' logged in successfully. Access token: {access_token}")
        return access_token
    else:
        print(f"Failed to login user '{username}': {response.json()}")
        return None

# Download a file
def download_file(access_token, filename):
    url = f"{API_BASE_URL}/download"
    headers = {
        'Authorization': access_token
    }
    params = {
        'filename': filename
    }
    response = requests.get(url, headers=headers, params=params)
    logging.debug(f"Download response: {response.status_code}, {response.content}")
    if response.status_code == 200:
        with open(filename, 'wb') as file:
            file.write(response.content)
        print(f"File '{filename}' downloaded successfully.")
    else:
        print(f"Failed to download file '{filename}': {response.json()}")

if __name__ == '__main__':
    # Register a new user
    register_user('testuser', 'testpassword')

    # Login with the new user
    token = login_user('testuser', 'testpassword')

    # Download a file using the obtained access token
    if token:
        download_file(token, 'testfile.exe')
