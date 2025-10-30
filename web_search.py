import braintrust
from langchain_tavily import TavilySearch
from langchain_core.tools import tool

import streamlit as st

project = braintrust.projects.create(name="Playlist Generation")

tavily_key = st.secrets["TAVILY_API_KEY"]

@tool
def search(query: str) -> list:
    """Search the web for a query related to an artist, album, or other music-related topic."""
    tavily_search = TavilySearch(api_key=tavily_key, max_results=2, include_raw_content=True)
    results = tavily_search.invoke(query)
    return results

project.tools.create(
    handler=search,
    name="Web Search",
    slug="web-search-pg-1",
    description="Tavily web search to find music information",
    parameters="query to run",
    returns="results of the query to be used in playlist generation"
)