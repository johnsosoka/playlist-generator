from langchain import PromptTemplate
from spotipy import SpotifyOAuth
from langchain.vectorstores import FAISS
from langchain.docstore import InMemoryDocstore
from langchain.embeddings import OpenAIEmbeddings
import faiss
from config.config_loader import ConfigLoader
import spotipy
from langchain_experimental.autonomous_agents import AutoGPT
from langchain.chat_models import ChatOpenAI
from langchain.tools import tool, WriteFileTool, ReadFileTool
from langchain.agents import load_tools


import os
# Define your embedding model
embeddings_model = OpenAIEmbeddings()
# Initialize the vectorstore as empty


embedding_size = 1536
index = faiss.IndexFlatL2(embedding_size)
vectorstore = FAISS(embeddings_model.embed_query, index, InMemoryDocstore({}), {})


scope = "user-library-read playlist-modify-public playlist-modify-private"

# configure
config_loader = ConfigLoader("/Users/john/code/misc/playlist-generator/src/config.yml")
config_loader.set_environment_variables()
for key, value in os.environ.items():
    print(f"{key}={value}")

config = config_loader.load_config()

from src.tools.add_song_tool import AddSongTool
from src.tools.playlist_content_tool import PlaylistContentsTool
from tools.find_song_tool import FindSongTool

spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

tools = load_tools(["google-search"])
tools.append(WriteFileTool())
tools.append(ReadFileTool())
tools.append(FindSongTool())
tools.append(AddSongTool())
tools.append(PlaylistContentsTool())

agent = AutoGPT.from_llm_and_tools(
    ai_name="Tom",
    ai_role="Assistant",
    tools=tools,
    llm=ChatOpenAI(temperature=0),
    memory=vectorstore.as_retriever(),
)
# Set verbose to be true
agent.chain.verbose = True

# ORIGINAL DUPES..
# task_template = """
# Your task is to build a themed spotify playlist. The playlist must not contain any duplicate songs.
#
# 1. Identify songs that fit the theme: '{song_theme}' using existing knowledge and internet search.
# 2. Identify that the song is not already in the playlist with id {playlist_id}
# 3. If the song is not currently in the playlist, Find the song on spotify.
# 4. If spotify returns a URI, add the song to playlist id {playlist_id}
# 5. Your task is complete when the playlist has {num_items} songs in it.
# """

task_template = """
Your task is to build a themed spotify playlist. The playlist must not contain any duplicate songs. To add
a song to a spotify playlist, you must identify the URI.

1. Identify songs that fit the theme: '{song_theme}' using existing knowledge and internet search.
2. Find the URI for the song on spotify.
3. Check the playlist contents to ensure that the song is not already in the playlist. If the song is already in the playlist DO NOT ADD IT. Find another song.
4. Add the song to playlist id {playlist_id}

Your task is complete when the playlist has {num_items} songs in it.

Remember that it is essential that only unique songs are added to the playlist. Check the playlist contents before adding a song
to ensure that it is not already in the playlist. If the song is already in the playlist and you add it again, you will be penalized.
"""

prompt = PromptTemplate.from_template(task_template)


# TODO Capture from input
playlist_id = "0ylrX64UMWUwS1gjrDY2UO"
topic = "songs about mountains"
target_playlist_size = 5


agent.run([prompt.format(song_theme=topic, playlist_id=playlist_id, num_items=target_playlist_size)])

