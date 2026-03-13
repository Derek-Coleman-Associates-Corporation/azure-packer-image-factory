import requests
import msal
import json
import time
import os

def run_rhel_automation():
    print("Initiating BRAND NEW Red Hat Enterprise Linux (RHEL) Partner Center Injection...")
    
    client_id = os.environ.get("AZURE_CLIENT_ID")
    tenant_id = os.environ.get("AZURE_TENANT_ID")
    client_secret = os.environ.get("AZURE_CLIENT_SECRET")

    if not client_id or not tenant_id or not client_secret:
        print("CRITICAL VALIDATION ERROR: Missing AZURE Authentication Secrets!")
        return

    # Helper: Discover Latest ACG Version Autonomously
    def get_latest_gallery_version(img_def_target):
        # The authority for Azure Management API is typically the same as for Graph API, but scopes differ.
        # The tenant_id is already available in the outer scope.
        mgmt_authority = f"https://login.microsoftonline.com/{tenant_id}"
        mgmt_app = msal.ConfidentialClientApplication(client_id, authority=mgmt_authority, client_credential=client_secret)
        mgmt_result = mgmt_app.acquire_token_for_client(scopes=["https://management.azure.com/.default"])
        if "access_token" not in mgmt_result:
            print(f"Failed to acquire token for Azure Management API for {img_def_target}. Defaulting to 1.0.0.")
            return "1.0.0"
            
        mgmt_headers = {"Authorization": f"Bearer {mgmt_result['access_token']}"}
        sub_id = "f4085274-4e9d-4e93-8360-67a4be900d81"
        rg = "RG-PACKER-IMAGE-FACTORY-EASTUS"
        gallery = "acgpackerfactoryeastus"
        
        url = f"https://management.azure.com/subscriptions/{sub_id}/resourceGroups/{rg}/providers/Microsoft.Compute/galleries/{gallery}/images/{img_def_target}/versions?api-version=2024-03-03"
        resp = requests.get(url, headers=mgmt_headers, timeout=15)
        
        if resp.status_code == 200:
            versions = resp.json().get("value", [])
            if not versions:
                print(f"No versions found for {img_def_target}. Defaulting to 1.0.0.")
                return "1.0.0"
            # Sort versions by name (which is typically semantic versioning) to find the latest
            latest = sorted(versions, key=lambda x: x.get("name", "0.0.0"), reverse=True)[0]
            discovered_version = latest.get("name", "1.0.0")
            print(f"[{img_def_target}] Automatically bonded to Version: {discovered_version}")
            return discovered_version
        else:
            print(f"Failed to retrieve versions for {img_def_target}. Status Code: {resp.status_code}, Response: {resp.text}. Defaulting to 1.0.0.")
        return "1.0.0"

    print("Authenticating to Microsoft Graph API...")
    app = msal.ConfidentialClientApplication(
        client_id, authority="https://login.microsoftonline.com/" + tenant_id,
        client_credential=client_secret
    )
    result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])

    if "access_token" not in result:
        print("Authentication Failed.")
        return

    token = result["access_token"]
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    rhel_products = {
        "rhel-server-gen2": {
            "name": "Red Hat Enterprise Linux (RHEL)",
            "plans": [
                {
                    "id": "plan-rhel-94",
                    "title": "Red Hat Enterprise Linux 9.4 (Gen2)",
                    "summary": "The newest iteration of the ultimate open-source enterprise operating system deployment.",
                    "description": "<p>Maximize hybrid cloud success with the unparalleled performance and security of RHEL 9.4. Natively configured to capitalize on Azure's newest Gen2 hypervisor specifications, this image delivers extensive application stream coverage, native compliance frameworks, and proactive defense paradigms.</p>"
                },
                {
                    "id": "plan-rhel-93",
                    "title": "Red Hat Enterprise Linux 9.3 (Gen2)",
                    "summary": "Highly resilient RHEL 9.3 runtime execution optimized strictly for mission-critical Gen2 throughput.",
                    "description": "<p>Deploy sophisticated, compliance-driven enterprise applications securely with Red Hat Enterprise Linux 9.3. Engineered to support massive-scale Linux execution across hybrid infrastructure footprints.</p>"
                },
                {
                    "id": "plan-rhel-810",
                    "title": "Red Hat Enterprise Linux 8.10 (Gen2)",
                    "summary": "RHEL 8.10, optimized for legacy enterprise compatibility, strict regulatory workflows, and predictable execution.",
                    "description": "<p>Ensuring total application stability and deeply-vetted security profiles, Red Hat Enterprise Linux 8.10 offers continuous enterprise-grade compute. Ideal for strict production architectures requiring proven dependency tracking and rigid, scalable lifecycle administration across Azure topologies.</p>"
                }
            ]
        }
    }
    
    resources = []
    
    for product_id, product_data in rhel_products.items():
        print(f"Synthesizing Configuration Payload for {product_data['name']} ({product_id})...")
        
        # 1. Product (Offer) Creation Shell
        resources.append({
            "$schema": "https://schema.mp.microsoft.com/schema/product/2022-03-01-preview3",
            "id": f"product/{product_id}",
            "name": product_data['name'],
            "kind": "azureVM"
        })
        
        # 2. Plan Minting Loop
        for plan_obj in product_data['plans']:
            p_id = plan_obj['id']
            p_title = plan_obj['title']
            p_summary = plan_obj['summary']
            p_desc = plan_obj['description']
            
            resources.append({
                "$schema": "https://schema.mp.microsoft.com/schema/plan/2022-03-01-preview2",
                "id": f"plan/{product_id}/{p_id}",
                "product": f"product/{product_id}",
                "name": p_title
            })
            
            resources.append({
                "$schema": "https://schema.mp.microsoft.com/schema/plan-listing/2022-03-01-preview3",
                "id": f"plan-listing/{product_id}/public/main/{p_id}/en-us",
                "product": f"product/{product_id}",
                "plan": f"plan/{product_id}/{p_id}",
                "kind": "azureVM-plan",
                "languageId": "en-us",
                "name": p_title,
                "summary": p_summary,
                "description": p_desc
            })
            
            # Hardware & Image Technical Configuration
            img_def = p_id.replace("plan-rhel-", "imgdef-rhel-") + "-gen2"
            resources.append({
                "$schema": "https://schema.mp.microsoft.com/schema/virtual-machine-plan-technical-configuration/2022-03-01-preview2",
                "id": f"virtual-machine-plan-technical-configuration/{product_id}/{p_id}",
                "product": f"product/{product_id}",
                "plan": f"plan/{product_id}/{p_id}",
                "operatingSystemFamily": "Linux",
                "operatingSystem": "Other", 
                "generation": "gen2",
                "state": "generalized",
                "securityType": "TrustedLaunch",
                "supportsAcceleratedNetworking": True,
                "supportsCloudInitConfiguration": True,
                "supportsVmExtensions": True,
                "supportsBackup": True,
                "supportsMicrosoftEntraIdentityAuthentication": True,
                "isNetworkVirtualAppliance": False,
                "recommendedSizes": [
                    "Standard_D2s_v5",
                    "Standard_D4s_v5",
                    "Standard_D8s_v5",
                    "Standard_E2s_v5",
                    "Standard_E4s_v5",
                    "Standard_E8s_v5"
                ],
                "azureComputeGalleryImageIdentities": [
                    {
                        "subscriptionId": "f4085274-4e9d-4e93-8360-67a4be900d81",  
                        "resourceGroup": "RG-PACKER-IMAGE-FACTORY-EASTUS",
                        "galleryName": "acgpackerfactoryeastus",
                        "imageDefinitionName": img_def,
                        "imageVersion": get_latest_gallery_version(img_def)
                    }
                ]
            })
            
    payload = {
        "$schema": "https://schema.mp.microsoft.com/schema/configure/2022-03-01-preview2",
        "resources": resources
    }
    
    cfg_url = "https://graph.microsoft.com/rp/product-ingestion/configure?api-version=2022-03-01-preview2"
    
    print(f"\nExecuting POST /configure to mint ALL Red Hat Topologies and Nested Plans...")
    try:
        r = requests.post(cfg_url, headers=headers, json=payload, timeout=30)
        print(f"HTTP Return Code: {r.status_code}")
        
        if r.status_code in [200, 202]:
            job_id = r.json().get("jobId")
            print(f"Polling Job ID: {job_id}")
            for _ in range(12):
                time.sleep(5)
                stat_url = f"https://graph.microsoft.com/rp/product-ingestion/configure/{job_id}/status?api-version=2022-03-01-preview2"
                stat = requests.get(stat_url, headers=headers, timeout=10).json()
                s = stat.get("jobStatus", "").lower()
                print(f"Current Execution Status: {s}")
                if s in ["completed", "succeeded"]: 
                    print("--> Brand New Offer Creation Succeeded!")
                    break
                if s == "failed":
                    print("--> MAPPING FAILED. DIAGNOSTICS:")
                    print(json.dumps(stat, indent=2))
                    break
        else:
            print("API Rejection:", r.text)
            
    except Exception as e:
        print("Network Socket Timeout or Execution Error:", str(e))

if __name__ == "__main__":
    run_rhel_automation()
