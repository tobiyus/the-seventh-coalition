#!/usr/bin/env python3
"""Update the leaderboard page from a saved copy of the armory guild page.

usage: refresh.py <leaderboard.html> <guild.html> [YYYY-MM-DD]
Rewrites the JSON inside <script id="guild-data"> in the leaderboard page.
"""
import sys, re, json, html, datetime

KEEP_DAYS = 45

def parse_guild(src):
    members = []
    for block in re.findall(r'<a class="member"[^>]*href="([^"]+)">(.*?)</a>', src, re.S):
        href, body = block
        def cell(cls):
            m = re.search(r'class="%s"[^>]*>(.*?)</span>' % cls, body, re.S)
            return html.unescape(re.sub(r'<[^>]+>', '', m.group(1))).strip() if m else ''
        name, lvl = cell('c-name'), cell('c-level')
        if not name or not lvl.isdigit():
            continue
        gs = cell('c-gs')
        members.append({'n': name, 'l': int(lvl), 'r': cell('c-race'), 'c': cell('c-class'),
                        'k': cell('c-rank'), 'g': int(gs) if gs.isdigit() else 0,
                        'u': href.rsplit('/', 1)[-1]})
    return members

def main():
    page_path, guild_path = sys.argv[1], sys.argv[2]
    today = sys.argv[3] if len(sys.argv) > 3 else datetime.datetime.utcnow().strftime('%Y-%m-%d')
    members = parse_guild(open(guild_path, encoding='utf-8').read())
    if len(members) < 5:
        sys.exit('refusing to update: only %d members parsed from the guild page' % len(members))
    page = open(page_path, encoding='utf-8').read()
    m = re.search(r'(<script id="guild-data" type="application/json">)(.*?)(</script>)', page, re.S)
    if not m:
        sys.exit('guild-data block not found in page')
    try:
        old = json.loads(m.group(2))
    except Exception:
        old = {}
    hist = old.get('hist', {})
    hist[today] = {x['n']: x['l'] for x in members}
    cutoff = (datetime.date.fromisoformat(today) - datetime.timedelta(days=KEEP_DAYS)).isoformat()
    hist = {d: v for d, v in sorted(hist.items()) if d >= cutoff}
    # remember the first day each member was seen at 60
    dinged = old.get('dinged', {})
    for x in members:
        if x['l'] >= 60 and x['n'] not in dinged:
            dinged[x['n']] = {'d': today, 'r': x['r'], 'c': x['c']}
    data = {'guild': 'The Seventh Coalition', 'region': 'EU', 'realm': 'Normal',
            'source': 'https://armorywowforever.com/g/forever/eu/normal/the-seventh-coalition',
            'updated': today, 'members': members, 'hist': hist, 'dinged': dinged}
    blob = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c')
    page = page[:m.start(2)] + blob + page[m.end(2):]
    open(page_path, 'w', encoding='utf-8').write(page)
    top = max(members, key=lambda x: x['l'])
    print('updated %s: %d members, top %s (%d), snapshots kept: %d' % (today, len(members), top['n'], top['l'], len(hist)))

main()
