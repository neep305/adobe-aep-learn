#!/usr/bin/env python3
"""
Adobe Experience Platform Profile Lookup Tool

Simple CLI tool for looking up customer profiles by identity.
This is the tool referenced in SKILL.md Quick Start section.
"""

import json
import sys
import argparse
from pathlib import Path

# Handle relative import
try:
    from api_client import AEPAPIClient
except ImportError:
    from scripts.api_client import AEPAPIClient


def format_profile_output(profile_data, output_format='pretty'):
    """Format profile data for display

    Args:
        profile_data: Profile response from API
        output_format: 'pretty', 'json', or 'compact'

    Returns:
        str: Formatted output
    """
    if output_format == 'json':
        return json.dumps(profile_data, indent=2)

    if output_format == 'compact':
        return json.dumps(profile_data)

    # Pretty format - extract key information
    if not profile_data or 'entities' not in profile_data:
        return "No profile found"

    entities = profile_data.get('entities', [])
    if not entities:
        return "No profile found"

    profile = entities[0]

    output = []
    output.append("=" * 60)
    output.append("CUSTOMER PROFILE")
    output.append("=" * 60)

    # Profile ID
    if '_id' in profile:
        output.append(f"\nProfile ID: {profile['_id']}")

    # Personal Information
    person = profile.get('person', {})
    name = person.get('name', {})
    if name:
        full_name = f"{name.get('firstName', '')} {name.get('lastName', '')}".strip()
        if full_name:
            output.append(f"\nName: {full_name}")
        if person.get('birthDate'):
            output.append(f"Birth Date: {person['birthDate']}")
        if person.get('gender'):
            output.append(f"Gender: {person['gender']}")

    # Contact Information
    email = profile.get('personalEmail', {})
    if email.get('address'):
        status = email.get('status', 'unknown')
        output.append(f"\nEmail: {email['address']} (status: {status})")

    phone = profile.get('mobilePhone', {}) or profile.get('homePhone', {})
    if phone.get('number'):
        output.append(f"Phone: {phone['number']}")

    # Address
    address = profile.get('homeAddress', {})
    if address:
        addr_parts = []
        if address.get('street1'):
            addr_parts.append(address['street1'])
        if address.get('city'):
            city_state = address['city']
            if address.get('stateProvince'):
                city_state += f", {address['stateProvince']}"
            if address.get('postalCode'):
                city_state += f" {address['postalCode']}"
            addr_parts.append(city_state)
        if address.get('country'):
            addr_parts.append(address['country'])

        if addr_parts:
            output.append(f"\nAddress:")
            for part in addr_parts:
                output.append(f"  {part}")

    # Identities
    identity_map = profile.get('identityMap', {})
    if identity_map:
        output.append(f"\nIdentities:")
        for ns, ids in identity_map.items():
            for id_obj in ids:
                primary = " (primary)" if id_obj.get('primary') else ""
                output.append(f"  {ns}: {id_obj.get('id')}{primary}")

    # Loyalty (if present)
    loyalty = profile.get('loyalty', {})
    if loyalty:
        output.append(f"\nLoyalty:")
        if loyalty.get('tier'):
            output.append(f"  Tier: {loyalty['tier']}")
        if loyalty.get('points') is not None:
            output.append(f"  Points: {loyalty['points']}")

    # Metadata
    repo = profile.get('_repo', {})
    if repo:
        output.append(f"\nMetadata:")
        if repo.get('createDate'):
            output.append(f"  Created: {repo['createDate']}")
        if repo.get('modifyDate'):
            output.append(f"  Modified: {repo['modifyDate']}")

    output.append("\n" + "=" * 60)

    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(
        description='Adobe Experience Platform Profile Lookup',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Lookup by email
  python profile_lookup.py --config config.json --namespace email --value john@example.com

  # Lookup by ECID with specific fields
  python profile_lookup.py --config config.json --namespace ECID --value 12345-67890 --fields person.name personalEmail

  # Output as JSON
  python profile_lookup.py --config config.json --namespace email --value john@example.com --format json

Common Identity Namespaces:
  email           - Email address
  ECID            - Experience Cloud ID
  phone           - Phone number
  crmId           - CRM customer ID
  loyaltyId       - Loyalty program ID
        """
    )

    parser.add_argument(
        '--config',
        required=True,
        help='Path to config JSON file'
    )
    parser.add_argument(
        '--namespace',
        required=True,
        help='Identity namespace (email, ECID, phone, crmId, etc.)'
    )
    parser.add_argument(
        '--value',
        required=True,
        help='Identity value to look up'
    )
    parser.add_argument(
        '--fields',
        nargs='*',
        help='Optional: XDM field paths to return (e.g., person.name personalEmail.address)'
    )
    parser.add_argument(
        '--format',
        choices=['pretty', 'json', 'compact'],
        default='pretty',
        help='Output format (default: pretty)'
    )
    parser.add_argument(
        '--output',
        help='Optional: Write output to file instead of stdout'
    )

    args = parser.parse_args()

    try:
        # Initialize API client
        client = AEPAPIClient(args.config)

        # Lookup profile
        print(f"🔍 Looking up profile: {args.namespace}:{args.value}", file=sys.stderr)
        result = client.get_profile(args.namespace, args.value, args.fields)

        # Format output
        output = format_profile_output(result, args.format)

        # Write to file or stdout
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
            print(f"✓ Profile saved to {args.output}", file=sys.stderr)
        else:
            print(output)

    except FileNotFoundError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        print(f"\nMake sure the config file exists at: {args.config}", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
