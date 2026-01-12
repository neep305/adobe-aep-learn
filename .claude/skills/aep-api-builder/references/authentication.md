# Adobe Experience Platform Authentication

Complete guide to authenticating with Adobe Experience Platform APIs.

## Authentication Methods

Adobe Experience Platform supports two authentication methods:

### 1. OAuth Server-to-Server (Recommended)

**Status**: Current standard for new integrations
**Use Case**: Production applications, automated workflows

#### Setup Process

1. **Create Project in Adobe Developer Console**
   - Navigate to https://developer.adobe.com/console
   - Create new project or select existing
   - Add API: Experience Platform API
   - Select OAuth Server-to-Server credential type

2. **Configure OAuth Credentials**
   - Client ID: Auto-generated
   - Client Secret: Auto-generated (store securely)
   - Scopes: Select required AEP scopes
     - `openid`
     - `AdobeID`
     - `read_organizations`
     - `additional_info.projectedProductContext`
     - `session`

3. **Generate Access Token**
   ```bash
   curl -X POST 'https://ims-na1.adobelogin.com/ims/token/v3' \
     -H 'Content-Type: application/x-www-form-urlencoded' \
     -d 'grant_type=client_credentials' \
     -d 'client_id={CLIENT_ID}' \
     -d 'client_secret={CLIENT_SECRET}' \
     -d 'scope=openid,AdobeID,read_organizations,additional_info.projectedProductContext,session'
   ```

   **Response:**
   ```json
   {
     "access_token": "eyJhbG...",
     "token_type": "bearer",
     "expires_in": 86399
   }
   ```

#### Python Implementation

```python
import requests
import time
from datetime import datetime, timedelta

class OAuthAuthHelper:
    TOKEN_URL = 'https://ims-na1.adobelogin.com/ims/token/v3'

    def __init__(self, client_id, client_secret, scopes=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.scopes = scopes or [
            'openid',
            'AdobeID',
            'read_organizations',
            'additional_info.projectedProductContext',
            'session'
        ]
        self.access_token = None
        self.token_expiry = None

    def get_access_token(self):
        """Get valid access token, refresh if expired"""
        if self.access_token and datetime.now() < self.token_expiry:
            return self.access_token

        # Request new token
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scope': ','.join(self.scopes)
        }

        response = requests.post(self.TOKEN_URL, data=data)
        response.raise_for_status()

        result = response.json()
        self.access_token = result['access_token']
        # Set expiry with 5-minute buffer
        self.token_expiry = datetime.now() + timedelta(seconds=result['expires_in'] - 300)

        return self.access_token
```

### 2. JWT Authentication (Legacy - Being Deprecated)

**Status**: Being phased out (deprecation announced)
**Migration Deadline**: Check Adobe Developer Console for your org
**Use Case**: Existing integrations only

#### JWT Flow Overview

1. **Generate JWT Token**
   - Create JWT payload with required claims
   - Sign with RSA private key
   - Validity: 24 hours

2. **Exchange JWT for Access Token**
   - POST JWT to Adobe IMS
   - Receive access token (valid 24 hours)

3. **Use Access Token**
   - Include in Authorization header
   - Refresh before expiry

#### JWT Payload Structure

```json
{
  "exp": 1234567890,
  "iss": "{ORG_ID}",
  "sub": "{TECHNICAL_ACCOUNT_ID}",
  "aud": "https://ims-na1.adobelogin.com/c/{CLIENT_ID}",
  "https://ims-na1.adobelogin.com/s/ent_dataservices_sdk": true
}
```

#### Migration from JWT to OAuth

**Steps:**
1. Create new OAuth Server-to-Server credential in Adobe Developer Console
2. Update application code to use OAuth flow
3. Test thoroughly in development sandbox
4. Deploy to production
5. Remove JWT credential after successful migration

## Required Headers

All AEP API requests require these headers:

```http
Authorization: Bearer {ACCESS_TOKEN}
x-api-key: {CLIENT_ID}
x-gw-ims-org-id: {ORG_ID}
x-sandbox-name: {SANDBOX_NAME}
Content-Type: application/json
```

### Header Descriptions

| Header | Description | Example |
|--------|-------------|---------|
| `Authorization` | Bearer token from OAuth/JWT | `Bearer eyJhbG...` |
| `x-api-key` | Client ID from Developer Console | `1234567890abcdef` |
| `x-gw-ims-org-id` | Organization ID | `ABC123@AdobeOrg` |
| `x-sandbox-name` | Target sandbox name | `prod` or `dev` |
| `Content-Type` | Request content type | `application/json` |

## Token Management Best Practices

### 1. Secure Storage

**DO:**
- Store credentials in environment variables or secret management systems
- Use encrypted storage for cached tokens
- Implement proper access controls

**DON'T:**
- Hardcode credentials in source code
- Commit credentials to version control
- Store tokens in plain text files

### 2. Token Caching

```python
import json
from pathlib import Path
from datetime import datetime

class TokenCache:
    def __init__(self, cache_file='~/.aep_token_cache'):
        self.cache_file = Path(cache_file).expanduser()

    def save(self, token, expiry):
        """Save token with expiry timestamp"""
        cache_data = {
            'token': token,
            'expiry': expiry.isoformat()
        }
        # Ensure file is only readable by owner
        self.cache_file.touch(mode=0o600, exist_ok=True)
        with open(self.cache_file, 'w') as f:
            json.dump(cache_data, f)

    def load(self):
        """Load token if not expired"""
        if not self.cache_file.exists():
            return None

        with open(self.cache_file, 'r') as f:
            cache_data = json.load(f)

        expiry = datetime.fromisoformat(cache_data['expiry'])
        if datetime.now() >= expiry:
            return None

        return cache_data['token']
```

### 3. Automatic Refresh

Implement automatic token refresh before expiry:

```python
def ensure_valid_token(self):
    """Ensure token is valid, refresh if needed"""
    # Refresh 5 minutes before expiry
    buffer_time = timedelta(minutes=5)

    if not self.token_expiry or datetime.now() + buffer_time >= self.token_expiry:
        self.access_token = self.get_access_token()

    return self.access_token
```

## Error Handling

### Common Authentication Errors

| Status Code | Error | Cause | Solution |
|-------------|-------|-------|----------|
| 401 | Unauthorized | Invalid/expired token | Refresh access token |
| 403 | Forbidden | Insufficient permissions | Check product profiles in Admin Console |
| 400 | Bad Request | Invalid credentials | Verify client ID and secret |
| 429 | Rate Limited | Too many auth requests | Implement exponential backoff |

### Example Error Response

```json
{
  "error_code": "401013",
  "message": "Oauth token is not valid",
  "error": "invalid_token"
}
```

### Retry Logic

```python
import time

def get_token_with_retry(auth_helper, max_retries=3):
    """Get token with exponential backoff retry"""
    for attempt in range(max_retries):
        try:
            return auth_helper.get_access_token()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                # Rate limited - use Retry-After header
                wait_time = int(e.response.headers.get('Retry-After', 2 ** attempt))
                time.sleep(wait_time)
            elif 400 <= e.response.status_code < 500:
                # Client error - don't retry
                raise
            else:
                # Server error - retry with backoff
                time.sleep(2 ** attempt)

    raise Exception(f"Failed to get token after {max_retries} attempts")
```

## Testing Authentication

### Verify Token Validity

```bash
curl -X GET 'https://platform.adobe.io/data/core/ups/config/mergePolicies' \
  -H 'Authorization: Bearer {ACCESS_TOKEN}' \
  -H 'x-api-key: {CLIENT_ID}' \
  -H 'x-gw-ims-org-id: {ORG_ID}' \
  -H 'x-sandbox-name: prod'
```

**Success Response (200)**: Token is valid
**Error Response (401)**: Token is invalid or expired

## Environment Configuration

### config.json Structure

```json
{
  "auth_method": "oauth",
  "client_id": "your_client_id",
  "client_secret": "your_client_secret",
  "org_id": "your_org_id@AdobeOrg",
  "sandbox_name": "prod",
  "scopes": [
    "openid",
    "AdobeID",
    "read_organizations",
    "additional_info.projectedProductContext",
    "session"
  ]
}
```

### Environment Variables

```bash
export AEP_CLIENT_ID="your_client_id"
export AEP_CLIENT_SECRET="your_client_secret"
export AEP_ORG_ID="your_org_id@AdobeOrg"
export AEP_SANDBOX="prod"
```

## Security Considerations

1. **Credential Rotation**: Regularly rotate client secrets (recommended: every 90 days)
2. **Scope Limitation**: Only request minimum required scopes
3. **Network Security**: Use HTTPS for all API calls
4. **Audit Logging**: Log authentication events for security monitoring
5. **Access Control**: Limit who can access credentials and tokens

## Additional Resources

- [Adobe I/O Authentication Overview](https://developer.adobe.com/developer-console/docs/guides/authentication/)
- [OAuth Server-to-Server Guide](https://developer.adobe.com/developer-console/docs/guides/authentication/ServerToServerAuthentication/)
- [JWT Deprecation Notice](https://developer.adobe.com/developer-console/docs/guides/authentication/JWT/)
- [Experience Platform API Authentication](https://experienceleague.adobe.com/docs/experience-platform/landing/platform-apis/api-authentication.html)
