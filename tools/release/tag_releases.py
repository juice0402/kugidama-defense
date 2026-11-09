"""Make a tag and a GitHub Release for each version in RELEASES.md that has no tag yet.

Run by .github/workflows/release.yml on every push to main (司令塔の決まり 11/5。juice0402/path-quest から写した 11/9).
- a version is a heading "## v1.1・2026-11-20"; the lines under it (up to the next heading) are what changed
- the tag goes on the pushed commit (GITHUB_SHA), or on the commit written as "（3c569c3）" in that version's lines
- oldest first, so the newest release ends up as the latest one
- DRY=1 only prints what it would do (for a check on your own machine)
"""
import os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FILE = os.path.join(ROOT, 'RELEASES.md')
DRY = os.environ.get('DRY') == '1'
HEAD = re.compile(r'^##\s+(v\d+(?:\.\d+)*)\s*・\s*(\d{4}-\d{2}-\d{2})\s*$')
PIN = re.compile(r'（([0-9a-f]{7,40})）')


def git(*a, check=True):
    r = subprocess.run(['git', *a], cwd=ROOT, capture_output=True, text=True)
    if check and r.returncode:
        sys.exit(f'git {" ".join(a)}: {r.stderr.strip()}')
    return r.stdout.strip()


def versions():
    out, cur = [], None
    for line in open(FILE, encoding='utf-8'):
        line = line.rstrip('\n')
        m = HEAD.match(line)
        if m:
            cur = {'v': m.group(1), 'date': m.group(2), 'lines': []}
            out.append(cur)
        elif line.startswith('#'):
            cur = None
        elif cur is not None and line.strip():
            cur['lines'].append(line.strip())
    return out


def main():
    have = set(git('tag', '-l').split())
    todo = [x for x in reversed(versions()) if x['v'] not in have]
    if not todo:
        print('新しい版はない')
        return
    head = os.environ.get('GITHUB_SHA') or git('rev-parse', 'HEAD')
    for x in todo:
        body = '\n'.join(x['lines'])
        pin = PIN.search(body)
        target = git('rev-parse', '--verify', pin.group(1) + '^{commit}') if pin else head
        notes = PIN.sub('', body).strip() or '（変えたことの記録なし）'
        title = f"パチおば {x['v']}"
        print(f"{x['v']} → {target[:7]}\n{notes}")
        if DRY:
            continue
        git('-c', 'user.name=github-actions[bot]', '-c', 'user.email=41898282+github-actions[bot]@users.noreply.github.com',
            'tag', '-a', x['v'], target, '-m', f"{title}（{x['date']}）\n\n{notes}")
        git('push', 'origin', 'refs/tags/' + x['v'])
        r = subprocess.run(['gh', 'release', 'create', x['v'], '--verify-tag', '--title', f"{title}（{x['date']}）", '--notes', notes],
                           cwd=ROOT, capture_output=True, text=True)
        print(r.stdout.strip() or r.stderr.strip())
        if r.returncode:
            sys.exit(f"{x['v']}: Releases を作れなかった（タグはできた）")


if __name__ == '__main__':
    main()
