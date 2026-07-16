import json
import time
import subprocess
from datetime import datetime
import pytz

# Setup Indian Standard Timezone
IST = pytz.timezone('Asia/Kolkata')

def get_current_ist():
    return datetime.now(IST)

def run_command(command):
    """Executes a shell command and returns the output."""
    result = subprocess.run(command, shell=True, text=True, capture_output=True)
    return result.stdout.strip(), result.stderr.strip()

def trigger_workflow(workflow_file):
    """Triggers a GitHub workflow using the GitHub CLI (gh)."""
    print(f"[{get_current_ist().strftime('%Y-%m-%d %H:%M:%S')}] Triggering workflow: {workflow_file}", flush=True)
    cmd = f"gh workflow run {workflow_file} --ref main"
    out, err = run_command(cmd)
    if err:
        print(f"Error triggering workflow: {err}", flush=True)
        return None
    
    # Wait for GitHub to register the run, then fetch the Run ID
    time.sleep(15)
    id_cmd = f"gh run list --workflow={workflow_file} --limit=1 --json databaseId --jq '..databaseId'"
    run_id, _ = run_command(id_cmd)
    return run_id

def monitor_workflow(run_id, workflow_file):
    """Monitors a workflow run. Runs rerun.py and cancels the run if it exceeds 5 hours."""
    start_time = time.time()
    five_hours_in_seconds = 5 * 60 * 60

    print(f"Monitoring Workflow Run ID: {run_id} for {workflow_file}", flush=True)
    
    while True:
        elapsed_time = time.time() - start_time
        print(f"Checking status... Elapsed time for this job: {elapsed_time / 3600:.2f} hours", flush=True)
        
        # Check if the workflow has hit or crossed the 5-hour mark
        if elapsed_time >= five_hours_in_seconds:
            print(f"⚠️ Alert: Workflow {workflow_file} (Run ID: {run_id}) has reached the 5-hour limit!", flush=True)
            
            # 1. Execute the rerun.py script synchronously (Using python3 explicitly for Linux compatibility)
            print("Executing rerun.py at root directory...", flush=True)
            result = subprocess.run(["python3", "-u", "rerun.py"], text=True, capture_output=True)
            print(f"rerun.py output stdout:\n{result.stdout}", flush=True)
            print(f"rerun.py output stderr:\n{result.stderr}", flush=True)
            
            # 2. Check if rerun.py succeeded (Exit code 0 means success)
            if result.returncode == 0:
                print("✅ rerun.py finished successfully. Proceeding to eliminate the workflow...", flush=True)
                
                # 3. Eliminate/Cancel the running target workflow
                print(f"Eliminating workflow run {run_id}...", flush=True)
                cancel_cmd = f"gh run cancel {run_id}"
                c_out, c_err = run_command(cancel_cmd)
                if c_err:
                    print(f"Error cancelling workflow via GitHub CLI: {c_err}", flush=True)
                else:
                    print(f"Successfully eliminated workflow {workflow_file}.", flush=True)
            else:
                print(f"❌ rerun.py failed to execute cleanly (Exit code: {result.returncode}). Aborting workflow termination.", flush=True)
            
            break

        # Check GitHub status of the workflow
        status_cmd = f"gh run view {run_id} --json status,conclusion"
        status_json, _ = run_command(status_cmd)
        
        try:
            status_data = json.loads(status_json)
            status = status_data.get("status")
            conclusion = status_data.get("conclusion")
            
            # If it finished naturally before 5 hours, exit tracking loop
            if status == "completed":
                print(f"Workflow {workflow_file} finished naturally with conclusion: {conclusion}", flush=True)
                break
        except Exception as e:
            # Logs temporary network dropouts or API rate-limits without breaking the loop
            print(f"Temporary GitHub API status checking glitch: {e}. Retrying...", flush=True)

        time.sleep(60) # Check status every 1 minute

def check_and_execute_jobs():
    """Reads config.json and runs any workflow matching the 5-minute window."""
    try:
        with open("config.json", "r") as f:
            schedules = json.load(f)
    except Exception as e:
        print(f"Error reading config.json: {e}", flush=True)
        return

    now_ist = get_current_ist()
    print(f"\n⏰ Checking schedules at {now_ist.strftime('%H:%M:%S')} IST...", flush=True)
    
    for item in schedules:
        target_time = datetime.strptime(item["time_ist"], "%H:%M").time()
        target_dt = IST.localize(datetime.combine(now_ist.date(), target_time))
        
        # Calculate time difference in minutes
        time_difference = (now_ist - target_dt).total_seconds() / 60
        
        # If current time is within 0 to 5 minutes past the target time
        if 0 <= time_difference <= 5:
            print(f"🎯 Match found! {item['workflow_file']} is scheduled for {item['time_ist']}.", flush=True)
            run_id = trigger_workflow(item["workflow_file"])
            if run_id:
                monitor_workflow(run_id, item["workflow_file"])
            break 

def main():
    print("🚀 Long-running master scheduler started via Python loop engine...", flush=True)
    
    while True:
        check_and_execute_jobs()
        
        # Sleep for exactly 5 minutes (300 seconds) before checking again
        print("Sleeping for 5 minutes...", flush=True)
        time.sleep(300)

if __name__ == "__main__":
    main()
