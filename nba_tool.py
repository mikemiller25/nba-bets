import requests
import pandas as pd

ESPN_TEAMS_URL = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams"

def parse_score(score_val):
    """Safely extract score as an integer whether ESPN returns int, str, or dict."""
    if isinstance(score_val, dict):
        val = score_val.get('value') or score_val.get('displayValue') or 0
        return int(float(val))
    elif score_val is not None:
        return int(float(score_val))
    return 0

def fetch_espn_team_l5_metrics(team_name: str):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        # Step 1: Find the team ID from ESPN's team directory
        resp = requests.get(ESPN_TEAMS_URL, headers=headers, timeout=10)
        if resp.status_code != 200:
            print(f"Error fetching team list: Status {resp.status_code}")
            return None
            
        teams_data = resp.json()['sports'][0]['leagues'][0]['teams']
        team_id = None
        for t in teams_data:
            team_info = t['team']
            if team_name.lower() in team_info['displayName'].lower() or team_name.lower() in team_info['name'].lower():
                team_id = team_info['id']
                break
                
        if not team_id:
            print(f"Team '{team_name}' not found.")
            return None

        # Step 2: Fetch team's schedule and past game scores from ESPN
        sched_url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams/{team_id}/schedule"
        sched_resp = requests.get(sched_url, headers=headers, timeout=10)
        if sched_resp.status_code != 200:
            print(f"Error fetching schedule for {team_name}: Status {sched_resp.status_code}")
            return None

        events = sched_resp.json().get('events', [])
        completed_games = []

        for e in events:
            competitions = e.get('competitions', [])
            if not competitions:
                continue
            competition = competitions[0]
            
            if competition.get('status', {}).get('type', {}).get('completed', False):
                competitors = competition.get('competitors', [])
                pts = 0
                opp_pts = 0
                is_winner = False
                
                for team in competitors:
                    if str(team.get('id')) == str(team_id):
                        pts = parse_score(team.get('score'))
                        is_winner = team.get('winner', False)
                    else:
                        opp_pts = parse_score(team.get('score'))
                
                diff = pts - opp_pts
                completed_games.append({
                    'PTS': pts,
                    'OPP_PTS': opp_pts,
                    'DIFF': diff,
                    'WIN': 1 if is_winner else 0
                })

        if not completed_games:
            print(f"No completed games found for {team_name}.")
            return None

        # Step 3: Compute rolling L5 metrics
        df = pd.DataFrame(completed_games).tail(5)
        
        return {
            "Team": team_name,
            "L5 PPG": round(df['PTS'].mean(), 1),
            "L5 Opp PPG": round(df['OPP_PTS'].mean(), 1),
            "L5 Diff": round(df['DIFF'].mean(), 1),
            "L5 Win Rate": f"{(df['WIN'].mean() * 100):.0f}%"
        }

    except Exception as e:
        print(f"Error fetching metrics for {team_name}: {e}")
        return None

if __name__ == "__main__":
    print("=== NBA BETTING INTELLIGENCE TOOL (ESPN DATA ENGINE) ===")
    teams_to_check = ["Boston Celtics", "Miami Heat"]
    
    results = []
    for team in teams_to_check:
        res = fetch_espn_team_l5_metrics(team)
        if res:
            results.append(res)
            
    if results:
        print("\n", pd.DataFrame(results).to_string(index=False))
    else:
        print("\nNo team metrics retrieved.")
