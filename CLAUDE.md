# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is an Adobe Experience Platform (AEP) learning repository containing study materials, hands-on projects, and documentation for understanding and implementing AEP features. The content is organized in Korean and follows a structured 8-week learning program covering architecture, data ingestion, segmentation, and activation.

## Repository Structure

```
adobe-aep-learn/
├── docs/               # Weekly learning materials (theoretical concepts)
│   ├── week1-2-architecture.md
│   ├── week3-4-data-ingestion.md
│   ├── week5-6-segmentation.md
│   └── week7-8-activation.md
├── projects/           # Hands-on project guides (practical exercises)
│   ├── week1-2/       # Schema and profile creation
│   ├── week3-4/       # Web SDK implementation
│   ├── week5-6/       # Segmentation exercises
│   ├── week7-8/       # Activation guides
│   └── final-project/ # End-to-end data pipeline
├── samples/data/      # Sample CSV data files
├── setup/             # Environment setup guides
└── resources/         # External links and references
```

## Key Concepts and Architecture

### Core AEP Components

**XDM (Experience Data Model)**
- Standardization framework for all data in AEP
- Composed of: Class (base structure), Field Groups (reusable fields), Data Types (complex structures)
- Two primary classes: XDM Individual Profile (customer attributes) and XDM Experience Event (behavioral events)
- Union Schema: Virtual schema merging all fields from schemas sharing the same class

**Identity Service**
- Unifies customer data from different systems into single profiles
- Identity Graph: Network connecting all customer identifiers (email, phone, ECID, custom IDs)
- Identity Namespace: Defines identifier types and matching rules

**Real-Time Customer Profile**
- Combines profile attributes and behavioral events into unified customer view
- Merge Policy: Determines how conflicting field values are resolved (Timestamp Ordering vs Priority Ordering)
- Profile Store: Separates standard profile data from edge profile data

### Data Architecture Patterns

**Profile vs Event Data**
- Profile: Mutable customer attributes (name, email, preferences) using XDM Individual Profile class
- Event: Immutable behavioral data (clicks, purchases, visits) using XDM Experience Event class, always timestamped

**Data Ingestion Methods**
- Batch Ingestion: Large historical data, scheduled updates, max 512MB per file
- Streaming Ingestion: Real-time data collection via Web SDK, Mobile SDK, or HTTP API
- Source Connectors: Pre-built integrations with cloud storage, CRM, databases

**Segmentation Types**
- Profile-Attribute: Based on customer properties (e.g., "Premium members")
- Event-Based: Based on behaviors (e.g., "Purchased in last 30 days")
- Time-Based: With temporal conditions (e.g., "Abandoned cart in 24 hours")
- Evaluation methods: Edge (client-side, lowest latency), Streaming (server-side real-time), Batch (scheduled, complex logic)

**Destinations**
- Streaming Destinations: Real-time export for advertising platforms (Google Ads, Facebook)
- Batch Destinations: Scheduled export for email platforms, data warehouses
- Profile Export: Full profile attributes to CRM/email systems
- Audience Export: Segment membership only to advertising platforms

## Development Setup

### Required Tools and Access
- Adobe Experience Platform trial or production account with API access
- Node.js (v14+) for Web SDK exercises
- PostgreSQL client for Query Service exercises
- Postman for API testing

### API Authentication
Configure Postman environment variables using [setup/postman-env-template.json](setup/postman-env-template.json):
- `organizationId`: AEP organization ID
- `apiKey`: API key from Adobe Developer Console
- `clientSecret`: Client secret for authentication
- `accessToken`: OAuth access token
- `sandboxName`: Target sandbox name
- `globalCompanyId`: Global company identifier

### Web SDK Setup
```javascript
// Basic Web SDK configuration pattern
alloy("configure", {
  "edgeConfigId": "YOUR_CONFIG_ID",
  "orgId": "YOUR_ORG_ID"
});

// Sending events
alloy("sendEvent", {
  "xdm": {
    "eventType": "web.webpagedetails.pageViews",
    "web": {
      "webPageDetails": {
        "URL": "https://example.com"
      }
    }
  }
});
```

### Query Service Patterns

**Profile Data Query**
```sql
SELECT * FROM profile_table LIMIT 10;
```

**Event Data with Time Filter**
```sql
SELECT * FROM event_table
WHERE timestamp >= '2023-01-01'
LIMIT 100;
```

**Data Aggregation**
```sql
SELECT city, COUNT(*) as customer_count
FROM profile_table
GROUP BY city
ORDER BY customer_count DESC;
```

## Working with Projects

### Learning Progression
Follow the weekly structure sequentially:
1. **Week 1-2**: Create schemas (Profile and Event), set up Identity Namespaces, configure Merge Policies
2. **Week 3-4**: Implement Web SDK, practice batch/streaming ingestion, apply data governance labels
3. **Week 5-6**: Build 5 business scenario segments (behavioral, demographic, multi-entity)
4. **Week 7-8**: Activate segments to Google Ads, email platforms, custom HTTP endpoints

### Final Project Workflow
End-to-end pipeline ([projects/final-project/README.md](projects/final-project/README.md)):
1. Schema creation: Customer Profile, Web Page View Events, Commerce Events
2. Web SDK implementation on HTML pages with pageview, add-to-cart, purchase events
3. Identity setup with Email and Phone namespaces
4. Five core segments: Cart Abandoners, VIP Customers, New Customers, Inactive Customers, Repeat Buyers
5. Activation to 3+ destinations with data flow monitoring

## Data Governance

### DULE Labels
- **C1**: Contract data (name, address, email)
- **C2**: Personally Identifiable Information (PII)
- **C3**: Sensitive data (credit cards, SSN)
- **I1-I3**: Purpose-specific data (specific use, analytics, marketing)

### Consent Management
- Opt-in: Explicit user consent
- Opt-out: User revokes consent
- No Preference: User hasn't expressed preference

## Sample Data

Sample CSV files in [samples/data/](samples/data/):
- `sample-customer-profiles.csv`: Customer profile attributes
- `sample-web-events.csv`: Web browsing events
- `estore_order_swa.csv`: E-commerce order data
- `estore_order_voucher_swa.csv`: Order voucher data

## Common Workflows

### Creating Schemas
1. Choose Class: XDM Individual Profile (for profiles) or XDM Experience Event (for events)
2. Add Field Groups: Pre-built field collections (Demographic Details, Personal Contact Details, etc.)
3. Set Primary Identity: Choose field (e.g., `personalEmail.address`) and assign Identity Namespace
4. Enable for Profile: Activate schema for Real-Time Customer Profile

### Building Segments
1. Use Segment Builder UI for visual segment construction
2. Define conditions: Profile attributes, events, or time-based rules
3. Set evaluation method: Streaming (real-time) or Batch (scheduled)
4. Monitor segment population in aggregation view

### Activating to Destinations
1. Connect destination: Configure authentication for target platform
2. Map fields: Align XDM fields to destination requirements
3. Select segments: Choose which audiences to export
4. Configure schedule: Set frequency for batch destinations
5. Monitor data flow: Check activation logs and success metrics

## Documentation Standards

All learning materials include:
- **학습 목표** (Learning Objectives): High-level goals for each week
- **개념** (Concepts): Theoretical foundation
- **실습 가이드** (Practice Guides): Step-by-step project links
- **학습 체크리스트** (Learning Checklist): Verification tasks
- **참고 자료** (References): Adobe Experience League documentation links

## Official Resources

- [Experience League Documentation](https://experienceleague.adobe.com/docs/experience-platform.html)
- [API Reference](https://www.adobe.io/apis/experienceplatform/home/api-reference.html)
- [Postman Collection](https://www.postman.com/adobe-experience-platform-ecosystem/)
- [Adobe Experience Platform Debugger](https://chrome.google.com/webstore/detail/adobe-experience-cloud-de/ocdmogmohccmeicdhlhhgeaonijenmgj)
- [Web SDK GitHub](https://github.com/adobe/alloy)

## Important Notes

- This repository contains learning materials, not production code
- Content is written in Korean; preserve language when editing
- Projects reference Adobe Experience Platform UI workflows which are cloud-based
- API examples require proper authentication setup before testing
- Sample data files use realistic e-commerce scenarios for practice
