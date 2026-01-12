#!/usr/bin/env python3
"""
Adobe Experience Platform Segment Builder Tool

Interactive CLI tool for creating and managing audience segments.
Uses segment_definition_template.json for common segment patterns.
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime

# Handle relative import
try:
    from api_client import AEPAPIClient
except ImportError:
    from scripts.api_client import AEPAPIClient


def load_templates(templates_path=None):
    """Load segment definition templates

    Args:
        templates_path: Optional path to templates file

    Returns:
        dict: Template definitions
    """
    if not templates_path:
        # Try to find templates in default location
        script_dir = Path(__file__).parent
        templates_path = script_dir.parent / 'assets' / 'segment_definition_template.json'

    try:
        with open(templates_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"⚠️  Warning: Template file not found: {templates_path}", file=sys.stderr)
        return {'templates': {}}


def list_templates(templates_data):
    """Display available segment templates

    Args:
        templates_data: Templates data from JSON
    """
    templates = templates_data.get('templates', {})

    if not templates:
        print("No templates available")
        return

    print("\n" + "=" * 70)
    print("AVAILABLE SEGMENT TEMPLATES")
    print("=" * 70)

    for template_id, template in sorted(templates.items()):
        name = template.get('name', 'Unnamed')
        description = template.get('description', 'No description')
        pql = template.get('expression', {}).get('value', 'N/A')

        print(f"\n[{template_id}]")
        print(f"  Name: {name}")
        print(f"  Description: {description}")
        print(f"  PQL: {pql[:80]}{'...' if len(pql) > 80 else ''}")

    print("\n" + "=" * 70)


def customize_segment(template, custom_name=None, custom_description=None,
                     custom_pql=None, merge_policy_id=None):
    """Customize a segment template

    Args:
        template: Template dict to customize
        custom_name: Optional custom name
        custom_description: Optional custom description
        custom_pql: Optional custom PQL expression
        merge_policy_id: Merge policy ID

    Returns:
        dict: Customized segment definition
    """
    segment = template.copy()

    if custom_name:
        segment['name'] = custom_name

    if custom_description:
        segment['description'] = custom_description

    if custom_pql:
        if 'expression' not in segment:
            segment['expression'] = {
                'type': 'PQL',
                'format': 'pql/text'
            }
        segment['expression']['value'] = custom_pql

    if merge_policy_id:
        segment['mergePolicyId'] = merge_policy_id

    # Remove template-only fields
    for key in list(segment.keys()):
        if key.startswith('_'):
            del segment[key]

    return segment


def validate_segment(segment_def):
    """Validate segment definition before creation

    Args:
        segment_def: Segment definition dict

    Returns:
        tuple: (is_valid, error_message)
    """
    required_fields = ['name', 'expression', 'schema']

    for field in required_fields:
        if field not in segment_def:
            return False, f"Missing required field: {field}"

    expression = segment_def.get('expression', {})
    if 'value' not in expression:
        return False, "Missing PQL expression value"

    if not expression.get('value').strip():
        return False, "PQL expression cannot be empty"

    schema = segment_def.get('schema', {})
    if 'name' not in schema:
        return False, "Missing schema name"

    return True, None


def format_segment_output(segment_data, output_format='pretty'):
    """Format segment data for display

    Args:
        segment_data: Segment response from API
        output_format: 'pretty' or 'json'

    Returns:
        str: Formatted output
    """
    if output_format == 'json':
        return json.dumps(segment_data, indent=2)

    # Pretty format
    output = []
    output.append("=" * 70)
    output.append("SEGMENT CREATED SUCCESSFULLY")
    output.append("=" * 70)

    output.append(f"\nSegment ID: {segment_data.get('id', 'N/A')}")
    output.append(f"Name: {segment_data.get('name', 'N/A')}")
    output.append(f"Description: {segment_data.get('description', 'N/A')}")

    expression = segment_data.get('expression', {})
    if expression:
        output.append(f"\nPQL Expression:")
        output.append(f"  {expression.get('value', 'N/A')}")

    evaluation_info = segment_data.get('evaluationInfo', {})
    if evaluation_info:
        output.append(f"\nEvaluation Methods:")
        batch = evaluation_info.get('batch', {})
        continuous = evaluation_info.get('continuous', {})
        synchronous = evaluation_info.get('synchronous', {})

        output.append(f"  Batch: {'enabled' if batch.get('enabled') else 'disabled'}")
        output.append(f"  Streaming: {'enabled' if continuous.get('enabled') else 'disabled'}")
        output.append(f"  Edge: {'enabled' if synchronous.get('enabled') else 'disabled'}")

    output.append(f"\nSchema: {segment_data.get('schema', {}).get('name', 'N/A')}")
    output.append(f"Merge Policy: {segment_data.get('mergePolicyId', 'N/A')}")

    create_time = segment_data.get('createEpoch')
    if create_time:
        output.append(f"\nCreated: {datetime.fromtimestamp(create_time / 1000).isoformat()}")

    output.append("\n" + "=" * 70)

    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(
        description='Adobe Experience Platform Segment Builder',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List available templates
  python segment_builder.py --list-templates

  # Create segment from template
  python segment_builder.py --config config.json --template 5_recent_purchasers --merge-policy YOUR_MERGE_POLICY_ID

  # Create custom segment with your own PQL
  python segment_builder.py --config config.json --name "VIP Customers" --pql "loyalty.tier = 'platinum'"

  # Create from template with customization
  python segment_builder.py --config config.json --template 6_cart_abandoners --name "My Cart Abandoners" --merge-policy YOUR_MERGE_POLICY_ID

  # Create from JSON file
  python segment_builder.py --config config.json --file my_segment.json
        """
    )

    parser.add_argument(
        '--config',
        help='Path to config JSON file (required unless --list-templates)'
    )
    parser.add_argument(
        '--list-templates',
        action='store_true',
        help='List available segment templates and exit'
    )
    parser.add_argument(
        '--template',
        help='Template ID to use (see --list-templates)'
    )
    parser.add_argument(
        '--file',
        help='Path to segment definition JSON file'
    )
    parser.add_argument(
        '--name',
        help='Segment name (overrides template)'
    )
    parser.add_argument(
        '--description',
        help='Segment description (overrides template)'
    )
    parser.add_argument(
        '--pql',
        help='PQL expression (overrides template)'
    )
    parser.add_argument(
        '--merge-policy',
        help='Merge Policy ID (required for segment creation)'
    )
    parser.add_argument(
        '--format',
        choices=['pretty', 'json'],
        default='pretty',
        help='Output format (default: pretty)'
    )
    parser.add_argument(
        '--output',
        help='Optional: Write output to file instead of stdout'
    )
    parser.add_argument(
        '--templates-file',
        help='Path to custom templates file (default: ../assets/segment_definition_template.json)'
    )

    args = parser.parse_args()

    # Load templates
    templates_data = load_templates(args.templates_file)

    # List templates mode
    if args.list_templates:
        list_templates(templates_data)
        return

    # Validate required arguments
    if not args.config:
        parser.error("--config is required (unless using --list-templates)")

    # Determine segment definition source
    segment_def = None

    if args.file:
        # Load from file
        try:
            with open(args.file, 'r') as f:
                segment_def = json.load(f)
            print(f"✓ Loaded segment definition from {args.file}", file=sys.stderr)
        except FileNotFoundError:
            print(f"❌ Error: File not found: {args.file}", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"❌ Error: Invalid JSON in file: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.template:
        # Load from template
        templates = templates_data.get('templates', {})
        if args.template not in templates:
            print(f"❌ Error: Template '{args.template}' not found", file=sys.stderr)
            print(f"\nAvailable templates: {', '.join(templates.keys())}", file=sys.stderr)
            print(f"Use --list-templates to see all templates", file=sys.stderr)
            sys.exit(1)

        template = templates[args.template]
        segment_def = customize_segment(
            template,
            custom_name=args.name,
            custom_description=args.description,
            custom_pql=args.pql,
            merge_policy_id=args.merge_policy
        )
        print(f"✓ Using template: {args.template}", file=sys.stderr)

    elif args.pql:
        # Create from scratch with PQL
        if not args.name:
            parser.error("--name is required when using --pql")

        segment_def = {
            'name': args.name,
            'description': args.description or f"Segment created on {datetime.now().isoformat()}",
            'expression': {
                'type': 'PQL',
                'format': 'pql/text',
                'value': args.pql
            },
            'schema': {
                'name': '_xdm.context.profile'
            },
            'evaluationInfo': {
                'batch': {'enabled': True},
                'continuous': {'enabled': False},
                'synchronous': {'enabled': False}
            }
        }

        if args.merge_policy:
            segment_def['mergePolicyId'] = args.merge_policy

        print(f"✓ Created segment definition from PQL", file=sys.stderr)

    else:
        parser.error("Must specify one of: --template, --file, or --pql")

    # Validate merge policy
    if 'mergePolicyId' not in segment_def or not segment_def['mergePolicyId']:
        print("❌ Error: Merge Policy ID is required", file=sys.stderr)
        print("Use --merge-policy to specify the merge policy ID", file=sys.stderr)
        print("\nTo get merge policy ID, use:", file=sys.stderr)
        print("  curl -X GET 'https://platform.adobe.io/data/core/ups/config/mergePolicies' \\", file=sys.stderr)
        print("    -H 'Authorization: Bearer {TOKEN}' ...", file=sys.stderr)
        sys.exit(1)

    # Validate segment definition
    is_valid, error_msg = validate_segment(segment_def)
    if not is_valid:
        print(f"❌ Error: Invalid segment definition: {error_msg}", file=sys.stderr)
        sys.exit(1)

    try:
        # Initialize API client
        client = AEPAPIClient(args.config)

        # Create segment
        print(f"🔨 Creating segment: {segment_def['name']}", file=sys.stderr)
        result = client.create_segment(segment_def)

        # Format output
        output = format_segment_output(result, args.format)

        # Write to file or stdout
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output if args.format == 'pretty' else json.dumps(result, indent=2))
            print(f"✓ Segment details saved to {args.output}", file=sys.stderr)
        else:
            print(output)

    except FileNotFoundError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
