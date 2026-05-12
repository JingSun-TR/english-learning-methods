#!/usr/bin/env python3
"""Static site builder for English Learning Methods."""

import json
import os
import shutil
import re
from pathlib import Path
from datetime import datetime

try:
    from jinja2 import Environment, FileSystemLoader
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'jinja2'])
    from jinja2 import Environment, FileSystemLoader

BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / 'templates'
DATA_DIR = BASE_DIR / 'data'
OUTPUT_DIR = BASE_DIR / 'output'
STATIC_DIR = BASE_DIR / 'static'

# Skill name mapping
SKILL_MAP = {
    'listening': '听力', 'speaking': '口语', 'reading': '阅读',
    'writing': '写作', 'vocabulary': '词汇', 'pronunciation': '发音'
}

def load_data():
    with open(DATA_DIR / 'methods.json', 'r') as f:
        return json.load(f)

def markdown_to_html(text):
    """Simple markdown to HTML converter for method descriptions."""
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # Links
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    # Line breaks to paragraphs
    paragraphs = text.split('\n')
    result = []
    for p in paragraphs:
        p = p.strip()
        if p:
            result.append(f'<p>{p}</p>')
    return '\n'.join(result)

def build():
    data = load_data()
    
    # Setup Jinja2
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    env.globals['now'] = datetime.now()
    env.globals['SKILL_MAP'] = SKILL_MAP
    
    # Clean output
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True)
    
    # Copy static files
    output_static = OUTPUT_DIR / 'static'
    if STATIC_DIR.exists():
        shutil.copytree(STATIC_DIR, output_static)
    
    # Build index page
    index_template = env.get_template('index.html')
    index_html = index_template.render(
        page='index',
        site=data,
        methods=data['methods'],
        categories=data['categories'],
        quick_guide=data['quick_guide']
    )
    with open(OUTPUT_DIR / 'index.html', 'w') as f:
        f.write(index_html)
    
    # Build individual method pages
    method_template = env.get_template('method.html')
    methods_dir = OUTPUT_DIR / 'methods'
    methods_dir.mkdir(exist_ok=True)
    
    for method in data['methods']:
        method_html = method_template.render(
            page='method',
            site=data,
            method=method,
            all_methods=data['methods']
        )
        with open(methods_dir / f"{method['id']}.html", 'w') as f:
            f.write(method_html)
    
    # Build by-skill pages
    for skill_en, skill_zh in SKILL_MAP.items():
        skill_methods = [m for m in data['methods'] if skill_zh in m.get('best_for', [])]
        if skill_methods:
            skill_html = index_template.render(
                page='skill',
                site=data,
                methods=skill_methods,
                categories=data['categories'],
                quick_guide=data['quick_guide'],
                filter_title=f'{skill_zh}训练方法',
                filter_desc=f'专注于提升{skill_zh}能力的学习方法'
            )
            with open(OUTPUT_DIR / f'{skill_en}.html', 'w') as f:
                f.write(skill_html)
    
    # Copy index.html as 404.html (for SPA-like behavior)
    shutil.copy(OUTPUT_DIR / 'index.html', OUTPUT_DIR / '404.html')
    
    print(f"✓ Built {len(data['methods'])} method pages")
    print(f"✓ Built {len(SKILL_MAP)} skill pages")
    print(f"✓ Site ready at {OUTPUT_DIR}")

if __name__ == '__main__':
    build()
