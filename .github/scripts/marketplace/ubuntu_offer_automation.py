import requests
import msal
import json
import time
import os

def run_ubuntu_automation():
    print("Initiating Canonical Ubuntu Server 1st-Party SEO Plan Ingestion...")
    
    # Load Environment Variables from GitHub Actions Secrets natively
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
        client_id, authority="https://login.microsoftonline.com/" + tenant_id,
        client_credential=client_secret
    )
    result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])

    if "access_token" not in result:
        print("Authentication to Microsoft Graph Failed.")
        return

    token = result["access_token"]
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    ubuntu_products = {
        "ubuntu-server-gen2": {
            "name": "Ubuntu Enterprise (Server & Desktop)",
            "logo_path": ".agents/workflows/ubuntu-logo.png",
            "plans": [
                {
                    "id": "ubuntu-2404-lts",
                    "img_def": "imgdef-ubuntu-desktop-2404-gen2",
                    "title": "Ubuntu Desktop 24.04.4 LTS",
                    "summary": "Canonical Ubuntu Desktop 24.04.4 LTS natively optimized for Azure Virtual Desktop.",
                    "description": "<p>Deliver resilient GUI-based developer desktops utilizing Canonical Ubuntu 24.04.4 LTS. Provides a hardened foundation equipped with optimized GPU drivers tested for desktop stability.</p>"
                },
                {
                    "id": "ubuntu-2510",
                    "img_def": "imgdef-ubuntu-desktop-2410-gen2",
                    "title": "Ubuntu Desktop 25.10",
                    "summary": "The latest Canonical Ubuntu Desktop 25.10 release with advanced UI and developer tooling.",
                    "description": "<p>Deploy an incredibly fast iteration of Canonical Ubuntu Desktop 25.10 for cutting-edge development workflows.</p>"
                },
                {
                    "id": "ubuntu-server-2404",
                    "img_def": "imgdef-ubuntu-server-2404-gen2",
                    "title": "Ubuntu Server 24.04 LTS",
                    "summary": "Canonical Ubuntu 24.04 LTS built aggressively for cutting-edge enterprise scaling.",
                    "description": "<p>Optimize modern infrastructure atop Ubuntu Server 24.04 LTS. Hardened and equipped with the newest Linux kernels.</p>"
                },
                {
                    "id": "ubuntu-server-2204",
                    "img_def": "imgdef-ubuntu-server-2204-gen2",
                    "title": "Ubuntu Server 22.04 LTS",
                    "summary": "Canonical Ubuntu Server 22.04 LTS tailored for strict production stability.",
                    "description": "<p>Deliver resilient backend systems utilizing Canonical Ubuntu Server 22.04 LTS.</p>"
                },
                {
                    "id": "ubuntu-server-2004",
                    "img_def": "imgdef-ubuntu-server-2004-gen2",
                    "title": "Ubuntu Server 20.04 LTS",
                    "summary": "Legacy Canonical Ubuntu Server 20.04 LTS for architectural backward compatibility.",
                    "description": "<p>Ensure long-term operability of aging applications with Canonical Ubuntu Server 20.04 LTS.</p>"
                },
                {
                    "id": "ubuntu-desktop-2204",
                    "img_def": "imgdef-ubuntu-desktop-2204-gen2",
                    "title": "Ubuntu Desktop 22.04 LTS",
                    "summary": "Canonical Ubuntu Desktop 22.04 LTS designed for remote access protocols.",
                    "description": "<p>Deploy a stable, heavily supported GUI environment with Ubuntu Desktop 22.04 LTS.</p>"
                },
                {
                    "id": "ubuntu-desktop-2004",
                    "img_def": "imgdef-ubuntu-desktop-2004-gen2",
                    "title": "Ubuntu Desktop 20.04 LTS",
                    "summary": "Canonical Ubuntu Desktop 20.04 LTS for legacy X11 compatibility workflows.",
                    "description": "<p>Provides a hardened, historically trusted X11 foundation for legacy UI testing atop Ubuntu Desktop 20.04 LTS.</p>"
                }
            ]
        }
    }
    
    resources = []
    
    for product_id, product_data in ubuntu_products.items():
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
            
            # Core Plan structural node
            resources.append({
                "$schema": "https://schema.mp.microsoft.com/schema/plan/2022-03-01-preview2",
                "id": f"plan/{product_id}/{p_id}",
                "product": f"product/{product_id}",
                "name": p_title
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
            img_def = plan_obj.get("img_def", f"imgdef-ubuntu-{p_id}-gen2")
            resources.append({
                "$schema": "https://schema.mp.microsoft.com/schema/virtual-machine-plan-technical-configuration/2022-03-01-preview2",
                "id": f"virtual-machine-plan-technical-configuration/{product_id}/{p_id}",
                "product": f"product/{product_id}",
                "plan": f"plan/{product_id}/{p_id}",
                "operatingSystemFamily": "Linux",
                "operatingSystem": "ubuntu",
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
    
    print(f"\nExecuting POST /configure to mint ALL Ubuntu Server Topologies and Nested Plans...")
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
                    print("--> Matrix Injection Succeeded!")
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
    run_ubuntu_automation()
