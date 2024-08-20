import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import altair as alt
import numpy as np

from backend import *

# Load data:
deliveries_data = pd.read_csv("./data/deliveries.csv")
matches_data = pd.read_csv("./data/matches.csv")

# Update venue names:
deliveries_df = deliveries_data[['match_id', 'batter', 'bowler', 'batsman_runs', 'extra_runs', 'extras_type', 'total_runs', 'is_wicket', 'player_dismissed', 'dismissal_kind', 'fielder']]
matches_df = matches_data[['id', 'venue']]
matches_df.loc[matches_df['venue'] == 'Arun Jaitley Stadium, Delhi','venue'] = "Arun Jaitley Stadium"
matches_df.loc[matches_df['venue'] == 'Brabourne Stadium, Mumbai','venue']='Brabourne Stadium'
matches_df.loc[matches_df['venue'] == 'Dr DY Patil Sports Academy, Mumbai','venue']='Dr DY Patil Sports Academy'
matches_df.loc[matches_df['venue'] == 'Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium, Visakhapatnam','venue']='Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium'
matches_df.loc[matches_df['venue'] == 'Eden Gardens, Kolkata','venue']='Eden Gardens'
matches_df.loc[matches_df['venue'] ==  'Himachal Pradesh Cricket Association Stadium, Dharamsala','venue']= 'Himachal Pradesh Cricket Association Stadium'
matches_df.loc[(matches_df['venue'] == 'M Chinnaswamy Stadium, Bengaluru') | (matches_df['venue'] =='M.Chinnaswamy Stadium' ),'venue']='M Chinnaswamy Stadium'
matches_df.loc[(matches_df['venue'] == 'Rajiv Gandhi International Stadium, Uppal') | (matches_df['venue'] =='Rajiv Gandhi International Stadium, Uppal, Hyderabad' ),'venue']='Rajiv Gandhi International Stadium'
matches_df.loc[(matches_df['venue'] == 'MA Chidambaram Stadium, Chepauk') | (matches_df['venue'] =='MA Chidambaram Stadium, Chepauk, Chennai' ),'venue']='MA Chidambaram Stadium'
matches_df.loc[(matches_df['venue'] == 'Punjab Cricket Association IS Bindra Stadium, Mohali') | (matches_df['venue'] =='Punjab Cricket Association IS Bindra Stadium, Mohali, Chandigarh' )| (matches_df['venue'] == 'Punjab Cricket Association Stadium, Mohali' ),'venue']='Punjab Cricket Association IS Bindra Stadium'
matches_df.loc[matches_df['venue'] == 'Maharashtra Cricket Association Stadium, Pune','venue']='Maharashtra Cricket Association Stadium'
matches_df.loc[matches_df['venue'] == 'Sawai Mansingh Stadium, Jaipur','venue']='Sawai Mansingh Stadium'
matches_df.loc[matches_df['venue'] == 'Wankhede Stadium, Mumbai','venue']='Wankhede Stadium'




class HeadTOHead:
    def __init__(self,selected_skills,selected_players):
        self.selected_skills = selected_skills
        self.selected_players = selected_players
        self.skills = [ 'batter' if s == "BATTING" else 'bowler' if s == "BOWLING" else "fielder" for s in self.selected_skills ]

    # Returns a list of boolean masks for each player's performance in the selected skills.
    def two_players_df(self):
        return [deliveries_data[skill] == player for player,skill in zip(self.selected_players,self.skills)]
    
    # Returns a list of unique venues where the selected players have played.
    def venue_list(self):
        match_id_list = deliveries_df.loc[self.two_players_df()[0] & self.two_players_df()[1],'match_id'].unique()
        return matches_df[matches_df.id.isin(match_id_list)]['venue'].unique()

    # Returns a DataFrame containing performance data for the selected players.
    def final_dataframe(self):
        return deliveries_df.loc[self.two_players_df()[0] & self.two_players_df()[1]]
    
    # Filters the final DataFrame based on selected venues.
    def on_final_dataframe(self,selected_venues):
        final_dataframe = pd.DataFrame({})
        # If a venue is selected, update dataframes for two players based on the selected venue.
        for selected_venue in selected_venues:
            venue_df = deliveries_df[self.two_players_df()[0] & self.two_players_df()[1]].loc[
                (deliveries_data.match_id.isin(matches_df.loc[matches_df.venue == selected_venue, 'id'].unique()))]
            final_dataframe = pd.concat([venue_df,final_dataframe])
        return final_dataframe


    # Generates a bar chart with text annotations for the given data.
    def graph(self,data,col,wid,heig):
        # Create a bar chart for the given data (attributes vs. score)
        graph = alt.Chart(data).mark_bar().encode(y=alt.Y("attributes").title(""), x=alt.X("score").title(""),color=alt.value(col)).properties(width=wid,height=heig)
        # Create another bar chart with text labels for the scores
        graph_text = alt.Chart(data).mark_bar().encode(y=alt.Y("attributes").title(""), x=alt.X("score").title(""),color=alt.value('#FAF1EF')).properties(width=wid,height=heig).mark_text(
                align='right',baseline='middle',dx=-2).encode(text="score")
        # Combine the two charts and display the result
        return st.write(graph+graph_text)
            
    # Displays select bar for venues
    def select_venue(self):
        venue_col,empty_col = st.columns([1,1])

        with venue_col:
            selected_venues = st.multiselect("select venue", self.venue_list(), placeholder="select venue", key="f8")
        # Check if any venue is selected; if not, stop execution
        try:
            selected_venues[0] == None
        except:
            st.stop()
        return selected_venues


    def output(self):
        # Display header and subheader for player statistics
        st.header("Player Statistics")
        st.subheader(f"Head to Head: {self.selected_players[0]} vs {self.selected_players[1]}")        
        final_df = self.final_dataframe()

        # Toggle for selecting a venue
        on = st.toggle('Select Venue')

        # If the toggle is on, update the DataFrame with selected venues
        if on:
            final_df = self.on_final_dataframe(self.select_venue())
                
        # Depending on skills, display relevant statistics
        if 'fielder' in self.skills:
            self.graph(FieldingAttributes(final_df).fielder_attributes(),'#e91e63',800,250)
                
        else:
            # Display bowler and batsman statistics
            st.write(f"Number of matches: {HeadToHeadBowling(final_df).num_matches}")
            st.write(f"Total balls faced by {self.selected_players[0]} against {self.selected_players[1]}: {HeadToHeadBowling(final_df).total_balls}")

            st.subheader("Bowler Statistics")
            self.graph(BowlerAttributes(final_df).bowling_attributes(),'#e91e63',800,250)

            st.subheader("Batsman Statistics")
            self.graph(BatsmanAttributes(final_df).batting_attributes(),'#227425',800,350)



class PlayerPerformance:
    def __init__(self, selected_skills, selected_players):
        self.selected_skills = selected_skills
        self.selected_players = selected_players
        self.skills = [ 'batter' if s == "BATTING" else 'bowler' if s == "BOWLING" else "fielder" for s in self.selected_skills ]

    # Returns a list of boolean masks for each player's performance in the selected skills.
    def two_players_df(self):
        return [deliveries_data[self.skills[0]] == player for player in self.selected_players]

    # Returns a list of unique venues where the selected players have played.
    def venue_list(self):
        player1_match_id_list = deliveries_df.loc[self.two_players_df()[0],'match_id'].unique()
        player2_match_id_list = deliveries_df.loc[self.two_players_df()[1],'match_id'].unique()
        return matches_df[(matches_df.id.isin(player1_match_id_list)) & (matches_df.id.isin(player2_match_id_list))]['venue'].unique()

    # Returns a DataFrame containing performance data for the selected players.
    def final_dataframe(self,n):
        return deliveries_df.loc[self.two_players_df()[n]]
    
    # Filters the final DataFrame based on selected venues.
    def on_final_dataframe(self,selected_venues,n):
        final_dataframe = pd.DataFrame({})
        # If a venue is selected, update dataframes for two players based on the selected venue.
        for selected_venue in selected_venues:
            venue_df = deliveries_df[self.two_players_df()[n]].loc[
                (deliveries_data.match_id.isin(matches_df.loc[matches_df.venue == selected_venue, 'id'].unique()))]
        return pd.concat([venue_df,final_dataframe])
    

    # Generates a bar chart with text annotations for the given data.
    def graph(self,data1, data2):
        # Extract x, y1, and y2 values from the provided data
        x_values = np.array(data1['attributes'].values.tolist())
        y1_values = np.array(data1['score'].values.tolist())
        y2_values = np.array(data2['score'].values.tolist())
        # Set figure size and autolayout settings
        plt.rcParams["figure.figsize"] = [5.50, 3.50]
        plt.rcParams["figure.autolayout"] = False
        fig, ax = plt.subplots(figsize=(17, 5))

        fig.set_facecolor("none")
        ax.set_facecolor("none")
        b1 = ax.barh(x_values, y1_values, color="skyblue")
        b2 = ax.barh(x_values, y2_values, left=y1_values, color="limegreen")
        # Add legend with player names
        ax.legend([b1, b2], [self.selected_players[0], self.selected_players[1]], title="", loc="upper right")
        # Display text labels for values
        for i, (v1, v2) in enumerate(zip(y1_values, y2_values)):
            ax.text(5, i, str(v1), color='black', verticalalignment='top', horizontalalignment='left')
            ax.text(v1 + v2, i, str(v2), color='darkgreen', verticalalignment='bottom', horizontalalignment='left')
        # Show the plot
        st.pyplot(fig)

    # Displays select bar for venues
    def select_venue(self):
        venue_col,empty_col = st.columns([1,1])

        with venue_col:
            selected_venues = st.multiselect("select venue", self.venue_list(), placeholder="select venue", key="f0")
        # Check if any venue is selected; if not, stop execution
        try:
            selected_venues[0] == None
        except:
            st.stop()
        return selected_venues

    def output(self):
        # Display subheader for player performance comparison
        st.subheader(f"Player Performance : {self.selected_players[0]} vs {self.selected_players[1]}")      
        # Create DataFrames for both players using the final_dataframe method
        player1_df = self.final_dataframe(0)
        player2_df = self.final_dataframe(1)
        # Toggle for selecting a venue
        on = st.toggle('Select Venue')
        # If the toggle is on, update DataFrames based on selected venue
        if on:
            s = self.select_venue()
            player1_df = self.on_final_dataframe(s,0)
            player2_df = self.on_final_dataframe(s,1)

        # Depending on skills, generate relevant graphs
    
        if 'fielder' in self.skills:
            self.graph(FieldingAttributes(player1_df).fielder_attributes(),FieldingAttributes(player2_df).fielder_attributes())

        elif 'bowler' in self.skills:
            self.graph(BowlerAttributes(player1_df).bowling_attributes(),BowlerAttributes(player2_df).bowling_attributes())

        else:
            self.graph(BatsmanAttributes(player1_df).batting_attributes(),BatsmanAttributes(player2_df).batting_attributes())

        
