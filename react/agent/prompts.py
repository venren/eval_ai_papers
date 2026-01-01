"""
Prompt loader and formatter for the ReACT trading agent.

Loads prompts from JSON files and formats them with runtime context.
"""

import json
import os
from typing import Dict, List, Tuple, Any

# Base path for prompt files
PROMPTS_DIR = os.path.join(os.path.dirname(__file__), "prompts")


def _load_prompt_file(filename: str) -> Dict[str, str]:
    """Load a prompt from JSON file."""
    filepath = os.path.join(PROMPTS_DIR, filename)
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        raise RuntimeError(f"Failed to load prompt {filename}: {e}")


def system_prompt() -> str:
    """Load the system prompt for the trading advisor."""
    data = _load_prompt_file("system.json")
    return data.get("system_prompt", "")


def initial_user_prompt(state: dict, candidate_symbols: List[str]) -> str:
    """Format the initial user prompt with portfolio and market data."""
    data = _load_prompt_file("initial.json")
    template = data.get("initial_prompt", "")
    
    # Format price data with moving average ratios for LLM analysis
    price_data_formatted = {}
    if "price_data" in state:
        for ticker, ticker_data in state["price_data"].items():
            price = ticker_data.get("price")
            fifty_day = ticker_data.get("fifty_day")
            two_hundred_day = ticker_data.get("two_hundred_day")
            
            ratio_50 = price / fifty_day if (price and fifty_day and fifty_day != 0) else None
            ratio_200 = price / two_hundred_day if (price and two_hundred_day and two_hundred_day != 0) else None
            
            price_data_formatted[ticker] = {
                "price": f"{price:.2f}" if price else "N/A",
                "50_day_avg": f"{fifty_day:.2f}" if fifty_day else "N/A",
                "200_day_avg": f"{two_hundred_day:.2f}" if two_hundred_day else "N/A",
                "ratio_50": f"{ratio_50:.2f}" if ratio_50 else "N/A",
                "ratio_200": f"{ratio_200:.2f}" if ratio_200 else "N/A"
            }
    
    return template.format(
        day=state["day"],
        portfolio_value=state["portfolio_value"],
        cash=state.get("cash", 0),
        holdings=state["holdings"],
        prices=state["prices"],
        price_data=price_data_formatted,
        candidate_symbols=candidate_symbols
    )


def trajectory_thinking_prompt(trajectory_context: str) -> str:
    """Continue thinking with prior trajectory context."""
    data = _load_prompt_file("trajectory.json")
    template = data.get("template", "")
    return template.format(trajectory_context=trajectory_context)


def decision_prompt(state: dict) -> str:
    """Format the final decision prompt with current state."""
    data = _load_prompt_file("decision.json")
    template = data.get("decision_prompt", "")
    
    trajectory_str = state.get("trajectory", "")
    
    # Format price data with moving average ratios for LLM analysis
    price_data_formatted = {}
    if "price_data" in state:
        for ticker, ticker_data in state["price_data"].items():
            price = ticker_data.get("price")
            fifty_day = ticker_data.get("fifty_day")
            two_hundred_day = ticker_data.get("two_hundred_day")
            
            ratio_50 = price / fifty_day if (price and fifty_day and fifty_day != 0) else None
            ratio_200 = price / two_hundred_day if (price and two_hundred_day and two_hundred_day != 0) else None
            
            price_data_formatted[ticker] = {
                "price": f"{price:.2f}" if price else "N/A",
                "50_day_avg": f"{fifty_day:.2f}" if fifty_day else "N/A",
                "200_day_avg": f"{two_hundred_day:.2f}" if two_hundred_day else "N/A",
                "ratio_50": f"{ratio_50:.2f}" if ratio_50 else "N/A",
                "ratio_200": f"{ratio_200:.2f}" if ratio_200 else "N/A"
            }
    
    return template.format(
        day=state["day"],
        portfolio_value=state["portfolio_value"],
        cash=state.get("cash", 0),
        holdings=state["holdings"],
        prices=state["prices"],
        price_data=price_data_formatted,
        trajectory=trajectory_str
    )
