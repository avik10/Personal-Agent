"""Weather Specialist Agent."""

from langchain_core.tools import StructuredTool
from langgraph.prebuilt import create_react_agent

from agents.base import llm
from tools.weather_tools import (
    get_current_weather,
    get_weather_forecast,
)

weather_tools = [
    StructuredTool.from_function(get_current_weather),
    StructuredTool.from_function(get_weather_forecast),
]

WEATHER_PROMPT = (
    "You are the Weather Specialist Agent. "
    "Your responsibility is to fetch and report accurate live weather conditions and forecasts "
    "using your tools (get_current_weather, get_weather_forecast). "
    "Always provide your final response in clear, concise English."
)

weather_agent = create_react_agent(llm, weather_tools, prompt=WEATHER_PROMPT)
