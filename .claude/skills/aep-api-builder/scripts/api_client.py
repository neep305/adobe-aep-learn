#!/usr/bin/env python3
"""
Adobe Experience Platform API Client

Provides a simple interface for common AEP API operations.
Handles authentication headers and error responses automatically.
"""

import requests
import json
import time
import sys
from pathlib import Path

# Handle relative import
try:
    from auth_helper import AEPAuthHelper
except ImportError:
    # Try absolute import for when running as module
    from scripts.auth_helper import AEPAuthHelper

class AEPAPIClient:
    """Adobe Experience Platform API Client

    Provides methods for common AEP operations:
    - Profile lookup and management
    - Segment (audience) creation and listing
    - Query execution
    - Schema management
    """

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
    
    def get_profile(self, namespace, value, fields=None):
        """Retrieve a customer profile by identity

        Args:
            namespace: Identity namespace (email, ECID, crmId, etc.)
            value: Identity value
            fields: Optional list of XDM field paths to return

        Returns:
            dict: Profile data

        Raises:
            Exception: If profile lookup fails
        """
        url = f'{self.BASE_URL}/data/core/ups/access/entities'

        params = {
            'schema.name': '_xdm.context.profile',
            'entityId': value,
            'entityIdNS': namespace
        }

        if fields:
            params['fields'] = ','.join(fields) if isinstance(fields, list) else fields

        response = requests.get(url, headers=self._get_headers(), params=params)
        return self._handle_response(response, f"Profile lookup for {namespace}:{value}")
    
    def list_segments(self, limit=20, offset=0, filter_property=None):
        """List segment definitions

        Args:
            limit: Number of results per page (max 100)
            offset: Offset for pagination
            filter_property: Optional filter (e.g., 'evaluationInfo.continuous==true')

        Returns:
            dict: Segment definitions list

        Raises:
            Exception: If listing fails
        """
        url = f'{self.BASE_URL}/data/core/ups/segment/definitions'

        params = {
            'limit': min(limit, 100),  # Cap at 100
            'start': offset
        }

        if filter_property:
            params['property'] = filter_property

        response = requests.get(url, headers=self._get_headers(), params=params)
        return self._handle_response(response, "List segments")

    def create_segment(self, segment_definition):
        """Create a new segment definition

        Args:
            segment_definition: Segment definition dict (use segment_definition_template.json)

        Returns:
            dict: Created segment with ID

        Raises:
            Exception: If segment creation fails
        """
        url = f'{self.BASE_URL}/data/core/ups/segment/definitions'

        response = requests.post(url, headers=self._get_headers(), json=segment_definition)
        return self._handle_response(response, "Create segment")

    def get_segment(self, segment_id):
        """Get a specific segment definition

        Args:
            segment_id: Segment ID

        Returns:
            dict: Segment definition

        Raises:
            Exception: If segment not found
        """
        url = f'{self.BASE_URL}/data/core/ups/segment/definitions/{segment_id}'

        response = requests.get(url, headers=self._get_headers())
        return self._handle_response(response, f"Get segment {segment_id}")

    def delete_segment(self, segment_id):
        """Delete a segment definition

        Args:
            segment_id: Segment ID

        Returns:
            dict: Deletion confirmation

        Raises:
            Exception: If deletion fails
        """
        url = f'{self.BASE_URL}/data/core/ups/segment/definitions/{segment_id}'

        response = requests.delete(url, headers=self._get_headers())
        return self._handle_response(response, f"Delete segment {segment_id}")
    
    def execute_query(self, sql, name=None, async_mode=False, timeout=300):
        """Execute SQL query via Query Service

        Args:
            sql: SQL query string
            name: Optional query name for identification
            async_mode: If True, returns immediately with query ID. If False, waits for completion.
            timeout: Max wait time in seconds for sync queries (default 300)

        Returns:
            dict: Query result (sync) or query info (async)

        Raises:
            Exception: If query execution fails
        """
        url = f'{self.BASE_URL}/data/foundation/query/queries'

        payload = {
            'dbName': 'prod:all',
            'sql': sql
        }

        if name:
            payload['name'] = name

        response = requests.post(url, headers=self._get_headers(), json=payload)
        result = self._handle_response(response, "Execute query")

        if async_mode:
            print(f"✓ Query submitted. ID: {result['id']}")
            return result

        # Sync mode: wait for completion
        print(f"⟳ Query submitted. Waiting for completion (timeout: {timeout}s)...")
        return self._wait_for_query(result['id'], timeout)

    def get_query_status(self, query_id):
        """Get query status and details

        Args:
            query_id: Query ID

        Returns:
            dict: Query status and metadata

        Raises:
            Exception: If status check fails
        """
        url = f'{self.BASE_URL}/data/foundation/query/queries/{query_id}'

        response = requests.get(url, headers=self._get_headers())
        return self._handle_response(response, f"Get query status {query_id}")

    def get_query_results(self, query_id, limit=100, offset=0):
        """Get query results

        Args:
            query_id: Query ID
            limit: Number of rows to return
            offset: Row offset for pagination

        Returns:
            dict: Query results

        Raises:
            Exception: If fetching results fails
        """
        url = f'{self.BASE_URL}/data/foundation/query/queries/{query_id}/results'

        params = {
            'limit': limit,
            'offset': offset
        }

        response = requests.get(url, headers=self._get_headers(), params=params)
        return self._handle_response(response, f"Get query results {query_id}")

    def _wait_for_query(self, query_id, timeout=300):
        """Wait for query completion with polling

        Args:
            query_id: Query ID to monitor
            timeout: Max wait time in seconds

        Returns:
            dict: Query results when complete

        Raises:
            Exception: If query fails or times out
        """
        start_time = time.time()
        poll_interval = 2  # Start with 2 second intervals

        while True:
            elapsed = time.time() - start_time

            if elapsed > timeout:
                raise Exception(f"Query {query_id} timed out after {timeout} seconds")

            # Check query status
            status_response = self.get_query_status(query_id)
            state = status_response.get('state')

            if state == 'SUCCESS':
                print(f"✓ Query completed successfully")
                # Fetch and return results
                return self.get_query_results(query_id)

            elif state == 'FAILED':
                error = status_response.get('errors', [{}])[0].get('message', 'Unknown error')
                raise Exception(f"Query {query_id} failed: {error}")

            elif state in ['IN_PROGRESS', 'SUBMITTED']:
                print(f"  Query status: {state} (elapsed: {int(elapsed)}s)", end='\r')
                time.sleep(min(poll_interval, timeout - elapsed))
                # Increase poll interval gradually (max 10 seconds)
                poll_interval = min(poll_interval * 1.2, 10)

            else:
                print(f"⚠️  Unknown query state: {state}", file=sys.stderr)
                time.sleep(poll_interval)

# CLI Interface
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Adobe Experience Platform API Client',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Get customer profile
  python api_client.py --config config.json profile --namespace email --value john@example.com

  # List all segments
  python api_client.py --config config.json segments

  # Create segment from template
  python api_client.py --config config.json create-segment --file segment.json

  # Execute SQL query
  python api_client.py --config config.json query --sql "SELECT COUNT(*) FROM profile_dataset"
        """
    )
    parser.add_argument('--config', required=True, help='Path to config JSON file')

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Profile command
    profile_parser = subparsers.add_parser('profile', help='Get customer profile by identity')
    profile_parser.add_argument('--namespace', required=True, help='Identity namespace (email, ECID, etc.)')
    profile_parser.add_argument('--value', required=True, help='Identity value')
    profile_parser.add_argument('--fields', nargs='*', help='XDM field paths to return')

    # List segments command
    segments_parser = subparsers.add_parser('segments', help='List segment definitions')
    segments_parser.add_argument('--limit', type=int, default=20, help='Number of results (max 100)')
    segments_parser.add_argument('--filter', help='Filter property (e.g., evaluationInfo.continuous==true)')

    # Get segment command
    get_segment_parser = subparsers.add_parser('get-segment', help='Get specific segment')
    get_segment_parser.add_argument('--id', required=True, help='Segment ID')

    # Create segment command
    create_segment_parser = subparsers.add_parser('create-segment', help='Create new segment')
    create_segment_parser.add_argument('--file', required=True, help='Path to segment definition JSON')

    # Query command
    query_parser = subparsers.add_parser('query', help='Execute SQL query')
    query_parser.add_argument('--sql', required=True, help='SQL query string')
    query_parser.add_argument('--name', help='Optional query name')
    query_parser.add_argument('--async', action='store_true', help='Run asynchronously')
    query_parser.add_argument('--timeout', type=int, default=300, help='Timeout in seconds (for sync queries)')

    # Query status command
    query_status_parser = subparsers.add_parser('query-status', help='Check query status')
    query_status_parser.add_argument('--id', required=True, help='Query ID')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        client = AEPAPIClient(args.config)

        if args.command == 'profile':
            result = client.get_profile(args.namespace, args.value, args.fields)
            print(json.dumps(result, indent=2))

        elif args.command == 'segments':
            result = client.list_segments(args.limit, filter_property=args.filter)
            print(json.dumps(result, indent=2))

        elif args.command == 'get-segment':
            result = client.get_segment(args.id)
            print(json.dumps(result, indent=2))

        elif args.command == 'create-segment':
            with open(args.file, 'r') as f:
                segment_def = json.load(f)
            result = client.create_segment(segment_def)
            print(json.dumps(result, indent=2))

        elif args.command == 'query':
            result = client.execute_query(
                args.sql,
                name=args.name,
                async_mode=getattr(args, 'async'),
                timeout=args.timeout
            )
            print(json.dumps(result, indent=2))

        elif args.command == 'query-status':
            result = client.get_query_status(args.id)
            print(json.dumps(result, indent=2))

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)