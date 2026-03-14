import azure.functions as func
import logging
import json
import os
import requests
import hmac
import hashlib

app = func.FunctionApp()

# Secure Webhook Secret from GitHub App Configuration
GITHUB_WEBHOOK_SECRET = os.environ.get("GITHUB_WEBHOOK_SECRET")
# Antigravity / Agent Orchestrator Endpoint
AGENT_API_ENDPOINT = os.environ.get("AGENT_API_ENDPOINT")
AGENT_API_KEY = os.environ.get("AGENT_API_KEY")

def verify_signature(req: func.HttpRequest) -> bool:
    """Cryptographically verifies the GitHub Webhook payload signature."""
    if not GITHUB_WEBHOOK_SECRET:
        logging.warning("GITHUB_WEBHOOK_SECRET is not configured. Bypassing validation (NOT RECOMMENDED).")
        return True
        
    signature_header = req.headers.get("X-Hub-Signature-256")
    if not signature_header:
        return False
        
    sha_name, signature = signature_header.split('=')
    if sha_name != 'sha256':
        return False
        
    mac = hmac.new(GITHUB_WEBHOOK_SECRET.encode(), msg=req.get_body(), digestmod=hashlib.sha256)
    return hmac.compare_digest(mac.hexdigest(), signature)

@app.route(route="github-webhook-trigger", auth_level=func.AuthLevel.FUNCTION)
def github_webhook_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Received a GitHub Webhook Event.')
    
    if not verify_signature(req):
        return func.HttpResponse("Unauthorized: Invalid Signature", status_code=401)

    event_type = req.headers.get('X-GitHub-Event')
    if event_type != 'workflow_run':
        return func.HttpResponse(f"Ignored event type: {event_type}", status_code=200)

    try:
        payload = req.get_json()
        action = payload.get('action')
        workflow_run = payload.get('workflow_run', {})
        conclusion = workflow_run.get('conclusion')
        
        # We only want to orchestrate agents when a workflow actually FAILS
        if action == 'completed' and conclusion == 'failure':
            repo_name = payload.get('repository', {}).get('full_name')
            run_id = workflow_run.get('id')
            triggering_actor = workflow_run.get('triggering_actor', {}).get('login')
            workflow_name = workflow_run.get('name')
            html_url = workflow_run.get('html_url')
            
            logging.warning(f"CRITICAL: Workflow '{workflow_name}' (Run ID: {run_id}) in {repo_name} FAILED.")
            
            # Step 1: Synthesize the Agent Payload
            agent_payload = {
                "task": "CI/CD Remediation",
                "repository": repo_name,
                "run_id": run_id,
                "workflow_name": workflow_name,
                "context": f"The Packer CI/CD workflow run {run_id} failed. Please download the logs, analyze the crash in the provisioner or script, checkout a fix branch, push the patch, and re-trigger.",
                "triggered_by": triggering_actor,
                "logs_url": f"https://api.github.com/repos/{repo_name}/actions/runs/{run_id}/logs"
            }
            
            # Step 2: Offload to the Agentic Tier (Antigravity/Azure AI)
            if AGENT_API_ENDPOINT:
                logging.info(f"Offloading remediation to Agent API: {AGENT_API_ENDPOINT}")
                headers = {
                    "Authorization": f"Bearer {AGENT_API_KEY}",
                    "Content-Type": "application/json"
                }
                
                # We do not wait for the agent to finish (async offload) because agents take minutes to code/test,
                # and GitHub webhooks time out after 10 seconds.
                try:
                   requests.post(AGENT_API_ENDPOINT, json=agent_payload, headers=headers, timeout=5)
                except requests.exceptions.ReadTimeout:
                   logging.info("Successfully handed off to Agent async worker.")
            
            return func.HttpResponse(
                 json.dumps({"status": "Remediation Agent Dispatched", "run_id": run_id}),
                 mimetype="application/json",
                 status_code=202
            )
            
        return func.HttpResponse("Event processed. No remediation required.", status_code=200)
            
    except ValueError:
        return func.HttpResponse("Invalid JSON payload", status_code=400)
    except Exception as e:
        logging.error(f"Function trapped unhandled exception: {str(e)}")
        return func.HttpResponse("Internal Server Error", status_code=500)
