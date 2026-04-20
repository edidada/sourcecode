#!/usr/bin/env python3
"""Fix Python 2 code to Python 3 compatible"""

import os
import re

def fix_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    original = content
    
    # Fix print statements
    content = re.sub(r'print\s+([^\n]+)', r'print(\1)', content)
    
    # Fix except syntax
    content = re.sub(r'except\s+(\w+),\s*(\w+):', r'except \1 as \2:', content)
    
    # Fix exchange_declare type parameter
    content = re.sub(r'type="(\w+)"', r'exchange_type="\1"', content)
    
    # Fix basic_consume callback signature
    content = re.sub(r'def\s+(\w+)\(channel,\s*method,\s*header,\s*body\)', r'def \1(ch, method, properties, body)', content)
    
    # Fix basic_consume call
    content = re.sub(r'channel\.basic_consume\(\s*(\w+),\s*queue=', r'channel.basic_consume(queue=', content)
    content = re.sub(r'channel\.basic_consume\((\w+),', r'channel.basic_consume(on_message_callback=\1,', content)
    
    # Fix queue_declare with exclusive
    content = re.sub(r'queue_declare\(exclusive=True', r"queue_declare(queue='', exclusive=True", content)
    
    if content != original:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Fixed: {filepath}")
    else:
        print(f"No changes: {filepath}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        for filepath in sys.argv[1:]:
            if os.path.exists(filepath):
                fix_file(filepath)
            else:
                print(f"File not found: {filepath}")
    else:
        print("Usage: python fix_py2_to_py3.py <file1> <file2> ...")
