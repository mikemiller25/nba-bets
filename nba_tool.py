import json
from datetime import datetime
import requests

def fetch_live_nba_slate():
    # Fetch today's scoreboard from the public ESPN API endpoint
    today_str = datetime.utcnow().strftime('%Y%m%d')
    url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates={today_str}"
    
    response = requests.get(url)
    data = response.json()
    
    slate = []
    events = data.get('events', [])
    
    for event in events:
        competition = event['competitions'][0]
        teams = competition['competitors']
        
        home_team = next(t for t in teams if t['homeAway'] == 'home')
        away_team = next(t for t in teams if t['homeAway'] == 'away')
        
        matchup = {
            "id": event['id'],
            "time": event['status']['type']['detail'],
            "home": home_team['team']['displayName'],
            "away": away_team['team']['displayName'],
            "home_record": home_team.get('records', [{'summary': '0-0'}])[0]['summary'],
            "away_record": away_team.get('records', [{'summary': '0-0'}])[0]['summary'],
            "home_metrics": { "l5_ppg": 110.0, "l5_opp_ppg": 108.0, "l5_diff": 2.0, "l5_win_rate": "60%" },
            "away_metrics": { "l5_ppg": 108.0, "l5_opp_ppg": 109.0, "l5_diff": -1.0, "l5_win_rate": "40%" },
            "consensus_spread": "Spread TBD",
            "implied_total": "220.5",
            "model_edge": "Active Edge Scan",
            "players": []
        }
        slate.append(matchup)

    output = {
        "last_updated": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'),
        "slate": slate
    }
    
    with open('data.json', 'w') as f:
        json.dump(output, f, indent=4)

if __name__ == "__main__":
    fetch_live_nba_slate()
