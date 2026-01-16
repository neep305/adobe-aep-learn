---
name: adobe-aep
description: >
  Adobe Experience Platform API integration for customer profile management,
  segmentation, and data querying. Use when working with Real-Time Customer
  Profiles, audience segmentation, XDM schemas, Query Service, and identity
  graphs. Supports JWT/OAuth authentication, profile operations, segment
  creation, and batch/streaming data access.
---

# Adobe Experience Platform API Skill

Enables Claude to interact with Adobe Experience Platform APIs for customer data management, segmentation, and analytics.

## Quick Start

### 1. Authentication Setup

AEP requires JWT-based authentication. Run the authentication helper:
```bash
python scripts/auth_helper.py --config assets/config_template.json
```

This generates an access token valid for 24 hours. The script automatically handles token refresh.

### 2. Common Operations

#### Retrieve Customer Profile
```python
python scripts/profile_lookup.py \
  --namespace email \
  --value john@example.com \
  --fields person.name,homeAddress
```

#### Query Customer Data

Use Query Service for SQL-based analysis. For common patterns, see [references/query_examples.md](references/query_examples.md).

#### Create Audience Segment

Use segment definition templates from `assets/segment_definition_template.json` with appropriate PQL expressions.

## Core Workflows

### Profile Management

1. **Lookup by Identity**: Use namespace (email, ECID, CRM ID) and value
2. **Batch Retrieval**: For multiple profiles, use batch API (see references/api_endpoints.md)
3. **Field Selection**: Specify XDM paths to reduce response size

### Segmentation

1. **List Segments**: GET /segment/definitions
2. **Create Segment**: POST with PQL expression
3. **Evaluate**: Trigger segment evaluation job
4. **Export**: Extract segment members for activation

### Data Querying

1. **Interactive Query**: For quick analysis (<10 min execution)
2. **Scheduled Query**: For recurring reports
3. **CTAS (Create Table As Select)**: To materialize query results

## Important Notes

### Rate Limits
- Standard tier: 60 requests/minute
- Use batch endpoints for bulk operations
- Implement exponential backoff for 429 responses

### Sandbox Management
- Always specify `x-sandbox-name` header
- Production vs. development sandboxes have different data
- Use `prod` for production queries

### XDM Field Paths
- Use dot notation: `person.name.firstName`
- Array access: `commerce.purchases[0].productID`
- See [references/xdm_schemas.md](references/xdm_schemas.md) for schema details

## Advanced Usage

For detailed API specifications, authentication flows, or XDM schema structures, refer to:
- **API Details**: [references/api_endpoints.md](references/api_endpoints.md)
- **Authentication**: [references/authentication.md](references/authentication.md)  
- **XDM Schemas**: [references/xdm_schemas.md](references/xdm_schemas.md)
- **Query Examples**: [references/query_examples.md](references/query_examples.md)

## Troubleshooting

**401 Unauthorized**: Token expired, run `auth_helper.py` again
**403 Forbidden**: Check sandbox name and user permissions
**404 Not Found**: Verify entity ID and namespace combination
**429 Rate Limited**: Implement delay and retry logic