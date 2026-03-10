import os
import glob

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    if 'from unfold.admin import' in content:
        return

    new_content = content.replace('admin.ModelAdmin', 'ModelAdmin')
    new_content = new_content.replace('admin.TabularInline', 'TabularInline')
    new_content = new_content.replace('admin.StackedInline', 'StackedInline')

    # Find the imports section to add the unfold imports safely
    lines = new_content.split('\n')
    import_idx = 0
    for i, line in enumerate(lines):
        if line.startswith('from django.contrib import admin'):
            import_idx = i + 1
            break
            
    lines.insert(import_idx, 'from unfold.admin import ModelAdmin, TabularInline, StackedInline')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

for admin_file in glob.glob('hutech_program/**/admin.py', recursive=True):
    process_file(admin_file)
    print(f"Updated {admin_file}")

