import pandas as pd
from nba_api.stats.static import teams
from nba_api.stats.endpoints import teamgamelog

def get_team_id(team_name: str):
    for t in teams.get_teams():
        if team_name.lower() in t['full_name'].lower() or team_name.lower() in t['nickname'].lower():
            return t['id']
    return None

def fetch_team_rolling_metrics(team_name: str):
    team_id = get_team_id(team_name)
    if not team_id:
        return None
    try:
        gamelog = teamgamelog.TeamGameLog(team_id=team_id, season="2025-26")
        df = gamelog.get_data_frames()[0].head(5)
        
        # Calculate point differential per game
        if 'PLUS_MINUS' in df.columns:
            df['DIFF'] = df['PLUS_MINUS']
        elif 'PTS' in df.columns and 'PTS_ALLOWED' in df.columns:
            df['DIFF'] = df['PTS'] - df['PTS_ALLOWED']
        else:
            df['DIFF'] = 0

        return {
            "Team": team_name,
            "L5 PPG": round(df['PTS'].mean(), 1),
            "L5 Diff": round(df['DIFF'].mean(), 1),
            "L5 Win Rate": f"{(df['WL'] == 'W').mean() * 100:.0f}%"
        }
    except Exception as e:
        print(f"Error fetching metrics for {team_name}: {e}")
        return None

if __name__ == "__main__":
    print("=== NBA BETTING INTELLIGENCE TOOL ===")
    teams_to_check = ["Boston Celtics", "Miami Heat"]
    team_comparison = [fetch_team_rolling_metrics(t) for t in teams_to_check]
    print(pd.DataFrame([t for t in team_comparison if t]).to_string(index=False))