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
            "name": "Ubuntu Server",
            "plans": [
                {
                    "id": "plan-ubuntu-2404",
                    "title": "Ubuntu Server 24.04 LTS (Noble Numbat)",
                    "summary": "The latest Canonical Ubuntu 24.04 LTS built aggressively for cutting-edge enterprise scaling and containerization.",
                    "description": "<p>Optimize modern infrastructure atop Ubuntu Server 24.04 LTS. Hardened, rigorously tested, and equipped with the newest Linux kernel enhancements to drive flawless performance across Azure hybrid architectures. Includes an unmodified Canonical base image optimized strictly for maximum throughput and native cloud-init customization.</p>"
                },
                {
                    "id": "plan-ubuntu-2404-minimal",
                    "title": "Ubuntu Server 24.04 LTS Minimal",
                    "summary": "A highly-compressed, streamlined Canonical Ubuntu 24.04 LTS environment offering strict security posturing.",
                    "description": "<p>Engineered to reduce architectural attack surfaces, the Minimal deployment of Ubuntu 24.04 LTS strips out unnecessary binaries to maximize compute efficiency and reduce boot times. Intentionally positioned as a scalable Docker/Kubernetes container host and microservice backend.</p>"
                },
                {
                    "id": "plan-ubuntu-2204",
                    "title": "Ubuntu Server 22.04 LTS (Jammy Jellyfish)",
                    "summary": "The industry-leading, universally compliant Ubuntu Server 22.04 LTS tailored for production stability.",
                    "description": "<p>Deliver resilient and highly predictable runtime execution utilizing Canonical Ubuntu Server 22.04 LTS. Provides a hardened, trusted foundation equipped with highly-optimized network drivers natively tested for extreme stability across the Azure ecosystem.</p>"
                },
                {
                    "id": "plan-ubuntu-2204-minimal",
                    "title": "Ubuntu Server 22.04 LTS Minimal",
                    "summary": "Streamlined Canonical Ubuntu Server 22.04 LTS designed for lightweight cloud execution and rapid scaling.",
                    "description": "<p>Deploy an incredibly fast, highly optimized iteration of Canonical Ubuntu natively stripped of bulk packages. The 22.04 LTS Minimal Gen2 foundation offers reduced memory footprint, lowering compute costs while maintaining peak enterprise compatibility and stability.</p>"
                },
                {
                    "id": "plan-ubuntu-2004",
                    "title": "Ubuntu Server 20.04 LTS (Focal Fossa)",
                    "summary": "Legacy Canonical Ubuntu Server 20.04 LTS ensuring maximum architectural backward compatibility and prolonged support frameworks.",
                    "description": "<p>Ensure long-term operability of aging applications lacking modern runtime upgrades with Canonical Ubuntu Server 20.04 LTS. This production-tested foundational OS maintains rigorous security pipelines natively backed by Canonical, minimizing migration friction for established environments.</p>"
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
            
            # Hardware & Image Technical Configuration
            img_def = p_id.replace("plan-ubuntu", "imgdef-ubuntu-server") + "-gen2"
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
