# %% [code]
# %% [code]
import os
import subprocess
import sys
import time
import datetime
import asyncio
import requests
from kaggle_secrets import UserSecretsClient

# 1. DEPENDENCY AUTOPREPARATION
try:
    import requests
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "-q"])
    import requests

# 2. DEFINED MULTI-WORKFLOW MATRIX
WORKFLOW_SCHEDULE = [
    {
        "target_time_ist": "06:45",
        "workflow_file": "populate_queue.yml",
        "repo_owner": "My-Memory-2008",
        "repo_name": "content-factory-orchestrator-2"
    },
    {
        "target_time_ist": "07:01",
        "workflow_file": "run_factory.yml",
        "repo_owner": "My-Memory-2008",
        "repo_name": "content-factory-orchestrator-2"
    },
    {
        "target_time_ist": "12:30",
        "workflow_file": "populate_queue.yml",
        "repo_owner": "My-Memory-2008",
        "repo_name": "content-factory-orchestrator-2"
    },
    {
        "target_time_ist": "12:45",
        "workflow_file": "run_factory.yml",
        "repo_owner": "My-Memory-2008",
        "repo_name": "content-factory-orchestrator-2"
    },
    {
        "target_time_ist": "17:45",
        "workflow_file": "populate_queue.yml",
        "repo_owner": "My-Memory-2008",
        "repo_name": "content-factory-orchestrator-2"
    },
    {
        "target_time_ist": "18:02",
        "workflow_file": "run_factory.yml",
        "repo_owner": "My-Memory-2008",
        "repo_name": "content-factory-orchestrator-2"
    }
]

# 3. IDENTIFICATION CREDENTIALS
print("🔐 Loading environment & secrets...")
secrets = UserSecretsClient()
GITHUB_USER = secrets.get_secret("GITHUB_USERNAME")
GITHUB_PASS = secrets.get_secret("GITHUB_PASSWORD")

# Try to load either token variation safely
GITHUB_TOKEN = secrets.get_secret("GH_TOKEN")

# Core Execution Variables
start_time = time.time()
MAX_RUN_TIME = 11.975 * 60 * 60   # 11.975 Hours execution threshold
CHECK_INTERVAL = 5 * 60      # 5 Minute clock validation loop

async def run_github_workflow_via_api(repo_owner, repo_name, workflow_file, token):
    """Securely dispatches a workflow run event via the standard GitHub REST API"""
    print(f"🚀 Dispatching GitHub REST API request for {workflow_file}...")
    
    if not token:
        print("❌ Error: Missing GH_TOKEN or GITHUB_TOKEN environment secret slot!")
        return False

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    loop = asyncio.get_event_loop()

    # ====================================================================
    # NEW AUTOMATED DEBUG STEP: DYNAMICALLY DETECT THE DEFAULT BRANCH
    # ====================================================================
    repo_info_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
    try:
        repo_response = await loop.run_in_executor(
            None, 
            lambda: requests.get(repo_info_url, headers=headers, timeout=15)
        )
        if repo_response.status_code == 200:
            detected_branch = repo_response.json().get("default_branch", "main")
            print(f"📡 System scanned repository! Default branch identified as: '{detected_branch}'")
        else:
            print(f"⚠️ Branch scanning warning ({repo_response.status_code}). Falling back to 'main'.")
            detected_branch = "main"
    except Exception as e:
        print(f"⚠️ Branch retrieval error: {e}. Defaulting to 'main'.")
        detected_branch = "main"

    # The REST API Endpoints URL for workflow dispatch actions
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/actions/workflows/{workflow_file}/dispatches"
    
    # We dynamically pass the verified repository branch
    payload = {
        "ref": detected_branch,
        "inputs": {}
    }
    
    try:
        response = await loop.run_in_executor(
            None, 
            lambda: requests.post(url, headers=headers, json=payload, timeout=30)
        )
        
        # GitHub REST returns 204 No Content upon a successful execution start
        if response.status_code == 204:
            print(f"✅ API Success! Remote workflow '{workflow_file}' successfully triggered via {detected_branch}.")
            return True
        else:
            print(f"❌ API Dispatch Rejected! Server response: {response.status_code}")
            # If the response isn't plain HTML, print the clean JSON validation text block
            if "application/json" in response.headers.get("Content-Type", ""):
                print(f"📄 Validation details: {response.json()}")
            else:
                print(f"📄 Response summary text snippet: {response.text[:300]}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to reach GitHub API endpoints: {e}")
        return False

async def main_loop():
    print("=== Independent Script GitHub REST API Scheduler Engine Initialized ===")
    
    while True:
        elapsed = time.time() - start_time
        
        # CONDITION A: 7-Hour Self Healing Check
        if elapsed >= MAX_RUN_TIME:
            print("\n[Baton Handover] 7 Hours reached! Calling self-healing API routine...")
            await run_github_workflow_via_api(
                "My-Memory-2008", 
                "content-factory-orchestrator-1", 
                "scheduler-controller.yml", 
                GITHUB_TOKEN
            )
            break

        # CONDITION B: Time Check Frame
        ist_now = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=5, minutes=30)
        current_time_ist = ist_now.strftime("%H:%M")
        
        print(f"[{current_time_ist}] Scanning script task arrays...")
        
        curr_h, curr_m = map(int, current_time_ist.split(":"))
        curr_total_minutes = curr_h * 60 + curr_m

        for task in WORKFLOW_SCHEDULE:
            target_h, target_m = map(int, task["target_time_ist"].split(":"))
            target_total_minutes = target_h * 60 + target_m
            time_difference = curr_total_minutes - target_total_minutes
            
            if 0 <= time_difference < 5:
                print(f"   -> Match confirmed! Current time intersects with scheduling rules.")
                await run_github_workflow_via_api(
                    task["repo_owner"], 
                    task["repo_name"], 
                    task["workflow_file"], 
                    GITHUB_TOKEN
                )

        await asyncio.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    loop.run_until_complete(main_loop())
