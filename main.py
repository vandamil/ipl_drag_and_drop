import streamlit as st
from components.mycomponent import mycomponent
from components.compo import compo
from components.field import field

import frontend 

# Set Streamlit page configuration
st.set_page_config(
    page_title="Cricket",
    page_icon="🧊",
    layout="wide")

# Toggle for player performance or head-to-head
on = st.toggle('Player performance')

if on:
     # Player performance section
    st.title('Player Performance')
    st.divider()
    # Create columns for skill selection and player selection.
    x,a,b,c,d = st.columns([0.2,.9,1,1.2,1])

    a.title("Drag skill")
    b.title("Drop skill :point_down:")
    d.title("Drag player")
    c.title(":point_down: Drop player ")
    a1,a2 = st.columns(2)
    # Custom components for input

    with a1:
        selected_skill = field(my_input_value=" ")
    with a2:
        selected_players = mycomponent(my_input_value = "")
    
    # Handle selected players
    try:
        selected_player1 = selected_players[0]
        selected_player2 = selected_players[1]
    
    except:
        # If no players are selected, stop execution
        st.stop()

    # Create a PlayerPerformance instance and display the output
    try:
        player_perfom = frontend.PlayerPerformance([selected_skill],selected_players)
        player_perfom.output()
    except:
        st.write("Data Not Available")

else:
    
    a1,a2 = st.columns(2)

    st.title('Head To Head')
    st.divider()

    x,a,b,c,d = st.columns([0.2,.9,1,1.2,1])

    a.title("Drag skill")
    b.title("Drop skill :point_down:")
    d.title("Drag player")
    c.title(":point_down: Drop player ")
    a1,a2 = st.columns(2)
    # Custom components for input

    with a1:
        select_skill = compo(my_input_value="")
    with a2:
        selected_players = mycomponent(my_input_value = "")

    # Handle selected players
    try:
        selected_player1 = selected_players[0]
        select_skill1 = select_skill[0]
    except:
        # If no players are selected, stop execution
        st.stop()

    # Calculate head-to-head statistics
    headtohead = frontend.HeadTOHead(select_skill,selected_players)
    headtohead.output()















    

