# Multi-Plan Azure Marketplace Strategy

## Overview

This document outlines the strategy for managing multi-plan offers within the Azure Marketplace. To optimize visibility and management, we will consolidate SKUs under single, unified Offers. A single parent "Offer" manages multiple "Plans" (variants), streamlining end-user discovery.

## Semantic Structure Mapping

1. **Publisher**: OpenClaw (Derek Coleman)
2. **Offer**: The high-level product listing visible in the Marketplace search results.
3. **Plan (SKU)**: The specific variant or flavor of that parent offer.

### Examples

#### Ubuntu Matrix

* **Offer**: `Ubuntu Server 25 LTS`
* **Plans**:
  * `server` (Standard UI-less server)
  * `minimal` (Stripped-down server)

#### Windows Server Matrix

* **Offer**: `Windows Server 2025`
* **Plans**:
  * `datacenter-core` (No Desktop Experience)
  * `datacenter-desktop` (With Desktop Experience - NOT standard Windows Desktop OS)

#### Windows Desktop Matrix

* **Offer**: `Windows 11 Professional`
* **Plans**:
  * `24h2-pro`
  * `24h2-ent`

## Repository Profile Mechanism

To support this cleanly within our `azure-packer-image-factory`, we use a dedicated `profiles/` directory hierarchy. The folder structure maps directly to the `Offer -> SKU` logic in the Azure Compute Gallery, which in turn feeds Microsoft Partner Center.

```text
profiles/
├── ubuntu-server-25-lts/           <-- Maps to Offer: ubuntu-server-25-lts
│   ├── server/                     <-- Maps to Plan: server
│   │   └── profile.yml
│   └── minimal/                    <-- Maps to Plan: minimal
│       └── profile.yml
├── windows-server-2025/            <-- Maps to Offer: windows-server-2025
│   ├── datacenter-core/            <-- Maps to Plan: datacenter-core
│   │   └── profile.yml
│   └── datacenter-desktop/         <-- Maps to Plan: datacenter-desktop
│       └── profile.yml
└── windows-11/                     <-- Maps to Offer: windows-11
    └── 24h2-pro/                   <-- Maps to Plan: 24h2-pro
        └── profile.yml
```

## Partner Center Alignment

When creating the offer in Microsoft Partner Center:

1. Create a single **Virtual Machine offer** named for the parent class (e.g. "Ubuntu Server 25 LTS").
2. Under the **Plan setup** tab, create the defined sub-plans (e.g. "server" and "minimal").
3. In the **Technical Configuration** tab for *each plan*, link it directly to the corresponding Image Definition deployed in the Azure Compute Gallery.

This design pattern ensures that when a customer searches for your brand, they see concise, top-level offers, and can use the plan dropdowns to select their desired variants without cluttering the marketplace search results with redundant entries.

## Partner Center API Pricing Strategy (Hard Rule)

In order to comply with offer creation best practices across the OpenClaw/DCA enterprise matrix, **all scripted virtual machine plans injected via the Partner Center API must rigidly enforce a $0.09 USD per vCPU (perCore) pricing model.**

When synthesizing the `price-and-availability-plan` JSON payload to `https://graph.microsoft.com/rp/product-ingestion/configure`, ensure the following schema block is present for every plan:

```json
"pricing": {
    "licenseModel": "payAsYouGo",
    "corePricing": {
        "priceInputOption": "perCore",
        "pricePerCore": 0.09
    }
}
```

This acts as a memory rule for any automation scripts mapping Azure Compute Gallery Image Definitions (`imgdef`) into the marketplace. Free or flat-rate options are strictly invalid for these OS images unless explicitly granted an exception.
