# AEP API Endpoints Reference

Complete reference for Adobe Experience Platform API endpoints.

## Base URLs

- **Platform APIs**: `https://platform.adobe.io`
- **IMS Authentication**: `https://ims-na1.adobelogin.com`

## Profile Service APIs

### Get Single Profile
```
GET /data/core/ups/access/entities
```

**Query Parameters:**
- `schema.name` (required): `_xdm.context.profile`
- `entityId` (required): Identity value
- `entityIdNS` (required): Identity namespace
- `fields` (optional): Comma-separated XDM paths

**Example:**
```bash
curl -X GET "https://platform.adobe.io/data/core/ups/access/entities?schema.name=_xdm.context.profile&entityId=john@example.com&entityIdNS=email" \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -H "x-api-key: {CLIENT_ID}" \
  -H "x-gw-ims-org-id: {ORG_ID}" \
  -H "x-sandbox-name: prod"
```

### Search Profiles (PQL)
```
POST /data/core/ups/access/entities
```

**Request Body:**
```json
{
  "schema": {
    "name": "_xdm.context.profile"
  },
  "predicates": [
    {
      "values": ["john@example.com"],
      "namespace": "email"
    }
  ],
  "limit": 100
}
```

## Segmentation APIs

### List Segment Definitions
```
GET /data/core/ups/segment/definitions
```

**Query Parameters:**
- `limit`: Results per page (default: 20, max: 100)
- `start`: Offset for pagination
- `property`: Filter by property (e.g., `evaluationInfo.continuous==true`)

### Create Segment
```
POST /data/core/ups/segment/definitions
```

**Request Body:**
```json
{
  "name": "High-Value Customers",
  "description": "Customers with >$10K lifetime value",
  "expression": {
    "type": "PQL",
    "format": "pql/text",
    "value": "workEmail.address.isNotNull() and commerce.purchases.value > 10000"
  },
  "schema": {
    "name": "_xdm.context.profile"
  },
  "mergePolicyId": "{MERGE_POLICY_ID}"
}
```

### Evaluate Segment
```
POST /data/core/ups/segment/jobs
```

## Query Service APIs

### Create Query
```
POST /data/foundation/query/queries
```

**Request Body:**
```json
{
  "dbName": "prod:all",
  "sql": "SELECT COUNT(*) FROM profile_dataset WHERE _aep_created > current_date - 7",
  "name": "Weekly New Profiles"
}
```

### Get Query Status
```
GET /data/foundation/query/queries/{QUERY_ID}
```

### Get Query Results
```
GET /data/foundation/query/queries/{QUERY_ID}/results
```

## Schema Registry APIs

### List Schemas
```
GET /data/foundation/schemaregistry/tenant/schemas
```

**Headers:**
- `Accept`: `application/vnd.adobe.xed-id+json` (for IDs only)
- `Accept`: `application/vnd.adobe.xed+json` (for full schemas)

### Get Schema by ID
```
GET /data/foundation/schemaregistry/tenant/schemas/{SCHEMA_ID}
```

## Rate Limits

| Tier | Requests/Minute | Burst |
|------|----------------|-------|
| Standard | 60 | 100 |
| Premium | 300 | 500 |

**429 Response Handling:**
```python
import time

def api_call_with_retry(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                retry_after = int(e.response.headers.get('Retry-After', 60))
                time.sleep(retry_after)
            else:
                raise
    raise Exception("Max retries exceeded")
```

## Error Codes

| Code | Meaning | Solution |
|------|---------|----------|
| 401 | Unauthorized | Refresh access token |
| 403 | Forbidden | Check permissions and sandbox |
| 404 | Not Found | Verify entity ID and namespace |
| 429 | Rate Limited | Implement backoff strategy |
| 500 | Server Error | Retry with exponential backoff |