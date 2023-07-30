from langchain.agents import initialize_agent, AgentType
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.tools import tool
from langchain.agents import load_tools
import spotipy
import json
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials


scope = "user-library-read playlist-modify-public playlist-modify-private"

spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

song_template = '[{"song": "title", "artist": "artist"}]'

prompt = PromptTemplate.from_template("Using existing knowledge and the internet, consider songs that would work in a playlist with a theme: {theme} Once you have identified 10 songs, find them on spotify. Results must conform to {song_template}. If songs are not returned by the tool, think of different tracks and try again.")



llm = OpenAI()
chat_model = ChatOpenAI()



import json

@tool("find_on_spotify", return_direct=True)
def find_on_spotify(query: str) -> str:
    """Adds a batch of songs to a playlist on spotify. Accepts a list of json objects with keys "song" and "artist"."""
    # Parse the string into a list of dictionaries
    song_list = json.loads(query)

    # Initialize an empty string to store the output
    output = ""

    # Iterate over each dictionary in the list
    for song_dict in song_list:
        # Get the song and artist from the dictionary
        song = song_dict["song"]
        artist = song_dict["artist"]

        spotify_search(song, artist)

        # Add the song and artist to the output string
        output += f"Song: {song}, Artist: {artist}\n"

    return "<DummySeachResult>\n"

# https://open.spotify.com/playlist/0ylrX64UMWUwS1gjrDY2UO?si=049b5b9c39d0480a
def spotify_search(song_title: str, artist: str):
    results = spotify.search(q=f"track:{song_title} artist:{artist}", type="track")

    # Check if the search returned any results
    if results["tracks"]["items"]:
        top_result_item = results["tracks"]["items"][0]
        spotify.playlist_add_items("0ylrX64UMWUwS1gjrDY2UO", [top_result_item["uri"]])
        return results
    else:
        # Handle the case where the search didn't return any results
        message = f"No results found for track:{song_title} artist:{artist}"
        print(message)
        return message

tools = load_tools(["google-search"])
tools.append(find_on_spotify)

agent = initialize_agent(
    tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True
)

agent.run(prompt.format(theme="idaho", song_template=song_template))
