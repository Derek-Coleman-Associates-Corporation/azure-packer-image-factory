import requests
import json
import msal
import sys
import os

def main():
    print("Initiating Microsoft Partner Center SQL Server 2025 Automation...")

    # Load Authentication from GitHub Actions Environment Variables
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
        print("Failed to acquire MS Graph Token")
        sys.exit(1)

    token = result["access_token"]
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    sql_products = {
        "sql-server-2025-gen2": {
            "name": "SQL Server 2025",
            "plans": [
                {
                    "id": "plan-sql2025-ws2025-dev",
                    "img_def": "imgdef-sql2025-ws2025-dev-gen2",
                    "title": "SQL Server 2025 Developer on Windows Server 2025 (Gen2)",
                    "summary": "Microsoft SQL Server 2025 Developer Edition optimized on Windows Server 2025. Perfect for dev/test environments.",
                    "description": "<p>Deploy the ultimate, fully-featured SQL Server 2025 Developer Edition on the highly secure Windows Server 2025 foundation. This Gen2 Trusted Launch deployment is optimized specifically for non-production development and testing workflows, offering full Enterprise-level capabilities at zero licensing cost (standard Azure compute rates apply). Includes advanced vector search paradigms, secure enclaves, and intelligent query processing seamlessly integrated into the newest Windows Server architecture.</p>"
                },
                {
                    "id": "plan-sql2025-ws2025-std",
                    "img_def": "imgdef-sql2025-ws2025-std-gen2",
                    "title": "SQL Server 2025 Standard on Windows Server 2025 (Gen2)",
                    "summary": "Microsoft SQL Server 2025 Standard on Windows Server 2025. Production-ready relational performance.",
                    "description": "<p>Power your tier-1 production applications with Microsoft SQL Server 2025 Standard natively integrated upon Windows Server 2025. Engineered with Gen2 Trusted Launch security, this image offers highly scalable data performance, seamless hybrid cloud capability, industry-leading data integration, and advanced JSON/Vector capabilities. Highly optimized for medium-scale enterprise infrastructures requiring high-availability deployment structures.</p>"
                },
                {
                    "id": "plan-sql2025-ws2025-ent",
                    "img_def": "imgdef-sql2025-ws2025-ent-gen2",
                    "title": "SQL Server 2025 Enterprise on Windows Server 2025 (Gen2)",
                    "summary": "Microsoft SQL Server 2025 Enterprise on Windows Server 2025. Ultimate data warehouse and analytics ecosystem.",
                    "description": "<p>Execute mission-critical, large-scale database operations using Microsoft SQL Server 2025 Enterprise Edition on Windows Server 2025. Featuring maximum compute capabilities, native Gen2 Trusted Launch security, predictive analytics, transparent data encryption, and unparalleled transaction speeds. This robust production deployment operates at the bleeding edge of intelligent query processing algorithms to handle the most demanding, data-intensive enterprise footprints.</p>"
                }
            ]
        },
        "8a9b1fd3-aef8-44dc-a088-14d4ae49417a": {   # Product ID for SQL Server 2022 natively found by user
            "name": "SQL Server 2022 on Windows Server 2022",
            "plans": [
                {
                    "id": "sql2022win2022",
                    "img_def": "imgdef-sql2022-ws2022-gen2",   # Mapped to Base image
                    "title": "Windows Server 2022 (Base OS/Gen2)",
                    "summary": "The foundational Windows Server 2022 Gen2 operating system optimized for scalable SQL Server workloads.",
                    "description": "<p>A streamlined, highly-secure Windows Server 2022 Gen2 Base image engineered specifically for resilient, hybrid-cloud integration. Provides the core Trusted Launch foundation necessary for seamless enterprise scaling without pre-installed database engines.</p>"
                },
                {
                    "id": "sql2022devwin2022",
                    "img_def": "imgdef-sql2022-ws2022-developer-gen2",
                    "title": "SQL Server 2022 Developer on Windows Server 2022 (Gen2)",
                    "summary": "SQL Server 2022 Developer edition pre-configured for rigorous non-production testing and data engineering.",
                    "description": "<p>Seamlessly deploy a fully-stacked SQL Server 2022 development environment on Windows Server 2022. This Gen2 Virtual Machine yields full enterprise database features specifically licensed for development and testing. Accelerate pipeline generation and test hybrid cloud integration instantly.</p>"
                },
                {
                    "id": "sql2022stdwin2022",
                    "img_def": "imgdef-sql2022-ws2022-standard-gen2",
                    "title": "SQL Server 2022 Standard on Windows Server 2022 (Gen2)",
                    "summary": "The industry-standard operational database management system fully integrated into Windows Server 2022.",
                    "description": "<p>Designed for robust production deployment, SQL Server 2022 Standard on Windows Server 2022 implements reliable, high-performance structured data ingestion. Includes core database engine capabilities, enhanced security configurations, and Gen2 hypervisor compliance designed for mission-critical enterprise workloads.</p>"
                },
                {
                    "id": "sql_2022_ee_win2022",
                    "img_def": "imgdef-sql2022-ws2022-enterprise-gen2",
                    "title": "SQL Server 2022 Enterprise on Windows Server 2022 (Gen2)",
                    "summary": "Microsoft SQL Server 2022 Enterprise delivering unparalleled tier-1 performance, scale, and analytics.",
                    "description": "<p>Power your most demanding operational analytics and real-time transaction processing. Microsoft SQL Server 2022 Enterprise Edition on Windows Server 2022 offers massive scalability, unrestricted CPU mapping, built-in ML services, and end-to-end data encryptions deployed seamlessly on Gen2 architectural topologies.</p>"
                }
            ]
        }
    }
    
    resources = []
    
    for product_id, product_data in sql_products.items():
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
            img_def = plan_obj['img_def']
            
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
            resources.append({
                "$schema": "https://schema.mp.microsoft.com/schema/virtual-machine-plan-technical-configuration/2022-03-01-preview2",
                "id": f"virtual-machine-plan-technical-configuration/{product_id}/{p_id}",
                "product": f"product/{product_id}",
                "plan": f"plan/{product_id}/{p_id}",
                "operatingSystemFamily": "Windows",
                "operatingSystem": "Windows", 
                "generation": "gen2",
                "state": "generalized",
                "securityType": "TrustedLaunch",
                "supportsAcceleratedNetworking": True,
                "supportsCloudInitConfiguration": False,
                "supportsVmExtensions": True,
                "supportsBackup": True,
                "supportsMicrosoftEntraIdentityAuthentication": True,
                "isNetworkVirtualAppliance": False,
                "recommendedSizes": [
                    "Standard_D8s_v5",
                    "Standard_D16s_v5",
                    "Standard_E8s_v5",
                    "Standard_E16s_v5",
                    "Standard_M8ms",
                    "Standard_M16ms"
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
    
    print(f"\nExecuting POST /configure to mint ALL SQL Server Topologies and Nested Plans...")
    try:
        r = requests.post(cfg_url, headers=headers, json=payload, timeout=30)
        print(f"HTTP Return Code: {r.status_code}")
        if r.status_code in [200, 201, 202]:
            print(f"Successfully generated Marketing and Technical configurations for ALL SQL Server Offers!")
            print(json.dumps(r.json(), indent=2))
        else:
            print("Submission FAILED:")
            try:
                print(json.dumps(r.json(), indent=2))
            except:
                print(r.text)
    except Exception as e:
        print(f"Socket or HTTP connection error: {e}")

if __name__ == "__main__":
    main()
