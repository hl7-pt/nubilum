#!/usr/bin/env python3
"""
Translation management script for Nubilum.

This script helps manage translations by providing commands to:
- Extract translatable strings from source code
- Initialize a new language
- Update existing translations
- Compile translations to binary .mo files
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a shell command and handle errors."""
    print(f"\n{description}...")
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(1)

    print(result.stdout)
    print(f"✓ {description} completed successfully")


def extract_messages():
    """Extract translatable strings from source code."""
    cmd = [
        'pybabel', 'extract',
        '-F', 'babel.cfg',
        '-k', '_',
        '-k', '_l',
        '-o', 'nubilum/translations/messages.pot',
        '.'
    ]
    run_command(cmd, "Extracting translatable strings")


def init_language(lang):
    """Initialize a new language."""
    cmd = [
        'pybabel', 'init',
        '-i', 'nubilum/translations/messages.pot',
        '-d', 'nubilum/translations',
        '-l', lang
    ]
    run_command(cmd, f"Initializing {lang} translations")
    print(f"\n✓ Language '{lang}' initialized successfully!")
    print(f"Edit the translation file at: nubilum/translations/{lang}/LC_MESSAGES/messages.po")


def update_translations():
    """Update existing translations with new strings."""
    translations_dir = Path('nubilum/translations')

    # First extract the latest strings
    extract_messages()

    # Find all language directories
    lang_dirs = [d for d in translations_dir.iterdir()
                 if d.is_dir() and not d.name.startswith('.')]

    if not lang_dirs:
        print("No translations found. Use 'init' to create a new language.")
        return

    for lang_dir in lang_dirs:
        lang = lang_dir.name
        cmd = [
            'pybabel', 'update',
            '-i', 'nubilum/translations/messages.pot',
            '-d', 'nubilum/translations',
            '-l', lang
        ]
        run_command(cmd, f"Updating {lang} translations")


def compile_translations():
    """Compile translations to binary .mo files."""
    cmd = [
        'pybabel', 'compile',
        '-d', 'nubilum/translations'
    ]
    run_command(cmd, "Compiling translations")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Manage translations for Nubilum',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract translatable strings
  python manage_translations.py extract

  # Initialize a new language (e.g., Spanish)
  python manage_translations.py init es

  # Update all existing translations
  python manage_translations.py update

  # Compile translations
  python manage_translations.py compile

  # Full workflow: extract, update, and compile
  python manage_translations.py extract
  python manage_translations.py update
  # Edit translation files...
  python manage_translations.py compile
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Extract command
    subparsers.add_parser('extract', help='Extract translatable strings from source code')

    # Init command
    init_parser = subparsers.add_parser('init', help='Initialize a new language')
    init_parser.add_argument('language', help='Language code (e.g., pt, es, fr)')

    # Update command
    subparsers.add_parser('update', help='Update existing translations with new strings')

    # Compile command
    subparsers.add_parser('compile', help='Compile translations to binary .mo files')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Execute command
    if args.command == 'extract':
        extract_messages()
    elif args.command == 'init':
        init_language(args.language)
    elif args.command == 'update':
        update_translations()
    elif args.command == 'compile':
        compile_translations()


if __name__ == '__main__':
    main()
