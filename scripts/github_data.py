# get and store the info from `gh status`
# make clickable links to save user time 
import subprocess
import re
import yaml
from pathlib import Path

# Path to the YAML file
YAML_PATH = Path(__file__).parent.parent / 'user_data' / 'github_data.yml'

def run_gh_status():
    """Run `gh status` and return its output as a string."""
    result = subprocess.run(['gh', 'status'], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"gh status failed: {result.stderr}")
    return result.stdout

def parse_table_line(line):
    # Split by the vertical bar, handle lines with one or two columns
    parts = line.split('│')
    left = parts[0].strip() if len(parts) > 0 else ''
    right = parts[1].strip() if len(parts) > 1 else ''
    return left, right

def parse_issue_or_pr(text):
    # Example: CruGlobal/appbuilder_platform_pwa#46  As a user I can create an expense report
    m = re.match(r'([^#]+)#(\d+)\s+(.*)', text)
    if m:
        repo, num, title = m.groups()
        url = f"https://github.com/{repo.strip()}/issues/{num}"
        return num, f"{title} [{url}]"
    return None, None

def parse_pr(text):
    # Example: CruGlobal/appbuilder_docs#15  [WIP] update theme and build
    m = re.match(r'([^#]+)#(\d+)\s+(.*)', text)
    if m:
        repo, num, title = m.groups()
        url = f"https://github.com/{repo.strip()}/pull/{num}"
        return num, f"{title} [{url}]"
    return None, None

def parse_gh_status_table(output):
    data = {
        'account name': None,
        'my_issues': {},
        'my_prs': {},
        'my_reviews': {},
    }
    lines = output.splitlines()
    section = None
    for line in lines:
        if 'Assigned Issues' in line and 'Assigned Pull Requests' in line:
            section = 'issues_prs'
            continue
        if 'Review Requests' in line and 'Mentions' in line:
            section = 'reviews_mentions'
            continue
        if 'Repository Activity' in line:
            section = None
            continue
        if section == 'issues_prs':
            left, right = parse_table_line(line)
            # Issues (left column)
            if left and not left.startswith('Nothing here'):
                num, val = parse_issue_or_pr(left)
                if num:
                    data['my_issues'][num] = val
            # PRs (right column)
            if right and not right.startswith('Nothing here'):
                num, val = parse_pr(right)
                if num:
                    data['my_prs'][num] = val
        elif section == 'reviews_mentions':
            left, right = parse_table_line(line)
            # Reviews (left column)
            if left and not left.startswith('Nothing here'):
                num, val = parse_pr(left)
                if num:
                    data['my_reviews'][num] = val
    return data

def write_yaml(data):
    with open(YAML_PATH, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True)

def main():
    output = run_gh_status()
    data = parse_gh_status_table(output)
    write_yaml(data)
    print(f"Updated {YAML_PATH}")

if __name__ == '__main__':
    main() 