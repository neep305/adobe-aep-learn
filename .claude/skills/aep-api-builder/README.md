# Adobe Experience Platform API Builder

Complete toolkit for interacting with Adobe Experience Platform APIs through Claude Code.

## Quick Start

### 1. Install Dependencies

```bash
cd .claude/skills/aep-api-builder
pip install -r requirements.txt
```

### 2. Configure Authentication

Copy the config template and fill in your credentials:

```bash
cp assets/config_template.json config.json
# Edit config.json with your Adobe I/O credentials
```

**OAuth Configuration (Recommended):**
```json
{
  "auth_method": "oauth",
  "client_id": "your_client_id",
  "client_secret": "your_client_secret",
  "org_id": "your_org_id@AdobeOrg",
  "sandbox_name": "prod"
}
```

Get credentials from [Adobe Developer Console](https://developer.adobe.com/console):
1. Create/select project
2. Add "Experience Platform API"
3. Choose "OAuth Server-to-Server" credential
4. Copy client_id, client_secret, and org_id

### 3. Test Authentication

```bash
python scripts/auth_helper.py --config config.json
```

You should see: `✓ New token generated`

## Usage

### Profile Lookup

Look up customer profiles by identity:

```bash
# By email
python scripts/profile_lookup.py \
  --config config.json \
  --namespace email \
  --value john@example.com

# By ECID with specific fields
python scripts/profile_lookup.py \
  --config config.json \
  --namespace ECID \
  --value 12345-67890 \
  --fields person.name personalEmail homeAddress

# Output as JSON
python scripts/profile_lookup.py \
  --config config.json \
  --namespace email \
  --value john@example.com \
  --format json
```

### Segment Management

Create and manage audience segments:

```bash
# List available templates
python scripts/segment_builder.py --list-templates

# Create segment from template
python scripts/segment_builder.py \
  --config config.json \
  --template 5_recent_purchasers \
  --merge-policy YOUR_MERGE_POLICY_ID

# Create custom segment
python scripts/segment_builder.py \
  --config config.json \
  --name "VIP Customers" \
  --pql "loyalty.tier = 'platinum' and loyalty.points > 10000" \
  --merge-policy YOUR_MERGE_POLICY_ID

# List existing segments
python scripts/api_client.py --config config.json segments --limit 50
```

### Query Service

Execute SQL queries on your data:

```bash
# Run query (waits for results)
python scripts/api_client.py \
  --config config.json \
  query \
  --sql "SELECT COUNT(*) FROM profile_dataset WHERE homeAddress.city = 'San Francisco'"

# Run async query (returns immediately)
python scripts/api_client.py \
  --config config.json \
  query \
  --sql "SELECT * FROM experience_event_dataset WHERE timestamp > '2024-01-01' LIMIT 1000" \
  --async

# Check query status
python scripts/api_client.py \
  --config config.json \
  query-status \
  --id YOUR_QUERY_ID
```

## Available Tools

### Scripts

| Script | Purpose | Quick Example |
|--------|---------|---------------|
| [auth_helper.py](scripts/auth_helper.py) | Generate access tokens | `python scripts/auth_helper.py --config config.json` |
| [profile_lookup.py](scripts/profile_lookup.py) | Look up customer profiles | `python scripts/profile_lookup.py --config config.json --namespace email --value user@example.com` |
| [segment_builder.py](scripts/segment_builder.py) | Create audience segments | `python scripts/segment_builder.py --list-templates` |
| [api_client.py](scripts/api_client.py) | General API operations | `python scripts/api_client.py --config config.json segments` |

### Templates & References

| File | Description |
|------|-------------|
| [segment_definition_template.json](assets/segment_definition_template.json) | 15 pre-built segment templates with PQL examples |
| [api_endpoints.md](references/api_endpoints.md) | Complete API endpoint reference |
| [authentication.md](references/authentication.md) | OAuth & JWT authentication guide |
| [xdm_schemas.md](references/xdm_schemas.md) | XDM schema field reference |
| [query_examples.md](references/query_examples.md) | 18 SQL query examples |

## Common Workflows

### Workflow 1: Customer Profile Analysis

```bash
# 1. Look up profile
python scripts/profile_lookup.py \
  --config config.json \
  --namespace email \
  --value customer@example.com \
  --format json > profile.json

# 2. Query related events
python scripts/api_client.py \
  --config config.json \
  query \
  --sql "SELECT * FROM experience_event_dataset WHERE identityMap.email[0].id = 'customer@example.com' ORDER BY timestamp DESC LIMIT 100"
```

### Workflow 2: Create Target Audience

```bash
# 1. List templates
python scripts/segment_builder.py --list-templates

# 2. Create segment
python scripts/segment_builder.py \
  --config config.json \
  --template 6_cart_abandoners \
  --name "Cart Abandoners - Last 7 Days" \
  --merge-policy YOUR_MERGE_POLICY_ID \
  --format json > segment_result.json

# 3. Verify segment was created
python scripts/api_client.py \
  --config config.json \
  segments \
  --filter "name=='Cart Abandoners - Last 7 Days'"
```

### Workflow 3: Data Analysis

```bash
# Geographic distribution
python scripts/api_client.py \
  --config config.json \
  query \
  --sql "SELECT homeAddress.city, COUNT(*) as count FROM profile_dataset GROUP BY homeAddress.city ORDER BY count DESC LIMIT 20"

# Recent purchase activity
python scripts/api_client.py \
  --config config.json \
  query \
  --sql "SELECT DATE_TRUNC('day', timestamp) as day, COUNT(*) as purchases FROM experience_event_dataset WHERE eventType = 'commerce.purchases' AND timestamp > CURRENT_DATE - INTERVAL '30' DAY GROUP BY day ORDER BY day DESC"
```

## API Client Library Usage

You can also use the API client as a Python library:

```python
from scripts.api_client import AEPAPIClient

# Initialize
client = AEPAPIClient('config.json')

# Get profile
profile = client.get_profile('email', 'john@example.com')
print(profile)

# List segments
segments = client.list_segments(limit=50)
print(f"Found {len(segments['children'])} segments")

# Create segment
segment_def = {
    'name': 'High Value Customers',
    'expression': {
        'type': 'PQL',
        'format': 'pql/text',
        'value': 'workingSet().xEvent[eventType = "commerce.purchases"].count() >= 5'
    },
    'schema': {'name': '_xdm.context.profile'},
    'mergePolicyId': 'your-merge-policy-id'
}
result = client.create_segment(segment_def)
print(f"Created segment: {result['id']}")

# Execute query
query_result = client.execute_query(
    "SELECT COUNT(*) FROM profile_dataset",
    name="Profile Count",
    async_mode=False
)
print(query_result)
```

## Troubleshooting

### Authentication Issues

**Error: "401 Unauthorized"**
- Token may be expired - delete `~/.aep_token_cache.json` and retry
- Verify credentials in config.json
- Check that API is added to your Adobe I/O project

**Error: "403 Forbidden"**
- Check sandbox name matches your environment
- Verify user has correct product profiles in Adobe Admin Console
- Confirm API permissions in Adobe Developer Console

### Query Issues

**Error: "Query timed out"**
- Use `--async` flag for long-running queries
- Increase `--timeout` value (default: 300 seconds)
- Optimize query with date filters and LIMIT clause

**Error: "Field not found"**
- Verify field paths match schema definition
- Use [xdm_schemas.md](references/xdm_schemas.md) for field reference
- Check field capitalization (case-sensitive)

### Segment Creation Issues

**Error: "Merge Policy not found"**
- Get merge policy ID:
  ```bash
  curl -X GET 'https://platform.adobe.io/data/core/ups/config/mergePolicies' \
    -H 'Authorization: Bearer {TOKEN}' \
    -H 'x-api-key: {CLIENT_ID}' \
    -H 'x-gw-ims-org-id: {ORG_ID}' \
    -H 'x-sandbox-name: prod'
  ```

**Error: "Invalid PQL syntax"**
- Test PQL in AEP UI Segment Builder first
- See [segment_definition_template.json](assets/segment_definition_template.json) for PQL examples
- Use [references/api_endpoints.md](references/api_endpoints.md) for PQL syntax

## Advanced Configuration

### Environment Variables

Instead of config.json, you can use environment variables:

```bash
export AEP_CLIENT_ID="your_client_id"
export AEP_CLIENT_SECRET="your_client_secret"
export AEP_ORG_ID="your_org_id@AdobeOrg"
export AEP_SANDBOX="prod"
```

Then modify scripts to load from env vars.

### Multiple Sandboxes

Create separate config files:

```bash
# Production
python scripts/profile_lookup.py --config config.prod.json ...

# Development
python scripts/profile_lookup.py --config config.dev.json ...
```

### Custom Templates

Create your own segment templates by editing [assets/segment_definition_template.json](assets/segment_definition_template.json).

## Resources

- [Adobe Experience Platform Documentation](https://experienceleague.adobe.com/docs/experience-platform.html)
- [API Reference](https://www.adobe.io/apis/experienceplatform/home/api-reference.html)
- [Adobe Developer Console](https://developer.adobe.com/console)
- [XDM GitHub Repository](https://github.com/adobe/xdm)

## License

This is a learning toolkit for the Adobe Experience Platform course. Use at your own discretion.

## Support

For issues or questions:
1. Check [references/](references/) documentation
2. Review error messages carefully
3. Verify credentials and permissions
4. Test with simpler queries first
