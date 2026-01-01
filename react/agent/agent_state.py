from typing import TypedDict, List, Dict, Any, Literal
from react.data_models import Portfolio


ActionType = Literal["think", "buy", "sell", "done"]


class Action(TypedDict):
    """Represents an action in the ReACT loop."""
    type: ActionType
    symbol: str  # empty string for "think" and "done"
    quantity: float  # 0 for "think" and "done"
    reasoning: str


class AgentState(TypedDict, total=False):
    """State passed through the ReACT agent loop."""
    messages: List[str]  # Reasoning/observation history
    portfolio: Portfolio
    prices: Dict[str, float]  # Current stock prices
    day: int  # Current day/step
    actions: List[Action]  # History of actions taken
    observations: Dict[str, Any]  # Current market observations
    trajectory: List[Dict[str, Any]]  # Thinking trajectory (steps taken)
    candidate_symbols: List[str]  # Symbols to trade
    _current_llm_response: Dict[str, Any]  # Temporary: current LLM response
    _final_action: Action  # Temporary: final decision action
    history: Dict[str, Any]