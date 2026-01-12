# XDM Schemas Reference

Complete guide to Experience Data Model (XDM) schemas and field paths in Adobe Experience Platform.

## XDM Overview

Experience Data Model (XDM) is the standardization framework that Adobe Experience Platform uses to organize customer experience data.

### Core Concepts

**Schema Components:**
- **Class**: Base template defining the data type (Profile vs Event)
- **Field Groups**: Reusable sets of fields
- **Data Types**: Complex field structures
- **Mixins**: Legacy term for Field Groups

**Schema Types:**
- **XDM Individual Profile**: Customer attributes (who they are)
- **XDM ExperienceEvent**: Behavioral data (what they did)
- **Custom Classes**: Organization-specific data models

## XDM Individual Profile Class

Used for customer attribute data. Each profile represents a single person.

### Standard Field Groups

#### 1. Profile Core (Always Included)

```json
{
  "_id": "string",                    // Unique profile identifier
  "identityMap": {                    // Identity graph connections
    "email": [
      {
        "id": "john@example.com",
        "primary": true
      }
    ],
    "ECID": [
      {
        "id": "12345-67890-ABCDE"
      }
    ]
  },
  "_repo": {
    "createDate": "2024-01-15T10:30:00Z",
    "modifyDate": "2024-01-20T15:45:00Z"
  }
}
```

#### 2. Demographic Details

Field Group ID: `profile-person-details`

```json
{
  "person": {
    "name": {
      "firstName": "string",
      "lastName": "string",
      "middleName": "string",
      "fullName": "string",
      "courtesyTitle": "string"      // Mr., Ms., Dr., etc.
    },
    "birthDate": "YYYY-MM-DD",
    "birthDayAndMonth": "MM-DD",
    "gender": "male|female|not_specified|non_specific"
  }
}
```

**Field Paths:**
- `person.name.firstName`
- `person.name.lastName`
- `person.birthDate`
- `person.gender`

#### 3. Personal Contact Details

Field Group ID: `profile-personal-details`

```json
{
  "homeAddress": {
    "street1": "string",
    "street2": "string",
    "city": "string",
    "stateProvince": "string",
    "postalCode": "string",
    "country": "string",
    "countryCode": "string",           // ISO 3166-1 alpha-2
    "latitude": "number",
    "longitude": "number"
  },
  "personalEmail": {
    "address": "string",
    "status": "active|incomplete|pending_verification|blacklisted",
    "statusReason": "string"
  },
  "homePhone": {
    "number": "string",
    "status": "active|incomplete|blacklisted",
    "primary": "boolean"
  },
  "mobilePhone": {
    "number": "string",
    "status": "active|incomplete|blacklisted",
    "primary": "boolean"
  },
  "faxPhone": {
    "number": "string"
  }
}
```

**Field Paths:**
- `homeAddress.city`
- `homeAddress.postalCode`
- `personalEmail.address`
- `mobilePhone.number`

#### 4. Profile Preferences

Field Group ID: `profile-preferences-details`

```json
{
  "optInOut": {
    "email": {
      "optOut": "boolean",
      "timestamp": "datetime",
      "reason": "string"
    },
    "push": {
      "optOut": "boolean"
    },
    "sms": {
      "optOut": "boolean"
    },
    "globalOptout": "boolean"
  },
  "subscriptions": {
    "newsletter": "boolean",
    "promotions": "boolean"
  }
}
```

#### 5. Loyalty Details

Field Group ID: `profile-loyalty-details`

```json
{
  "loyalty": {
    "loyaltyID": ["string"],
    "points": "number",
    "pointsExpiration": "datetime",
    "tier": "string",                  // bronze, silver, gold, platinum
    "joinDate": "datetime",
    "upgradeDate": "datetime"
  }
}
```

#### 6. Work Contact Details

Field Group ID: `profile-work-details`

```json
{
  "workAddress": {
    "street1": "string",
    "city": "string",
    "stateProvince": "string",
    "postalCode": "string",
    "country": "string"
  },
  "workEmail": {
    "address": "string",
    "status": "active|incomplete|pending_verification|blacklisted"
  },
  "workPhone": {
    "number": "string",
    "primary": "boolean"
  },
  "organizations": ["string"]
}
```

## XDM ExperienceEvent Class

Used for behavioral and time-series data. Each event is immutable and timestamped.

### Standard Field Groups

#### 1. ExperienceEvent Core (Always Included)

```json
{
  "_id": "string",                     // Unique event identifier (UUID)
  "timestamp": "datetime",             // Required: when event occurred
  "eventType": "string",               // Event classification
  "identityMap": {                     // Identity at time of event
    "ECID": [
      {
        "id": "12345-67890-ABCDE"
      }
    ]
  }
}
```

**Common Event Types:**
- `web.webpagedetails.pageViews`
- `commerce.productViews`
- `commerce.productListAdds`
- `commerce.purchases`
- `advertising.impressions`
- `advertising.clicks`

#### 2. Web Details

Field Group ID: `experience-event-web-details`

```json
{
  "web": {
    "webPageDetails": {
      "URL": "string",
      "name": "string",
      "pageViews": {
        "value": 1
      },
      "server": "string",
      "isErrorPage": "boolean",
      "isHomePage": "boolean",
      "siteSection": "string"
    },
    "webReferrer": {
      "URL": "string",
      "type": "internal|external|search_engine|social_network"
    },
    "webInteraction": {
      "name": "string",                // Click name
      "type": "click|download|submit",
      "URL": "string",
      "linkClicks": {
        "value": 1
      }
    }
  }
}
```

**Field Paths:**
- `web.webPageDetails.URL`
- `web.webPageDetails.name`
- `web.webReferrer.URL`
- `web.webInteraction.type`

#### 3. Commerce Details

Field Group ID: `experience-event-commerce-details`

```json
{
  "commerce": {
    "order": {
      "purchaseID": "string",
      "currencyCode": "string",        // ISO 4217
      "priceTotal": "number",
      "payments": [
        {
          "paymentAmount": "number",
          "paymentType": "credit_card|debit_card|paypal|gift_card",
          "transactionID": "string"
        }
      ]
    },
    "productViews": {
      "value": 1
    },
    "productListAdds": {
      "value": 1
    },
    "checkouts": {
      "value": 1
    },
    "purchases": {
      "value": 1
    },
    "productListRemovals": {
      "value": 1
    },
    "saveForLaters": {
      "value": 1
    }
  },
  "productListItems": [
    {
      "SKU": "string",
      "name": "string",
      "quantity": "number",
      "priceTotal": "number",
      "currencyCode": "string",
      "productImageUrl": "string",
      "productCategories": [
        {
          "categoryID": "string",
          "categoryName": "string"
        }
      ]
    }
  ]
}
```

**Field Paths:**
- `commerce.order.purchaseID`
- `commerce.order.priceTotal`
- `commerce.purchases.value`
- `productListItems[].SKU`
- `productListItems[].name`
- `productListItems[].quantity`

#### 4. Environment Details

Field Group ID: `experience-event-environment-details`

```json
{
  "environment": {
    "type": "browser|application|iot|external",
    "browserDetails": {
      "name": "string",
      "vendor": "string",
      "version": "string",
      "userAgent": "string",
      "acceptLanguage": "string",
      "cookiesEnabled": "boolean",
      "javaScriptEnabled": "boolean",
      "javaScriptVersion": "string",
      "viewportHeight": "integer",
      "viewportWidth": "integer"
    },
    "operatingSystem": "string",
    "operatingSystemVersion": "string",
    "colorDepth": "integer",
    "viewportHeight": "integer",
    "viewportWidth": "integer",
    "connectionType": "wifi|3g|4g|5g|ethernet"
  },
  "device": {
    "type": "mobile|tablet|desktop|ereader|gaming|television|settop|mediaplayer",
    "manufacturer": "string",
    "model": "string",
    "modelNumber": "string",
    "screenHeight": "integer",
    "screenWidth": "integer",
    "colorDepth": "integer"
  }
}
```

#### 5. Marketing Details

Field Group ID: `experience-event-marketing-details`

```json
{
  "marketing": {
    "campaignName": "string",
    "campaignID": "string",
    "campaignGroup": "string",
    "trackingCode": "string"
  },
  "directMarketing": {
    "sends": {
      "value": 1
    },
    "opens": {
      "value": 1
    },
    "clicks": {
      "value": 1
    },
    "bounces": {
      "value": 1,
      "type": "hard|soft"
    },
    "unsubscriptions": {
      "value": 1
    }
  },
  "advertising": {
    "adAssetReference": {
      "assetID": "string",
      "assetName": "string",
      "creativeID": "string",
      "placementID": "string",
      "siteID": "string"
    },
    "impressions": {
      "value": 1
    },
    "clicks": {
      "value": 1
    },
    "conversions": {
      "value": 1
    }
  }
}
```

## Custom Field Groups

### Creating Custom Fields

Custom fields must use tenant namespace:

```json
{
  "_tenantId": {
    "customField1": "string",
    "customObject": {
      "nestedField": "string",
      "nestedArray": ["string"]
    }
  }
}
```

**Field Path Convention:**
- Custom fields: `_{TENANT_ID}.fieldName`
- Example: `_acme.customerScore`

### Data Types

Common XDM data types:

| Type | Description | Example |
|------|-------------|---------|
| `string` | Text value | `"John Doe"` |
| `integer` | Whole number | `42` |
| `number` | Decimal number | `99.99` |
| `boolean` | True/false | `true` |
| `date` | Date only | `"2024-01-15"` |
| `date-time` | ISO 8601 timestamp | `"2024-01-15T10:30:00Z"` |
| `object` | Nested structure | `{"key": "value"}` |
| `array` | List of values | `["item1", "item2"]` |

## Union Schema

Union schema combines all schemas sharing the same class for profile queries.

### Querying Union Schema

```sql
-- Profile union schema
SELECT * FROM profile_union_schema
WHERE personalEmail.address = 'john@example.com'

-- Event union schema
SELECT * FROM experience_event_union_schema
WHERE timestamp >= '2024-01-01'
  AND eventType = 'commerce.purchases'
```

## Field Path Syntax

### Dot Notation

Access nested fields using dots:

```
person.name.firstName
homeAddress.city
commerce.order.purchaseID
```

### Array Access

Access array elements:

```
productListItems[0].SKU              # First item
productListItems[*].SKU              # All items (some contexts)
```

### Identity Map

Special syntax for identity map:

```
identityMap.email[0].id
identityMap.ECID[*].id
```

## Working with Schemas via API

### List Schemas

```bash
GET /data/foundation/schemaregistry/tenant/schemas
Accept: application/vnd.adobe.xed-id+json
```

### Get Schema Definition

```bash
GET /data/foundation/schemaregistry/tenant/schemas/{SCHEMA_ID}
Accept: application/vnd.adobe.xed+json
```

### Get Field Descriptors

```bash
GET /data/foundation/schemaregistry/tenant/descriptors
```

## Common Field Patterns

### Identity Fields

Fields commonly used as identities:

- `personalEmail.address` - Email namespace
- `mobilePhone.number` - Phone namespace
- `_tenantId.crmId` - CRM ID namespace
- `identityMap.ECID` - Experience Cloud ID

### Primary Identity Configuration

Each schema must have one primary identity:

```json
{
  "meta:xdmField": "personalEmail.address",
  "meta:descriptors": [
    {
      "@type": "xdm:descriptorIdentity",
      "xdm:namespace": "email",
      "xdm:property": "personalEmail.address",
      "xdm:isPrimary": true
    }
  ]
}
```

### Profile-Enabled Fields

Fields enabled for Real-Time Customer Profile:

```json
{
  "meta:immutableTags": [
    "union"
  ]
}
```

## Best Practices

1. **Use Standard Field Groups**: Leverage Adobe's pre-built field groups before creating custom ones
2. **Consistent Naming**: Use camelCase for custom field names
3. **Namespace Custom Fields**: Always use tenant namespace for custom fields
4. **Document Field Usage**: Add descriptions to custom field groups
5. **Plan Identity Strategy**: Choose identity fields carefully - they can't be changed after ingestion
6. **Avoid Deep Nesting**: Keep field hierarchy shallow (max 3-4 levels)
7. **Use Appropriate Types**: Choose correct data type to enable proper validation

## Troubleshooting

### Common Issues

**Field Not Found:**
- Verify field path syntax (case-sensitive)
- Check if field group is added to schema
- Confirm schema is profile-enabled

**Identity Resolution Failed:**
- Verify identity namespace exists
- Check if field is marked as identity
- Confirm identity value format matches namespace rules

**Data Validation Failed:**
- Check data type matches schema definition
- Verify required fields are present
- Ensure enum values match allowed list

## Additional Resources

- [XDM System Overview](https://experienceleague.adobe.com/docs/experience-platform/xdm/home.html)
- [Schema Registry API Guide](https://experienceleague.adobe.com/docs/experience-platform/xdm/api/getting-started.html)
- [Standard Field Groups Reference](https://experienceleague.adobe.com/docs/experience-platform/xdm/schema/field-groups/overview.html)
- [XDM GitHub Repository](https://github.com/adobe/xdm)
