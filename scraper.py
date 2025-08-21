import requests
import re
import json
from datetime import datetime

URL = "https://www.psdevwiki.com/ps3/index.php?title=PSP_HD_%26_Minis_Emulator_Compatibility_List&action=raw"

PLAYABILITY_TAGS = {
    # "{{pspclassic}}": "PSP Remaster", # not designated on table
    "{{playable}}": "Playable",
    "{{minorissues}}": "Minor Issues",
    "{{majorissues}}": "Major Issues",
    "{{unplayable}}": "Unplayable",
}

def fetch_page():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/plain',
    }
    resp = requests.get(URL, headers=headers)
    resp.raise_for_status()
    return resp.text

def parse_stats(html):
    stats = {name: 0 for name in PLAYABILITY_TAGS.values()}
    stats["Untested"] = 0
    untested_games = []

    rows = html.split("|-")
    for row in rows:
        cols = [c.strip() for c in row.replace("\n", "").split("||")]
        if len(cols) < 2:
            continue

        game_name = cols[0].lstrip("|").strip()
        if not game_name or game_name.lower().startswith("title"):
            continue

        compatibility_info = " ".join(cols[1:4])
        
        # leaving the code in in case the table is updated to include PSP Remasters
        #if "{{pspclassic}}" in compatibility_info:
        #    stats["PSP Remaster"] += 1
        #    continue
            
        worst_status = None
        severity_order = ["Unplayable", "Major Issues", "Minor Issues", "Playable"]
        status_values = {status: i for i, status in enumerate(severity_order)}
        
        for marker, label in PLAYABILITY_TAGS.items():
            #if label == "PSP Remaster":
            #    continue
            if marker in compatibility_info:
                if worst_status is None or status_values[label] < status_values[worst_status]:
                    worst_status = label
        
        if worst_status:
            stats[worst_status] += 1
        else:
            stats["Untested"] += 1
            untested_games.append(game_name)

    return stats, untested_games

def main():
    html = fetch_page()
    stats, untested_games = parse_stats(html)

    data = {
        "stats": stats,
        "last_updated": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    }

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    with open("untested.json", "w", encoding="utf-8") as f:
        json.dump(untested_games, f, indent=2, ensure_ascii=False)

    print("Wrote data.json and untested.json")
    print("Summary:", stats)

if __name__ == "__main__":
    main()