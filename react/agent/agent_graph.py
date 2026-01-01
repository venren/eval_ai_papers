"""LangGraph-based ReACT trading agent with state machine, trajectory memory, and clear logging."""

import json
import re
from typing import Any, Dict, List

from react.agent.agent_state import AgentState, Action
from react.agent.prompts import (
    system_prompt,
    initial_user_prompt,
    trajectory_thinking_prompt,
    decision_prompt,
)
from react.data_models import Portfolio
from react.tools import fetch_price_data
from react.llm.open_router import call as invoke_llm

from langgraph.graph import StateGraph

# LangGraph imports
from langgraph.graph import StateGraph


class TradingAgentGraph:
    """ReACT agent with trajectory memory and dynamic observations."""

    def __init__(self, model_name: str = "mistralai/mistral-7b-instruct", max_think_steps: int = 3):
        """Initialize agent with OpenRouter LLM via open_router.py and build LangGraph."""
        self.model_name = model_name
        self.max_think_steps = max_think_steps
        self.graph = self._build_graph()  # Build and compile graph

    def _node_observe(self, state: AgentState) -> AgentState:
        """Node: Fetch market data."""
        print(f"\n{'='*70}")
        print(f"[OBSERVE] Day {state['day']}")
        print(f"{'='*70}")
        
        candidate_symbols = state.get("candidate_symbols", [])
        
        # Fetch prices and valuation data
        price_data = fetch_price_data(candidate_symbols)
        prices = {t: d["price"] for t, d in price_data.items() if d["price"] is not None}
        state["prices"] = prices
        state["portfolio"].update_prices(prices)
        
        # Log observation
        log = f"[OBSERVE] Fetched prices for {len(prices)} symbols\n"
        log += f"  ├─ Portfolio value: ${state['portfolio'].total_market_value():.2f}\n"
        log += f"  └─ Holdings: {list(state['portfolio'].positions.keys())}"
        
        print(log)
        state["messages"].append(log)
        state["observations"] = {
            "prices": prices,
            "price_data": price_data,  # Include full price data with moving averages
            "timestamp": state["day"]
        }
        
        return state

    def _node_think(self, state: AgentState) -> AgentState:
        """Node: Multi-step thinking with trajectory memory."""
        print(f"\n{'='*70}")
        print(f"[THINK] Step {len(state['trajectory']) + 1} of {self.max_think_steps}")
        print(f"{'='*70}")
        
        # Build trajectory context from prior actions
        trajectory_context = self._build_trajectory_context(state)
        
        # Prepare prompt with full context
        if len(state["trajectory"]) == 0:
            # First thinking step
            user_prompt = initial_user_prompt(
                {
                    "day": state["day"],
                    "portfolio_value": state["portfolio"].total_market_value(),
                    "cash": state["portfolio"].cash,
                    "holdings": state["portfolio"].to_dict(),
                    "prices": state["observations"]["prices"],
                    "price_data": state["observations"]["price_data"]
                },
                state.get("candidate_symbols", [])
            )
            print("[THINK] Initial analysis - evaluating market conditions")
        else:
            # Follow-up thinking with trajectory
            user_prompt = trajectory_thinking_prompt(trajectory_context)
            print(f"[THINK] Continuing analysis with prior context")
        
        # Invoke LLM
        response = self._invoke_llm(user_prompt)
        action = response.get("action", "done").lower()
        reasoning = response.get("reasoning", "")
        
        # Log thinking step
        log = f"  ├─ Decision: {action.upper()}\n"
        log += f"  └─ Reasoning: {reasoning}"
        print(log)
        state["messages"].append(log)
        
        # Record in trajectory
        state["trajectory"].append({
            "step": len(state["trajectory"]) + 1,
            "action": action,
            "reasoning": reasoning,
            "timestamp": state["day"]
        })
        
        # Store current response for routing
        state["_current_llm_response"] = response
        
        return state

    def _route_from_think(self, state: AgentState) -> str:
        """Route based on LLM thinking action."""
        if len(state["trajectory"]) >= self.max_think_steps:
            print(f"[ROUTE] Max thinking steps reached ({self.max_think_steps}), moving to DECIDE")
            return "decide"
        
        action = state["_current_llm_response"].get("action", "done").lower()
        
        if action == "observe":
            print(f"[ROUTE] Agent requested more observations, going to OBSERVE")
            return "observe"
        elif action == "think":
            print(f"[ROUTE] Agent wants to think more, continuing THINK loop")
            return "think"
        else:
            print(f"[ROUTE] Agent ready to decide, moving to DECIDE")
            return "decide"

    
    def _clean_json_text(self, text: str) -> str:
        """Best-effort cleanup for malformed JSON from LLMs."""
        return text.strip().replace("{{", "{").replace("}}", "}")

    def _build_graph(self):
        """Build and compile the LangGraph state machine."""
        workflow = StateGraph(AgentState)
        
        # Add nodes for each phase
        workflow.add_node("observe", self._node_observe)
        workflow.add_node("think", self._node_think)
        workflow.add_node("decide", self._node_decide)
        workflow.add_node("act", self._node_act)
        
        # Set entry point
        workflow.set_entry_point("observe")
        
        # Define edges
        workflow.add_edge("observe", "think")
        
        # Conditional routing from think
        workflow.add_conditional_edges(
            "think",
            self._route_from_think,
            {"think": "think", "observe": "observe", "decide": "decide"}
        )
        
        # Direct edges to final nodes
        workflow.add_edge("decide", "act")
        
        # Compile and return
        return workflow.compile()

    def _node_decide(self, state: AgentState) -> AgentState:
        """Node: Final decision with full context."""
        print(f"\n{'='*70}")
        print(f"[DECIDE] Making final trading decision")
        print(f"{'='*70}")
        
        # Build decision prompt with trajectory
        trajectory_summary = ""
        if state["trajectory"]:
            trajectory_summary = "**Thinking Trajectory:**\n"
            for t in state["trajectory"]:
                trajectory_summary += f"  Step {t['step']}: {t['action'].upper()} → {t['reasoning']}\n"
        
        decision_ctx = {
            "day": state["day"],
            "portfolio_value": state["portfolio"].total_market_value(),
            "cash": state["portfolio"].cash,
            "holdings": state["portfolio"].to_dict(),
            "prices": state["observations"]["prices"],
            "price_data": state["observations"]["price_data"],
            "trajectory": trajectory_summary
        }
        
        user_prompt = decision_prompt(decision_ctx)
        
        response = self._invoke_llm(user_prompt)
        action = self.decide_action(response)
        
        # Log decision
        log = f"  ├─ Final Action: {action['type'].upper()}\n"
        if action["symbol"]:
            log += f"  ├─ Symbol: {action['symbol']}\n"
            log += f"  ├─ Quantity: {action['quantity']}\n"
        log += f"  └─ Reasoning: {action['reasoning']}"
        print(log)
        state["messages"].append(log)
        state["_final_action"] = action
        
        return state

    def _node_act(self, state: AgentState) -> AgentState:
        """Node: Execute the action."""
        print(f"\n{'='*70}")
        print(f"[ACT] Executing trading action")
        print(f"{'='*70}")
        
        action = state["_final_action"]
        
        if action["type"] == "buy":
            current_price = state["prices"].get(action["symbol"], 0.0)
            state["portfolio"].buy(
                symbol=action["symbol"],
                quantity=action["quantity"],
                current_price=current_price
            )
        elif action["type"] == "sell":
            current_price = state["prices"].get(action["symbol"], 0.0)
            state["portfolio"].sell(
                symbol=action["symbol"],
                quantity=None,  # Sell all
                current_price=current_price
            )
        else:
            print(f"  - No action taken (DONE)")
        
        state["actions"].append(action)
        state["day"] += 1
        state["trajectory"] = []  # Reset trajectory for next episode
        
        print(f"\n[PORTFOLIO_UPDATE]")
        print(f"  ├─ Portfolio (Holdings): ${state['portfolio'].total_market_value():.2f}")
        print(f"  ├─ Cash: ${state['portfolio'].cash:.2f}")
        print(f"  ├─ Total Value: ${state['portfolio'].total_value():.2f}")
        print(f"  └─ Holdings: {state['portfolio'].to_dict()}")
        
        return state

    def _build_trajectory_context(self, state: AgentState) -> str:
        """Build human-readable trajectory context for LLM."""
        context = "**Prior Thinking Steps:**\n"
        for t in state["trajectory"]:
            context += f"  Step {t['step']}: {t['action'].upper()}\n"
            context += f"    → {t['reasoning']}\n"
        context += f"\n**Current Market State:**\n"
        context += f"  Portfolio Value: ${state['portfolio'].total_market_value():.2f}\n"
        context += f"  Holdings: {state['portfolio'].to_dict()}\n"
        context += f"  Prices: {state['observations'].get('prices', {})}"
        return context

    def _invoke_llm(self, user_prompt: str) -> Dict[str, Any]:
        """Invoke LLM using open_router.call and parse JSON response."""
        try:
            sys_prompt = system_prompt()
            
            # Log user prompt only
            print(f"\n[USER_PROMPT]\n{user_prompt}\n")
            
            response = invoke_llm(
                prompt=user_prompt,
                model_name=self.model_name,
                system_prompt=sys_prompt
            )
            parsed = self._parse_llm_response(response)
            print(f"[LLM_RESPONSE] {parsed}")
            return parsed
        except Exception as e:
            print(f"[ERROR] LLM error: {str(e)}")
            import traceback
            traceback.print_exc()  # Print full traceback for debugging
            return {"action": "done", "reasoning": f"LLM error: {str(e)}"}

    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON from LLM response with improved error handling."""
        if not response or not response.strip():
            print("[ERROR] Empty response from LLM")
            return {"action": "done", "reasoning": "Empty LLM response"}

        cleaned = self._clean_json_text(response)

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        try:
            json_match = re.search(
                r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}',
                cleaned,
                re.DOTALL,
            )
            if json_match:
                return json.loads(json_match.group(0))
        except (json.JSONDecodeError, AttributeError):
            pass

        print("[ERROR] Could not parse JSON from response:")
        print(f"[ERROR] Raw: {response[:500]}")

        return {
            "action": "done",
            "reasoning": "Could not parse LLM response",
            "trade_action": "done",
            "symbol": "",
            "quantity": 0,
        }


    def decide_action(self, llm_response: Dict[str, Any]) -> Action:
        """Extract trading action from LLM response."""
        trade_action = llm_response.get("trade_action", "done").lower()
        symbol = llm_response.get("symbol", "").upper()
        quantity = float(llm_response.get("quantity", 0))
        reasoning = llm_response.get("reasoning", "No decision made")
        
        if trade_action not in ["buy", "sell", "done"]:
            trade_action = "done"
        
        return {
            "type": trade_action,
            "symbol": symbol,
            "quantity": quantity,
            "reasoning": reasoning
        }

    def run(self, initial_state: AgentState, candidate_symbols: List[str], max_episodes: int = 3) -> AgentState:
        """Run agent for max_episodes trading days."""
        state = initial_state
        state["candidate_symbols"] = candidate_symbols
        state["trajectory"] = []
        state["observations"] = {}
        state["_current_llm_response"] = {}
        state["_final_action"] = {}
        
        print(f"\n\n{'#'*70}")
        print(f"# TRADING AGENT START (ReACT Implementation with LangGraph)")
        print(f"# Model: {self.model_name}")
        print(f"# Max Episodes: {max_episodes}")
        print(f"# Symbols: {candidate_symbols}")
        print(f"# Initial Cash: ${state['portfolio'].cash:.2f}")
        print(f"# Initial Holdings Value: ${state['portfolio'].total_market_value():.2f}")
        print(f"# Initial Total Value: ${state['portfolio'].total_value():.2f}")
        print(f"{'#'*70}")
        
        for episode in range(max_episodes):
            print(f"\n\n{'*'*70}")
            print(f"* EPISODE {episode + 1} / {max_episodes}")
            print(f"{'*'*70}")
            
            # Run one complete episode
            state = self._run_episode(state)
            
            print(f"\n[EPISODE_{episode + 1}_SUMMARY]")
            print(f"  ├─ Final Day: {state['day']}")
            print(f"  ├─ Holdings Value: ${state['portfolio'].total_market_value():.2f}")
            print(f"  ├─ Cash: ${state['portfolio'].cash:.2f}")
            print(f"  ├─ Total Value: ${state['portfolio'].total_value():.2f}")
            print(f"  ├─ Holdings: {state['portfolio'].to_dict()}")
            print(f"  └─ Actions Taken: {len(state['actions'])}")
        
        print(f"\n\n{'#'*70}")
        print(f"# TRADING AGENT COMPLETE")
        print(f"# Final Holdings Value: ${state['portfolio'].total_market_value():.2f}")
        print(f"# Final Cash: ${state['portfolio'].cash:.2f}")
        print(f"# Final Total Value: ${state['portfolio'].total_value():.2f}")
        print(f"# Total Actions: {len(state['actions'])}")
        print(f"# Total Days: {state['day'] - 1}")
        print(f"{'#'*70}\n")
        
        return state

    def _run_episode(self, state: AgentState) -> AgentState:
        """Run one complete episode using compiled LangGraph state machine."""
        return self.graph.invoke(state)
