# semantic_model.py

class PlayerQuery:
    def __init__(self, position=None, team=None, stat=None, timeframe=None):
        self.position = position
        self.team = team
        self.stat = stat
        self.timeframe = timeframe

    def to_api_params(self):
        return {
            "pos": self.position,
            "team": self.team,
            "metric": self.stat,
            "range": self.timeframe,
        }

    def describe(self):
        return f"🔍 Querying {self.position or 'all players'} for {self.stat} over {self.timeframe or 'season'}"
