import requests
import msal
import json
import time
import os

def run_kali_automation():
    print("Initiating Kali Linux Partner Center Injection Pipeline...")
    
    # Load Environment Variables natively
    client_id = os.environ.get("AZURE_CLIENT_ID")
    tenant_id = os.environ.get("AZURE_TENANT_ID")
    client_secret = os.environ.get("AZURE_CLIENT_SECRET")

    if not client_id or not tenant_id or not client_secret:
        print("Missing required API authentication variables.")
        return

    # Helper: Discover Latest ACG Version Autonomously
    authority = "https://login.microsoftonline.com/" + tenant_id
    def get_latest_gallery_version(img_def_target):
        mgmt_app = msal.ConfidentialClientApplication(client_id, authority=authority, client_credential=client_secret)
        mgmt_result = mgmt_app.acquire_token_for_client(scopes=["https://management.azure.com/.default"])
        if "access_token" not in mgmt_result:
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
                return "1.0.0"
            latest = sorted(versions, key=lambda x: x.get("name", "0.0.0"), reverse=True)[0]
            discovered_version = latest.get("name", "1.0.0")
            print(f"[{img_def_target}] Automatically bonded to Version: {discovered_version}")
            return discovered_version
        return "1.0.0"

    print("Authenticating to Microsoft Graph API...")
    app = msal.ConfidentialClientApplication(
        client_id, authority=authority,
        client_credential=client_secret
    )
    result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])

    if "access_token" not in result:
        print("Authentication to Microsoft Graph Failed.")
        return

    token = result["access_token"]
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    kali_products = {
        "kali-linux-security-gen2": {
            "name": "Kali Linux Security Operations",
            "plans": [
                {
                    "id": "kali-2024-base",
                    "img_def": "imgdef-kali-2024-base-gen2",
                    "title": "Kali Linux 2024.1 Base Image",
                    "summary": "Core Kali Linux offensive security framework for command-line CI/CD parsing.",
                    "description": "<p>Deploy an exceptionally fast Kali instance entirely streamlined for automated red-team security auditing pipelines within Azure Gen2 compute.</p>"
                },
                {
                    "id": "kali-2024-desktop",
                    "img_def": "imgdef-kali-2024-desktop-gen2",
                    "title": "Kali Linux 2024.1 Desktop Automation",
                    "summary": "Full Kali Linux XFCE desktop experience natively equipped with hundreds of offensive auditing toolchains.",
                    "description": "<p>Empower your security teams with a fully interactive Kali Linux Desktop environment, hardened exclusively over Azure compute nodes.</p>"
                },
                {
                    "id": "kali-2024-minimal",
                    "img_def": "imgdef-kali-2024-minimal-gen2",
                    "title": "Kali Linux 2024.1 Minimal",
                    "summary": "Radically compressed Kali Linux instance aimed strictly at execution density.",
                    "description": "<p>The smallest deployable Kali ecosystem natively structured for container or extreme scale testing swarms across the Microsoft network edge.</p>"
                }
            ]
        }
    }
    
    resources = []
    
    for product_id, product_data in kali_products.items():
        print(f"Synthesizing Configuration Payload for {product_data['name']} ({product_id})...")
        
        # 1. Product (Offer) Creation Shell
        resources.append({
            "$schema": "https://schema.mp.microsoft.com/schema/product/2022-03-01-preview3",
            "id": f"product/{product_id}",
            "name": product_data['name'],
            "kind": "azureVM"
        })
        
        # 1.5 Preview Audience Configurations (Offer-Level Testers)
        resources.append({
            "$schema": "https://schema.mp.microsoft.com/schema/price-and-availability-offer/2022-03-01-preview3",
            "id": f"price-and-availability-offer/{product_id}",
            "product": f"product/{product_id}",
            "previewAudiences": [
                {
                    "type": "subscription",
                    "id": "48fe169a-1451-4f57-8487-96a81f41e539",
                    "label": "Testers"
                }
            ]
        })

        # 2. Plan Minting Loop
        for plan_obj in product_data['plans']:
            p_id = plan_obj['id']
            p_title = plan_obj['title']
            p_summary = plan_obj['summary']
            p_desc = plan_obj['description']
            img_def = plan_obj['img_def']
            
            # Core Plan structural node
            resources.append({
                "$schema": "https://schema.mp.microsoft.com/schema/plan/2022-03-01-preview2",
                "id": f"plan/{product_id}/{p_id}",
                "product": f"product/{product_id}",
                "name": p_title,
                "azureRegions": ["azureGlobal", "azureGovernment"]
            })
            
            # EXACT Plan Listing SEO configuration mapping directly to Memory store
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

            # Plan Pricing and Availability (Enforcing $0.09 perCore universally)
            resources.append({
                "$schema": "https://schema.mp.microsoft.com/schema/price-and-availability-plan/2022-03-01-preview3",
                "id": f"price-and-availability-plan/{product_id}/{p_id}",
                "product": f"product/{product_id}",
                "plan": f"plan/{product_id}/{p_id}",
                "pricing": {
                    "licenseModel": "payAsYouGo",
                    "corePricing": {
                        "priceInputOption": "perCore",
                        "pricePerCore": 0.09
                    }
                },
                "visibility": "visible",
                "audience": "public",
                "customerMarkets": "allMarkets"
            })
            
            # Hardware & Image Technical Configuration
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
    
    print(f"\nExecuting POST /configure to mint ALL Kali Linux Nested Plans...")
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
                    print("--> Kali Network Security Offer Creation Succeeded!")
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
    run_kali_automation()
