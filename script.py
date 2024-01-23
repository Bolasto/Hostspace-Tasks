import os
import requests
from google.auth.transport.requests import Request
from google.oauth2 import service_account
import time

# Variables
PROJECT_ID = "internship-task-410804"
BUILD_API_URL = f"https://cloudbuild.googleapis.com/v1/projects/{PROJECT_ID}/builds"
DOCKERFILE_PATH = "./my-app/Dockerfile"  # Update with the path to your Dockerfile
SOURCE_PATH = "./my-app"     # Update with the path to your source code

# Load Google Cloud credentials
creds = service_account.Credentials.from_service_account_file(
    "./my-app/key.json",  # Update with the path to your service account key
    scopes=["https://www.googleapis.com/auth/cloud-platform"],
)
creds.refresh(Request())

# Base64 encode the Dockerfile and source code
with open(DOCKERFILE_PATH, "rb") as dockerfile_file:
    dockerfile_content = dockerfile_file.read()

# Trigger Cloud Build
response = requests.post(
    BUILD_API_URL,
    headers={
        "Authorization": f"Bearer {creds.token}",
        "Content-Type": "application/json",
    },
    json={
        "source": {
            "storageSource": {"bucket": f"{PROJECT_ID}_cloudbuild", "object": "Test.zip"},
        },
        "steps": [
            {
                "name": "gcr.io/cloud-builders/docker",
                "args": ["build", "-t", f"gcr.io/{PROJECT_ID}/my-image", "./Test"],
            }
        ],
        "images": [f"gcr.io/{PROJECT_ID}/my-image"],
    },
)


# Check if Cloud Build was successful
if response.ok:
    build_id = response.json()["metadata"]["build"]["id"]
    print(f"Cloud Build triggered successfully. Build ID: {build_id}")

    # Wait for the build to complete
    while True:
        build_status_response = requests.get(
            f"{BUILD_API_URL}/{build_id}", headers={"Authorization": f"Bearer {creds.token}"}
        )
        build_status = build_status_response.json()["status"]

        if build_status == "QUEUED" or build_status == "WORKING":
            print(f"Build is still in progress. Status: {build_status}")
            time.sleep(10)  # Wait for 10 seconds before checking again
        else:
            print("Build completed successfully.")

            break

            # Get the artifact URL
        artifact_url = build_status_response.json()["images"][0]
        print(f"Container Artifact URL: {artifact_url}")
		
else:
    print(f"Error triggering Cloud Build: {response.text}")