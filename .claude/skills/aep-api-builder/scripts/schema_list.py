#!/usr/bin/env python3
"""
Adobe Experience Platform Schema Registry Client

Lists and retrieves XDM schemas from your AEP instance.
"""

import requests
import json
import sys
from pathlib import Path

try:
    from auth_helper import AEPAuthHelper
except ImportError:
    from scripts.auth_helper import AEPAuthHelper


class AEPSchemaClient:
    """Adobe Experience Platform Schema Registry Client"""

    BASE_URL = 'https://platform.adobe.io'

    def __init__(self, config_path):
        """Initialize with config file

        Args:
            config_path: Path to JSON config file

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config is invalid
        """
        try:
            self.auth = AEPAuthHelper(config_path)

            with open(config_path, 'r') as f:
                config = json.load(f)

            self.client_id = config['client_id']
            self.org_id = config['org_id']
            self.sandbox = config.get('sandbox_name', 'prod')

        except FileNotFoundError:
            raise FileNotFoundError(f"Config file not found: {config_path}")
        except (json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"Invalid config file: {e}")

    def _get_headers(self, accept_type='application/json'):
        """Generate request headers with authentication

        Args:
            accept_type: Accept header value for specific response formats

        Returns:
            dict: Headers dictionary with authentication
        """
        return {
            'Authorization': f'Bearer {self.auth.get_access_token()}',
            'x-api-key': self.client_id,
            'x-gw-ims-org-id': self.org_id,
            'x-sandbox-name': self.sandbox,
            'Content-Type': 'application/json',
            'Accept': accept_type
        }

    def _handle_response(self, response, operation_name="API call"):
        """Handle API response with proper error messages

        Args:
            response: requests.Response object
            operation_name: Description of the operation for error messages

        Returns:
            dict: Parsed JSON response

        Raises:
            Exception: With user-friendly error message
        """
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            status_code = response.status_code

            # Try to get error details from response
            try:
                error_detail = response.json()
                error_msg = error_detail.get('detail', error_detail.get('message', str(e)))
            except:
                error_msg = str(e)

            # Provide helpful error messages
            if status_code == 401:
                raise Exception(f"{operation_name} failed: Unauthorized. Token may be expired. Error: {error_msg}")
            elif status_code == 403:
                raise Exception(f"{operation_name} failed: Forbidden. Check permissions and sandbox access. Error: {error_msg}")
            elif status_code == 404:
                raise Exception(f"{operation_name} failed: Resource not found. Error: {error_msg}")
            elif status_code == 429:
                raise Exception(f"{operation_name} failed: Rate limit exceeded. Retry after some time. Error: {error_msg}")
            elif status_code >= 500:
                raise Exception(f"{operation_name} failed: Server error. Try again later. Error: {error_msg}")
            else:
                raise Exception(f"{operation_name} failed: {error_msg}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"{operation_name} failed: Network error - {e}")

    def list_schemas(self, limit=100, offset=0, id_only=False, scope='tenant'):
        """List all XDM schemas

        Args:
            limit: Number of results per page (max 500)
            offset: Offset for pagination
            id_only: If True, returns only schema IDs and titles. If False, returns full schemas.
            scope: Schema scope - 'tenant' for custom schemas, 'global' for Adobe schemas

        Returns:
            dict: Schema list with results and metadata

        Raises:
            Exception: If listing fails
        """
        url = f'{self.BASE_URL}/data/foundation/schemaregistry/{scope}/schemas'

        params = {
            'limit': min(limit, 500)
        }

        # Only include start parameter if offset is not 0
        if offset:
            params['start'] = offset

        # Choose accept header based on detail level
        accept_type = 'application/vnd.adobe.xed-id+json' if id_only else 'application/vnd.adobe.xed+json'

        response = requests.get(url, headers=self._get_headers(accept_type), params=params)
        return self._handle_response(response, "List schemas")

    def get_schema(self, schema_id):
        """Get a specific schema by ID

        Args:
            schema_id: Schema ID or $id value

        Returns:
            dict: Full schema definition

        Raises:
            Exception: If schema not found
        """
        # URL encode the schema ID
        from urllib.parse import quote
        encoded_id = quote(schema_id, safe='')

        url = f'{self.BASE_URL}/data/foundation/schemaregistry/tenant/schemas/{encoded_id}'

        response = requests.get(url, headers=self._get_headers('application/vnd.adobe.xed+json'))
        return self._handle_response(response, f"Get schema {schema_id}")

    def list_classes(self, limit=100):
        """List available XDM classes

        Returns:
            dict: List of XDM classes
        """
        url = f'{self.BASE_URL}/data/foundation/schemaregistry/global/classes'

        params = {'limit': limit}

        response = requests.get(url, headers=self._get_headers('application/vnd.adobe.xed-id+json'), params=params)
        return self._handle_response(response, "List classes")

    def list_fieldgroups(self, limit=100):
        """List available field groups (mixins)

        Returns:
            dict: List of field groups
        """
        url = f'{self.BASE_URL}/data/foundation/schemaregistry/tenant/fieldgroups'

        params = {'limit': limit}

        response = requests.get(url, headers=self._get_headers('application/vnd.adobe.xed-id+json'), params=params)
        return self._handle_response(response, "List field groups")


# CLI Interface
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Adobe Experience Platform Schema Registry Client',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all schemas (summary)
  python schema_list.py --config config.json list

  # List schemas with full details
  python schema_list.py --config config.json list --full

  # Get specific schema
  python schema_list.py --config config.json get --id "https://ns.adobe.com/..."

  # List available classes
  python schema_list.py --config config.json classes

  # List field groups
  python schema_list.py --config config.json fieldgroups
        """
    )
    parser.add_argument('--config', required=True, help='Path to config JSON file')

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # List schemas command
    list_parser = subparsers.add_parser('list', help='List all schemas')
    list_parser.add_argument('--limit', type=int, default=100, help='Number of results (max 500)')
    list_parser.add_argument('--offset', type=int, default=0, help='Offset for pagination')
    list_parser.add_argument('--full', action='store_true', help='Return full schema details')
    list_parser.add_argument('--scope', choices=['tenant', 'global'], default='tenant', help='Schema scope (tenant=custom, global=Adobe)')

    # Get schema command
    get_parser = subparsers.add_parser('get', help='Get specific schema')
    get_parser.add_argument('--id', required=True, help='Schema ID')

    # List classes command
    classes_parser = subparsers.add_parser('classes', help='List XDM classes')
    classes_parser.add_argument('--limit', type=int, default=100, help='Number of results')

    # List field groups command
    fg_parser = subparsers.add_parser('fieldgroups', help='List field groups')
    fg_parser.add_argument('--limit', type=int, default=100, help='Number of results')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        client = AEPSchemaClient(args.config)

        if args.command == 'list':
            result = client.list_schemas(
                limit=args.limit,
                offset=args.offset,
                id_only=not args.full,
                scope=args.scope
            )

            # Pretty print with summary
            print(f"\n{'='*80}")
            print(f"XDM Schemas [{args.scope.upper()}] (Total: {len(result.get('results', []))})")
            print(f"{'='*80}\n")

            for idx, schema in enumerate(result.get('results', []), 1):
                print(f"{idx}. {schema.get('title', 'Untitled Schema')}")
                print(f"   ID: {schema.get('$id', schema.get('meta:altId', 'N/A'))}")
                if 'meta:class' in schema:
                    print(f"   Class: {schema['meta:class']}")
                if 'version' in schema:
                    print(f"   Version: {schema['version']}")
                print()

        elif args.command == 'get':
            result = client.get_schema(args.id)
            print(json.dumps(result, indent=2))

        elif args.command == 'classes':
            result = client.list_classes(args.limit)

            print(f"\n{'='*80}")
            print(f"XDM Classes (Total: {len(result.get('results', []))})")
            print(f"{'='*80}\n")

            for idx, cls in enumerate(result.get('results', []), 1):
                print(f"{idx}. {cls.get('title', 'Untitled Class')}")
                print(f"   ID: {cls.get('$id', 'N/A')}")
                print()

        elif args.command == 'fieldgroups':
            result = client.list_fieldgroups(args.limit)

            print(f"\n{'='*80}")
            print(f"Field Groups (Total: {len(result.get('results', []))})")
            print(f"{'='*80}\n")

            for idx, fg in enumerate(result.get('results', []), 1):
                print(f"{idx}. {fg.get('title', 'Untitled Field Group')}")
                print(f"   ID: {fg.get('$id', 'N/A')}")
                print()

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
