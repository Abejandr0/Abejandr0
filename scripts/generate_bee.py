#!/usr/bin/env python3
"""Create a GitHub-ready animated honey bee SVG using real contribution data.

Production: GH_TOKEN=... GH_USER=Abejandr0 python scripts/generate_bee.py
Preview only: python scripts/generate_bee.py --demo
"""
import argparse
from datetime import date, timedelta
import html
import json
import math
import os
from pathlib import Path
import random
import urllib.error
import urllib.request

W, H = 1140, 340
GRID_X, GRID_Y, STEP = 90, 114, 17
SQUARE = 12
DURATION = 30
OUT = Path(__file__).resolve().parents[1] / "assets" / "bee-contributions.svg"


def get_contributions(user, token):
    if not token:
        raise ValueError("Missing GH_TOKEN: use GitHub Actions, or --demo for a local preview.")
    query = '''query($login: String!) {
      user(login: $login) {
        contributionsCollection {
          contributionCalendar {
            totalContributions
            weeks { contributionDays { date contributionCount } }
          }
        }
      }
    }'''
    body = json.dumps({"query": query, "variables": {"login": user}}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql", body,
        {"Authorization": f"Bearer {token}", "Content-Type": "application/json",
         "Accept": "application/vnd.github+json", "User-Agent": "Abejandr0-honey-bee"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            payload = json.load(resp)
    except urllib.error.HTTPError as err:
        raise RuntimeError(f"GitHub API returned HTTP {err.code}: {err.read().decode()[:350]}") from err
    if payload.get("errors"):
        raise RuntimeError(f"GitHub GraphQL error: {payload['errors']}")
    user_data = payload.get("data", {}).get("user")
    if not user_data:
        raise RuntimeError(f"GitHub user not found: {user}")
    cal = user_data["contributionsCollection"]["contributionCalendar"]
    weeks = [w["contributionDays"] for w in cal["weeks"]]
    return weeks, cal["totalContributions"]


def make_demo():
    """For an offline illustrative image only: NOT real contribution data."""
    today = date.today()
    start = today - timedelta(days=370)
    start -= timedelta(days=(start.weekday() + 1) % 7)
    random.seed(21)
    weeks = []
    for col in range(53):
        days = []
        for row in range(7):
            day = start + timedelta(days=col * 7 + row)
            if day <= today:
                count = random.choices([0, 1, 2, 4, 8, 14], [42, 20, 15, 13, 8, 2])[0]
                days.append({"date": day.isoformat(), "contributionCount": count})
        weeks.append(days)
    return weeks, sum(x['contributionCount'] for w in weeks for x in w)


def render(weeks, total, user, demo=False):
    # Render exactly one square per provided contribution-day; original dates remain intact.
    cols = len(weeks)
    # Fit 53-54 columns within the canvas while preserving square spacing.
    stride = min(STEP, 950 / max(1, cols - 1))
    pieces = []
    add = pieces.append
    data_type = 'illustrative demo' if demo else 'real'
    add(f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Animated honey bee flying over {html.escape(user)}'s {data_type} GitHub contributions">''')
    add('''<defs>
      <linearGradient id="bg" x1="0" x2="1" y1="0" y2="1"><stop stop-color="#11141A"/><stop offset="1" stop-color="#1A1710"/></linearGradient>
      <linearGradient id="honey" x1="0" x2="1"><stop stop-color="#FCA311"/><stop offset="1" stop-color="#FFE26A"/></linearGradient>
      <filter id="light"><feGaussianBlur stdDeviation="3" /></filter>
      <pattern id="dots" width="25" height="25" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="0.6" fill="#D19E32" opacity=".13"/></pattern>
    </defs>''')
    add('<rect x="1" y="1" width="1138" height="338" rx="22" fill="url(#bg)" stroke="#50401C" stroke-width="2"/>')
    add('<rect x="2" y="2" width="1136" height="336" rx="21" fill="url(#dots)"/>')
    add(f'''<g font-family="ui-monospace, SFMono-Regular, Consolas, monospace">
      <text x="40" y="52" fill="#FFE29B" font-weight="bold" font-size="25" letter-spacing="2">THE HONEY TRAIL</text>
      <text x="40" y="74" fill="#958B71" font-size="12">a little bee collecting my commits</text>
      <rect x="923" y="28" width="178" height="30" rx="15" fill="#302718" stroke="#5A481E"/>
      <circle cx="944" cy="43" r="5" fill="#FFC64D"/>
      <text x="958" y="47" font-size="12" fill="#FCD36A">{total:,} contributions</text>
    </g>''')
    # Date-aware month captions, anchored on first week of each new month.
    last_month = None
    for col, week in enumerate(weeks):
        if not week:
            continue
        d = date.fromisoformat(week[0]['date'])
        if d.month != last_month:
            if col > 0:
                x = GRID_X + col * stride
                if x <= 1008:
                    add(f'<text x="{x:.1f}" y="100" font-family="monospace" font-size="10" fill="#807762">{d.strftime("%b").upper()}</text>')
            last_month = d.month
    colors = ('#2C2B26', '#665019', '#A98021', '#E6B532', '#FFE061')
    active = []
    for col, week in enumerate(weeks):
        for day in week:
            d = date.fromisoformat(day['date'])
            row = (d.weekday() + 1) % 7
            count = int(day['contributionCount'])
            idx = 0 if count == 0 else 1 if count <= 1 else 2 if count <= 3 else 3 if count <= 7 else 4
            x = GRID_X + col * stride
            y = GRID_Y + row * STEP
            add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{SQUARE}" height="{SQUARE}" rx="3" fill="{colors[idx]}"><title>{html.escape(day["date"])}: {count} contributions</title></rect>')
            if count:
                active.append((x + SQUARE/2, y + SQUARE/2, count))
    # Sparkle around the calendar without implying extra contribution days.
    for i in range(12):
        x = 96 + ((i * 89) % 902)
        y = 115 + ((i * 47) % 114)
        add(f'<circle cx="{x}" cy="{y}" r="1" fill="#EFC951" opacity=".28"><animate attributeName="opacity" values=".08;.5;.08" dur="{2.5+(i%3)}s" begin="{i*.3}s" repeatCount="indefinite"/></circle>')
    # Fly through up to 35 actual active days. Fallback to a tour of the empty grid.
    if active:
        stride_active = max(1, len(active)//32)
        route = active[::stride_active][:36]
    else:
        route = [(GRID_X+20, GRID_Y+60, 0), (GRID_X+430, GRID_Y+15, 0),
                 (GRID_X+920, GRID_Y+68, 0), (GRID_X+490, GRID_Y+110, 0)]
    # Moving path closes seamlessly and uses the real calendar's active-day coordinates.
    pts = [(x, y - 18) for x, y, _ in route]
    anchor_x, anchor_y = pts[0]
    # Pulse a tiny honey glow whenever the bee reaches a real contribution cell.
    hops = [math.hypot(pts[i][0]-pts[i-1][0], pts[i][1]-pts[i-1][1]) for i in range(1, len(pts))]
    total_distance = sum(hops) + math.hypot(pts[-1][0]-anchor_x, pts[-1][1]-anchor_y)
    covered = 0.0
    for index, (cx, cy) in enumerate(pts):
        if index:
            covered += hops[index-1]
        fraction = covered / total_distance if total_distance else 0
        if fraction > .96:
            continue
        at = max(.0001, fraction)
        bright = min(.999, at + .001)
        faded = min(.9999, at + .032)
        add(f'<circle cx="{cx:.1f}" cy="{cy+18:.1f}" r="8" fill="#FFE075" opacity="0"><animate attributeName="opacity" values="0;0;0.85;0;0" keyTimes="0;{at:.4f};{bright:.4f};{faded:.4f};1" dur="{DURATION}s" repeatCount="indefinite"/></circle>')
    d_string = 'M 0 0 L ' + ' L '.join(f'{x-anchor_x:.1f} {y-anchor_y:.1f}' for x, y in pts[1:]) + ' L 0 0'
    add(f'<g transform="translate({anchor_x:.1f} {anchor_y:.1f})"><g opacity=".75"><circle r="13" fill="#F0B42D" opacity=".28" filter="url(#light)"><animateMotion dur="{DURATION}s" repeatCount="indefinite" path="{d_string}"/></circle></g></g>')
    # Bee: SVG vector (animated wings and body), not a pre-rendered gif.
    add(f'<g transform="translate({anchor_x:.1f} {anchor_y:.1f})"><g><animateMotion dur="{DURATION}s" repeatCount="indefinite" path="{d_string}"/>')
    add('''<g><animateTransform attributeName="transform" type="translate" values="0 -2;0 2;0 -2" dur="0.55s" repeatCount="indefinite"/>
      <g transform="translate(-4 -7)"><ellipse cx="-6" cy="-9" rx="10" ry="6" fill="#C3EAFF" opacity=".88" transform="rotate(-27 -6 -9)"><animateTransform attributeName="transform" type="rotate" values="-27 -6 -9;8 -6 -9;-27 -6 -9" dur="0.25s" repeatCount="indefinite"/></ellipse>
      <ellipse cx="5" cy="-10" rx="10" ry="6" fill="#DDF8FF" opacity=".88" transform="rotate(30 5 -10)"><animateTransform attributeName="transform" type="rotate" values="30 5 -10;-10 5 -10;30 5 -10" dur="0.22s" repeatCount="indefinite"/></ellipse>
      <ellipse cx="0" cy="0" rx="17" ry="12" fill="url(#honey)" stroke="#161616" stroke-width="2"/>
      <path d="M -8 -10 Q -1 0 -8 10 M 3 -11 Q 11 0 3 11" fill="none" stroke="#211C17" stroke-width="6" />
      <ellipse cx="12" cy="-2" rx="8.5" ry="9" fill="#FFD14B" stroke="#161616" stroke-width="1.5"/>
      <circle cx="15.5" cy="-4" r="2.5" fill="#1B1714"/><circle cx="16.2" cy="-4.6" r="0.8" fill="white"/>
      <path d="M 13 3 q 3 3 6 -1" fill="none" stroke="#402C17" stroke-width="1.3" stroke-linecap="round"/>
      <path d="M 13 -10 q 0 -6 4 -8" stroke="#201C16" stroke-width="1.4" fill="none" stroke-linecap="round"/><circle cx="17" cy="-18" r="1.8" fill="#EFC451"/>
      <path d="M -16 1 l -6 3 l 7 4" fill="#E1AC35" stroke="#201C16" stroke-width="1.3"/>
      </g></g></g></g>''')
    add('''<g font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="11">
      <text x="40" y="307" fill="#968C73">LESS</text>''')
    for i,c in enumerate(colors):
        add(f'<rect x="{82+i*18}" y="297" width="11" height="11" rx="2" fill="{c}"/>')
    add('''<text x="183" y="307" fill="#968C73">MORE</text>
      <text x="1084" y="307" text-anchor="end" fill="#B69B53">BUZZING THROUGH CODE</text>
    </g>''')
    if demo:
        add('''<text x="568" y="327" text-anchor="middle" font-family="monospace" font-size="10" fill="#C2A06C">DEMO DATA · REPLACED WITH REAL GITHUB ACTIVITY AFTER WORKFLOW RUN</text>''')
    add('</svg>')
    return '\n'.join(pieces)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--demo', action='store_true', help='Build preview with illustrative data; never use as actual stats')
    args = parser.parse_args()
    user = os.environ.get('GH_USER', 'Abejandr0')
    if args.demo:
        weeks, total = make_demo()
    else:
        weeks, total = get_contributions(user, os.environ.get('GH_TOKEN'))
    OUT.parent.mkdir(exist_ok=True, parents=True)
    OUT.write_text(render(weeks, total, user, demo=args.demo), encoding='utf-8')
    print(f'Created {OUT} ({total} contributions; {len(weeks)} weeks; demo={args.demo})')

if __name__ == '__main__':
    main()
