# Adobe Experience Platform Learning Repository

## Overview
This repository provides structured learning materials for Adobe Experience Platform (AEP), organized by weeks covering architecture, data ingestion, segmentation, and activation. It includes theoretical documentation, hands-on projects, sample data, setup guides, and resources.

## Architecture & Data Flow
- **XDM Schemas**: Define data structures using classes (e.g., XDM Individual Profile), field groups, and data types for standardized data modeling
- **Identity Service**: Links customer identifiers across systems via identity graphs and namespaces (ECID, Email, Phone, Custom)
- **Real-Time Customer Profile**: Unifies profile data from multiple sources for personalized experiences
- **Segmentation**: Creates audience segments based on behavior and profile attributes
- **Activation**: Sends segments to destinations like Google Ads, email providers, or custom endpoints

Data flows from ingestion (Web SDK, APIs, batch uploads) through processing (identity resolution, profile unification) to activation (campaign targeting).

## Key Patterns & Conventions
- **Language**: Documentation in Korean, code examples and filenames in English
- **Structure**: Weekly progression (week1-2: architecture, week3-4: ingestion, week5-6: segmentation, week7-8: activation)
- **Projects**: Step-by-step guides with UI instructions and API examples (JSON payloads)
- **Sample Data**: CSV files with e-commerce order data, including hashed PII (SHA256 email hashes) and ETL metadata
- **Setup**: Postman environment templates for API testing, requiring Adobe org credentials

## Development Workflows
- **Environment Setup**: Obtain AEP trial account, configure sandbox, set up API credentials in Postman
- **Schema Creation**: Use AEP UI or Schema Registry API with JSON payloads extending base XDM classes
- **Web SDK Implementation**: Embed Alloy.js library, configure with edgeConfigId and orgId, send XDM events
- **Data Ingestion**: Upload CSV samples via AEP UI or batch ingestion APIs
- **Segmentation**: Define segments using profile attributes and behavioral events
- **Activation**: Connect destinations, map segment data, schedule exports

## Integration Points
- **APIs**: Schema Registry, Identity Service, Profile API, Segmentation API, Destinations API
- **Web SDK**: Client-side data collection with XDM event payloads
- **Destinations**: External platforms like Google Ads, email services, CRM systems
- **Sample Data**: Pre-hashed customer data for privacy-compliant testing

## Code Examples
- **Web SDK Events**: `alloy("sendEvent", { xdm: { eventType: "web.webpagedetails.pageViews", web: {...} } })`
- **Schema Definition**: JSON with `$ref` to XDM base schemas and custom properties
- **API Calls**: POST to `/data/foundation/schemaregistry/tenant/schemas` with Bearer token auth

Reference `docs/` for concepts, `projects/` for implementations, `samples/data/` for test data, `setup/` for environment config.</content>
<parameter name="filePath">/Users/jason/dev/adobe/adobe-aep-learn/.github/copilot-instructions.md