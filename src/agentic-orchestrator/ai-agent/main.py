from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import logging
import os
import tempfile
import subprocess
import requests

# Initialize FastAPI app for the Agent Endpoint
app = FastAPI(title="Self-Healing AI Agent API", version="1.0.0")

logging.basicConfig(level=logging.INFO)

# Models
class RemediationTask(BaseModel):
    task: str
    repository: str
    run_id: int
    workflow_name: str
    context: str
    triggered_by: str
    logs_url: str

def execute_agentic_patch(task_data: dict):
    """
    This function represents the core Agentic AI loop execution.
    In a fully operational production environment, this function initializes the
    Microsoft AutoGen/Azure AI SDK, providing the GPT-5.3-Codex model access to
    the local ML Compute Instance terminal and filesystem.
    """
    repo = task_data.get('repository')
    run_id = task_data.get('run_id')
    logs_url = task_data.get('logs_url')

    logging.info(f"Agent executing remediation for {repo} Run ID {run_id}")
    
    # Secure Sandbox Directory on the ML Compute Instance
    with tempfile.TemporaryDirectory(prefix=f"agent-workspace-run-{run_id}-") as work_dir:
        logging.info(f"Agent workspace initialized at: {work_dir}")
        
        # 1. Clone the repository (Using GitHub Token Injected from Env)
        github_token = os.environ.get("GITHUB_APP_TOKEN")
        if not github_token:
            logging.warning("No GITHUB_APP_TOKEN found. Agent operating in dry-run mode.")
        
        clone_url = f"https://oauth2:{github_token}@github.com/{repo}.git" if github_token else f"https://github.com/{repo}.git"
        
        try:
            # Clone Phase
            subprocess.run(["git", "clone", clone_url, work_dir], check=True, capture_output=True)
            logging.info("Repository successfully cloned into sandbox.")
            
            # 2. Context Ingestion Phase (The Agent reads the crash logs)
            # Fetching logs from GitHub using the provided URL
            headers = {"Authorization": f"Bearer {github_token}"} if github_token else {}
            log_response = requests.get(logs_url, headers=headers)
            crash_logs = log_response.text if log_response.status_code == 200 else "Failed to retrieve logs."
            
            # --- START AI INFERENCE BOUNDARY ---
            # In production, this section passes the `crash_logs` + `work_dir` path to gpt-5.3-codex
            # via AutoGen or the Azure AI SDK. The model autonomously runs `grep`,
            # finds the file, modifies it, and confirms the fix.
            logging.info("GPT-5.3-Codex ingesting logs and developing patch...")
            
            # [Pseudo-Agent Execution]
            # 1. Agent runs: `cat {work_dir}/.github/workflows/packer-build.yml`
            # 2. Agent identifies fault.
            # 3. Agent modifies file to resolve fault.
            # --- END AI INFERENCE BOUNDARY ---
            
            # 3. Commit Phase (The Agent finalizes the job natively)
            # The agent creates a new branch, commits the fix, and pushes it up.
            fix_branch = f"agent-fix-run-{run_id}"
            subprocess.run(["git", "checkout", "-b", fix_branch], cwd=work_dir, check=True)
            subprocess.run(["git", "add", "."], cwd=work_dir, check=True)
            
            # Safely check if changes were made before committing
            status = subprocess.run(["git", "status", "--porcelain"], cwd=work_dir, capture_output=True, text=True)
            if status.stdout.strip():
                subprocess.run(["git", "commit", "-m", f"fix: autonomous remediation for Run {run_id}"], cwd=work_dir, check=True)
                
                # Push the branch upstream
                if github_token:
                    subprocess.run(["git", "push", "origin", fix_branch], cwd=work_dir, check=True)
                    logging.info("Agent successfully pushed remediation patch. Re-triggering pipeline via webhook loop.")
                    
                    # 4. Trigger GitHub Actions API to rerun the workflow
                    dispatch_url = f"https://api.github.com/repos/{repo}/actions/workflows/{task_data.get('workflow_name')}/dispatches"
                    requests.post(dispatch_url, json={"ref": fix_branch}, headers=headers)
            else:
                logging.info("Agent determined no code changes were necessary.")
                
        except subprocess.CalledProcessError as e:
            logging.error(f"Agent Execution Failure: {e.stderr.decode('utf-8')}")
        except Exception as e:
            logging.error(f"Unexpected Agent Error: {str(e)}")


@app.post("/agent/remediate", status_code=202)
async def trigger_remediation(task: RemediationTask, background_tasks: BackgroundTasks):
    """
    Entrypoint for the Azure Function Orchestrator. 
    Returns HTTP 202 instantly, and places the Agent execution task in the background 
    to prevent API timeouts during complex repo clones and AI reasoning loops.
    """
    logging.info(f"Received remediation task for {task.repository} (Run ID: {task.run_id}).")
    
    # Hand off the long-running coding interaction to Background Tasks
    background_tasks.add_task(execute_agentic_patch, task.dict())
    
    return {
        "status": "Accepted", 
        "message": f"Agent dispatched to remediate {task.repository} run {task.run_id}.",
        "mode": "async"
    }
