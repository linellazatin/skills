#!/usr/bin/env python3
"""Portable Skill Buffer CLI. Paths and credentials are always explicit."""
import argparse
from pathlib import Path
import sys

sys.dont_write_bytecode = True
if sys.version_info < (3, 13):
    raise SystemExit('Python 3.13+ required')
import yaml
if yaml.__version__ != '6.0.3':
    raise SystemExit('PyYAML==6.0.3 required')

from buffer_core import DEFAULT_SETTINGS, freeze, import_responses, inspect, read_json, write_json
from buffer_http import evaluate
from buffer_review import brief, compare, grade, record


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('inspect')
    p.add_argument('--input', required=True)
    p.add_argument('--output', required=True)
    p = sub.add_parser('freeze')
    for key in ('baseline', 'candidate', 'suite', 'output'):
        p.add_argument('--' + key, required=True)
    p.add_argument('--settings', help='JSON settings overrides')
    p = sub.add_parser('import-responses')
    p.add_argument('--workspace', required=True)
    p.add_argument('--input', required=True)
    p = sub.add_parser('evaluate')
    for key in ('workspace', 'endpoint', 'model'):
        p.add_argument('--' + key, required=True)
    p.add_argument('--api-key-env')
    p.add_argument('--token-field', choices=('max_tokens', 'max_completion_tokens'), default='max_tokens')
    p.add_argument('--resume', action='store_true')
    for command in ('grade', 'compare'):
        p = sub.add_parser(command)
        p.add_argument('--workspace', required=True)
        p.add_argument('--input', required=True)
        p.add_argument('--output', required=True)
    p = sub.add_parser('enhance')
    enhancement = p.add_subparsers(dest='action', required=True)
    p = enhancement.add_parser('brief')
    for key in ('workspace', 'input', 'output'):
        p.add_argument('--' + key, required=True)
    p = enhancement.add_parser('record')
    for key in ('workspace', 'candidate', 'input', 'output'):
        p.add_argument('--' + key, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == 'inspect':
            result = inspect(args.input)
            write_json(args.output, result)
        elif args.command == 'freeze':
            result = freeze(args.baseline, args.candidate, read_json(args.suite), args.output, read_json(args.settings) if args.settings else None)
        elif args.command == 'import-responses':
            result = import_responses(args.workspace, read_json(args.input))
        elif args.command == 'evaluate':
            result = evaluate(args.workspace, args.endpoint, args.model, args.api_key_env, args.resume, args.token_field)
        elif args.command == 'grade':
            result = grade(args.workspace, read_json(args.input), args.output)
        elif args.command == 'compare':
            result = compare(args.workspace, read_json(args.input), args.output)
        elif args.action == 'brief':
            result = brief(args.workspace, read_json(args.input), args.output)
        else:
            result = record(args.workspace, args.candidate, read_json(args.input), args.output)
        print(f'{args.command}: completed')
        return 1 if result.get('stopped') or result.get('structural_findings') else 0
    except (OSError, ValueError, TypeError, KeyError, yaml.YAMLError) as error:
        print(f'error: {error}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
