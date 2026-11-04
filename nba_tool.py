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
        
        # Extract odds if available from ESPN payload
        consensus_spread = "Spread TBD"
        implied_total = "N/A"
        if 'odds' in competition and len(competition['odds']) > 0:
            odds_data = competition['odds'][0]
            consensus_spread = odds_data.get('details', 'Spread TBD')
            implied_total = str(odds_data.get('overUnder', 'N/A'))
        
        # Dynamic sample player props structure (ready for regular season box scores)
        sample_players = [
            {
                "name": "Featured Star",
                "position": "G-F",
                "prop": "Points",
                "line": 24.5,
                "l5_avg": 26.8,
                "hit_rate": "80% L5",
                "vs_opponent_home": "27.2 PTS (L3 Home)",
                "vs_opponent_away": "25.0 PTS (L3 Away)"
            }
        ]
        
        matchup = {
            "id": event['id'],
            "time": event['status']['type']['detail'],
            "home": home_team['team']['displayName'],
            "away": away_team['team']['displayName'],
            "home_record": home_team.get('records', [{'summary': '0-0'}])[0]['summary'],
            "away_record": away_team.get('records', [{'summary': '0-0'}])[0]['summary'],
            "home_metrics": { "l5_ppg": 112.0, "l5_opp_ppg": 106.5, "l5_diff": 5.5, "l5_win_rate": "75%" },
            "away_metrics": { "l5_ppg": 109.2, "l5_opp_ppg": 110.1, "l5_diff": -0.9, "l5_win_rate": "45%" },
            "consensus_spread": consensus_spread,
            "implied_total": implied_total,
            "model_edge": "Active Edge Scan",
            "players": sample_players
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
