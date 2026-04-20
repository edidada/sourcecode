#!/usr/bin/env python3
"""Fix all Python files with proper template"""

import os
import re

CHAPTER_2_5_TEMPLATE = '''###############################################
# {title}
# 
# Requires: pika >= 0.9.5
# 
# Author: Jason J. W. Williams
# (C)2011
###############################################

import pika, os, sys
from configparser import ConfigParser

# Read configuration from config file
config = ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), '..', 'chapter-4', 'config.ini'))

# Get environment from ENV or default to 'dev'
env = os.environ.get('RABBITMQ_ENV', 'dev')
if env not in config.sections():
    print(f"Error: Environment '{{env}}' not found in config.ini")
    sys.exit(1)

# Use guest credentials
credentials = pika.PlainCredentials("guest", "guest")
conn_params = pika.ConnectionParameters(
    host=config.get(env, 'host'),
    port=config.getint(env, 'port'),
    credentials=credentials
)
conn_broker = pika.BlockingConnection(conn_params)
'''

CHAPTER_6_7_TEMPLATE = '''###############################################
# {title}
# 
# Requires: pika >= 0.9.5
# 
# Author: Jason J. W. Williams
# (C)2011
###############################################

import pika, os, sys
from configparser import ConfigParser

# Read configuration from config file
config = ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), '..', 'chapter-4', 'config.ini'))

# Get environment from ENV or default to 'dev'
env = os.environ.get('RABBITMQ_ENV', 'dev')
if env not in config.sections():
    print(f"Error: Environment '{{env}}' not found in config.ini")
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
)
conn_broker = pika.BlockingConnection(conn_params)
'''

def fix_body_decode(content):
    """Fix body decode issues"""
    content = re.sub(r"body\.decode\(\\'utf-8\\'\)", r"body.decode('utf-8')", content)
    content = re.sub(r"if body == \"quit\"", r"body_str = body.decode('utf-8')\n    if body_str == \"quit\"", content)
    content = re.sub(r"print\(body\)", r"print(body_str)", content)
    return content

def fix_basic_consume(content):
    """Fix basic_consume calls"""
    # Fix various patterns
    content = re.sub(r'channel\.basic_consume\(\s*(\w+)\s*,\s*queue=', r'channel.basic_consume(queue=', content)
    content = re.sub(r'channel\.basic_consume\((\w+),\s*queue=', r'channel.basic_consume(queue=', content)
    content = re.sub(r'channel\.basic_consume\(\s*queue=', r'channel.basic_consume(queue=', content)
    
    # Add on_message_callback
    if 'on_message_callback=' not in content:
        # Find the consumer function name
        match = re.search(r'def\s+(\w+)\(ch,\s*method,\s*properties,\s*body\)', content)
        if match:
            func_name = match.group(1)
            content = re.sub(
                r'(channel\.basic_consume\(queue="[^"]+",)',
                r'\1\n                       on_message_callback=' + func_name + ',',
                content
            )
    return content

def fix_type_parameter(content):
    """Fix type parameter to exchange_type"""
    return re.sub(r'type="(\w+)"', r'exchange_type="\1"', content)

def fix_callback_signature(content):
    """Fix callback function signatures"""
    return re.sub(r'def\s+(\w+)\(channel,\s*method,\s*header,\s*body\)', r'def \1(ch, method, properties, body)', content)

def fix_print_statements(content):
    """Fix print statements"""
    # Fix simple print statements
    content = re.sub(r'^(\s*)print\s+([^(][^\n]*)$', r'\1print(\2)', content, flags=re.MULTILINE)
    return content

def process_file(filepath, template_type='guest'):
    """Process a single file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract title from original file
    title_match = re.search(r'#\s*(.+?)\s*#', content)
    title = title_match.group(1).strip() if title_match else "RabbitMQ Example"
    
    # Apply fixes
    content = fix_body_decode(content)
    content = fix_basic_consume(content)
    content = fix_type_parameter(content)
    content = fix_callback_signature(content)
    content = fix_print_statements(content)
    
    # Replace connection setup if needed
    if 'config.ini' not in content:
        if template_type == 'guest':
            template = CHAPTER_2_5_TEMPLATE.format(title=title)
        else:
            template = CHAPTER_6_7_TEMPLATE.format(title=title)
        
        # Replace the import and connection section
        content = re.sub(
            r'import pika.*?(conn_broker = pika\.BlockingConnection\(conn_params\))',
            template.strip(),
            content,
            flags=re.DOTALL
        )
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Processed: {filepath}")

if __name__ == "__main__":
    # Chapter 2 and 5 use guest
    for chapter in ['chapter-2', 'chapter-5']:
        chapter_dir = os.path.join('python', chapter)
        if os.path.exists(chapter_dir):
            for filename in os.listdir(chapter_dir):
                if filename.endswith('.py'):
                    filepath = os.path.join(chapter_dir, filename)
                    try:
                        process_file(filepath, 'guest')
                    except Exception as e:
                        print(f"Error processing {filepath}: {e}")
    
    # Chapter 6 and 7 use rpc_user
    for chapter in ['chapter-6', 'chapter-7']:
        chapter_dir = os.path.join('python', chapter)
        if os.path.exists(chapter_dir):
            for filename in os.listdir(chapter_dir):
                if filename.endswith('.py'):
                    filepath = os.path.join(chapter_dir, filename)
                    try:
                        process_file(filepath, 'rpc_user')
                    except Exception as e:
                        print(f"Error processing {filepath}: {e}")
