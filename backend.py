import pandas as pd
import streamlit as st
import altair as alt

def get_unique_players(df):
    bowlers = df['bowler'].dropna().unique()
    batsmen = df['batter'].dropna().unique()
    fielders = df['fielder'].dropna().unique()
    players = set(bowlers).union(set(batsmen), set(fielders))
    return tuple(players)

class HeadToHeadBowling:
    def __init__(self, dataframe):
        self.dataframe = dataframe
        self.num_matches = self.dataframe['match_id'].nunique()
        self.total_balls = len(self.dataframe[self.dataframe['extras_type'] != "wides"])
        self.non_bowler_dismissals = ['run out', 'retired hurt', 'hit wicket', 'obstructing the field', 'retired out']
        self.dataframe.reset_index(drop=True, inplace=True)

class BowlerAttributes(HeadToHeadBowling):
    def __init__(self, dataframe):
        super().__init__(dataframe)

    def get_wickets(self):
        non_bowler_wickets = len(self.dataframe[self.dataframe['dismissal_kind'].isin(self.non_bowler_dismissals)])
        total_wickets = len(self.dataframe[self.dataframe['is_wicket'] == 1])
        return total_wickets - non_bowler_wickets

    def get_run_rate(self):
        num_overs = self.total_balls / 6
        return round(self.dataframe['batsman_runs'].sum() / num_overs,2) if num_overs > 0 else 0

    def get_avg_balls_per_wicket(self):
        non_bowler_indices = self.dataframe[self.dataframe['dismissal_kind'].isin(self.non_bowler_dismissals)].index
        total_wicket_indices = self.dataframe[self.dataframe['is_wicket'] == 1].index
        wicket_indices = total_wicket_indices.difference(non_bowler_indices)


        balls_between_wickets = wicket_indices.to_series().diff().dropna()
        return f"{balls_between_wickets.mean():.0f}"



    def get_bowled_wickets(self):
        return len(self.dataframe[self.dataframe['dismissal_kind'] == "bowled"])

    def get_caught_wickets(self):
        return len(self.dataframe[self.dataframe['dismissal_kind'] == "caught"])

    def get_stumped_wickets(self):
        return len(self.dataframe[self.dataframe['dismissal_kind'] == "stumped"])

    def bowling_attributes(self):
        # self.get_wickets(),self.get_run_rate():.2f
        # self.get_avg_balls_per_wicket()
        # self.get_bowled_wickets()
        # self.get_caught_wickets()
        # self.get_stumped_wickets()

        data = pd.DataFrame(
            {
            "attributes": ["Total wickets","Avg runs per over","Avg Balls per wicket","Bowled wickets","Caught wickets","Stumped wickets"],
             "score": [self.get_wickets(),self.get_run_rate(),self.get_avg_balls_per_wicket(),self.get_bowled_wickets(),self.get_caught_wickets(),self.get_stumped_wickets()]
            }
        )

        return data

        # return f"""
        # Total wickets: {self.get_wickets()} \n
        # Average runs per over: {self.get_run_rate():.2f} \n
        # Average Balls per wicket: {self.get_avg_balls_per_wicket()} \n
        # Bowled wickets: {self.get_bowled_wickets()} \n
        # Caught wickets: {self.get_caught_wickets()} \n
        # Stumped wickets: {self.get_stumped_wickets()}"""

class BatsmanAttributes(HeadToHeadBowling):
    def __init__(self, dataframe):
        super().__init__(dataframe)
        self.total_runs = self.dataframe['batsman_runs'].sum()
        self.strike_rate = round(self.total_runs / self.total_balls * 100,2) if self.total_balls > 0 else 0
        self.extra_runs = self.dataframe['total_runs'].sum() - self.total_runs


    def batting_avg(self):
        wic = self.dataframe['is_wicket'].sum()
        if wic > 0:
            batting_avg = self.total_runs/wic
        else:
            batting_avg = 0
        return round(batting_avg,2)


    def get_singles(self):
        return len(self.dataframe[self.dataframe['batsman_runs'] == 1])

    def get_doubles(self):
        return len(self.dataframe[self.dataframe['batsman_runs'] == 2])

    def get_triples(self):
        return len(self.dataframe[self.dataframe['batsman_runs'] == 3])

    def get_fours(self):
        return len(self.dataframe[self.dataframe['batsman_runs'] == 4])

    def get_sixes(self):
        return len(self.dataframe[self.dataframe['batsman_runs'] == 6])

    def batting_attributes(self):
        data = pd.DataFrame(
            {
            "attributes": ["Total runs","Batting avg","Strike rate","Extra runs","Singles","Doubles","Triples","Fours","Sixes"],
             "score": [self.total_runs,self.batting_avg(),self.strike_rate,self.extra_runs,self.get_singles(),self.get_doubles(),self.get_triples(),self.get_fours(),self.get_sixes()]
            }
        )
        return data
        # return f"""
        # Total runs: {self.total_runs} \n
        # Batting avg: {self.batting_avg():.2f} \n
        # Strike rate: {self.strike_rate:.2f} \n
        # Extra runs: {self.extra_runs} \n
        # Singles: {self.get_singles()} \n
        # Doubles: {self.get_doubles()} \n
        # Triples: {self.get_triples()} \n
        # Fours: {self.get_fours()} \n
        # Sixes: {self.get_sixes()}"""

class FieldingAttributes:
    def __init__(self, dataframe):
        self.dataframe = dataframe
        self.num_fielding_dismissals = len(self.dataframe)
        self.catches = len(self.dataframe[self.dataframe['dismissal_kind'] == "caught"])
        self.run_outs = len(self.dataframe[self.dataframe['dismissal_kind'] == "run out"])
        self.stumpings = len(self.dataframe[self.dataframe['dismissal_kind'] == "stumped"])

    def fielder_attributes(self):
        data = pd.DataFrame(
            {
            "attributes": ["Total dismissals","Catches","Run outs","Stumpings"],
             "score": [self.num_fielding_dismissals,self.catches,self.run_outs,self.stumpings]
            }
        )

        return data
        # return f"""
        # Total dismissals: {self.num_fielding_dismissals} \n
        # Catches: {self.catches} \n
        # Run outs: {self.run_outs} \n
        # Stumpings: {self.stumpings}"""