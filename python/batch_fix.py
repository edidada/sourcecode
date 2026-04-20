#!/usr/bin/env python3
"""Batch fix Python 2 files to Python 3 compatible"""

import os
import re

def fix_python_file(filepath, use_guest=False):
    """Fix a single Python file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Fix print statements - handle various cases
    content = re.sub(r'^(\s*)print\s+([^(].*)$', r'\1print(\2)', content, flags=re.MULTILINE)
    
    # Fix type="direct" to exchange_type="direct"
    content = re.sub(r'type="(\w+)"', r'exchange_type="\1"', content)
    
    # Fix callback signatures
    content = re.sub(r'def\s+(\w+)\(channel,\s*method,\s*header,\s*body\)', r'def \1(ch, method, properties, body)', content)
    
    # Fix basic_consume calls
    content = re.sub(r'channel\.basic_consume\(\s*(\w+),\s*queue=', r'channel.basic_consume(queue=', content)
    content = re.sub(r'channel\.basic_consume\((\w+),', r'channel.basic_consume(on_message_callback=\1,', content)
    content = re.sub(r'channel\.basic_consume\(\s*([^,]+),\s*queue=', r'channel.basic_consume(queue=', content)
    
    # Fix queue_declare with exclusive
    content = re.sub(r'queue_declare\(exclusive=True', r"queue_declare(queue='', exclusive=True", content)
    
    # Fix except syntax
    content = re.sub(r'except\s+(\w+),\s*(\w+):', r'except \1 as \2:', content)
    
    # Fix body string comparison
    content = re.sub(r'if body == "quit"', r'if body.decode(\'utf-8\') == "quit"', content)
    content = re.sub(r'print\(body\)', r'print(body.decode(\'utf-8\'))', content)
    
    # Add config support if not present
    if 'config.ini' not in content and 'localhost' in content:
        # Add imports
        if 'from configparser import ConfigParser' not in content:
            content = content.replace('import pika', 'import pika, os, sys\nfrom configparser import ConfigParser')
        
        # Replace connection parameters
        if use_guest:
            # For chapter-2 examples using guest
            old_pattern = r'credentials = pika\.PlainCredentials\("guest", "guest"\)\nconn_params = pika\.ConnectionParameters\("localhost",\s*credentials = credentials\)'
            new_code = '''# Read configuration from config file
config = ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), '..', 'chapter-4', 'config.ini'))

# Get environment from ENV or default to 'dev'
env = os.environ.get('RABBITMQ_ENV', 'dev')
if env not in config.sections():
    print(f"Error: Environment '{env}' not found in config.ini")
    sys.exit(1)

# Use guest credentials for chapter-2 examples
credentials = pika.PlainCredentials("guest", "guest")
conn_params = pika.ConnectionParameters(
    host=config.get(env, 'host'),
    port=config.getint(env, 'port'),
    credentials=credentials
)'''
            content = re.sub(old_pattern, new_code, content)
        else:
            # For other examples using rpc_user
            old_pattern = r'creds_broker = pika\.PlainCredentials\("rpc_user", "rpcme"\)\nconn_params = pika\.ConnectionParameters\("localhost",\s*virtual_host = "/",\s*credentials = creds_broker\)'
            new_code = '''# Read configuration from config file
config = ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), '..', 'chapter-4', 'config.ini'))

# Get environment from ENV or default to 'dev'
env = os.environ.get('RABBITMQ_ENV', 'dev')
if env not in config.sections():
    print(f"Error: Environment '{env}' not found in config.ini")
    sys.exit(1)

# Use rpc_user credentials
creds_broker = pika.PlainCredentials(
    config.get(env, 'username'),
    config.get(env, 'password')
)
conn_params = pika.ConnectionParameters(
    host=config.get(env, 'host'),
    port=config.getint(env, 'port'),
    virtual_host=config.get(env, 'virtual_host'),
    credentials=creds_broker
)'''
            content = re.sub(old_pattern, new_code, content)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed: {filepath}")
        return True
    else:
        print(f"No changes: {filepath}")
        return False

if __name__ == "__main__":
    import sys
    
    chapters = ['chapter-2', 'chapter-5', 'chapter-6', 'chapter-7', 'chapter-9', 'chapter-10']
    
    for chapter in chapters:
        chapter_dir = os.path.join('python', chapter)
        if os.path.exists(chapter_dir):
            for filename in os.listdir(chapter_dir):
                if filename.endswith('.py'):
                    filepath = os.path.join(chapter_dir, filename)
                    use_guest = (chapter == 'chapter-2')
                    try:
                        fix_python_file(filepath, use_guest)
                    except Exception as e:
                        print(f"Error fixing {filepath}: {e}")
