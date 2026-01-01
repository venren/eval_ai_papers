"""
Demo: ReACT Trading Agent with LLM + LangGraph (Full Implementation)

Requires: OPENROUTER_API_KEY environment variable

Usage: 
  export OPENROUTER_API_KEY=sk-...
  python -m react.demo_agent (run from repo root)
"""

import os
from react.agent.agent_graph import TradingAgentGraph
from react.agent.agent_state import AgentState
from react.data_models import Portfolio
from dotenv import load_dotenv

load_dotenv()

def main():
    # Check for API key
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("Error: OPENROUTER_API_KEY environment variable not set.")
        print("Please set your OpenRouter API key and try again.")
        return
    
    # Initialize portfolio with some stocks and $1000 initial cash
    initial_positions = []
    portfolio = Portfolio(initial_positions, initial_cash=2000.0)
    
    # Initialize agent state with all required fields
    initial_state: AgentState = {
        "day": 1,
        "portfolio": portfolio,
        "prices": {},
        "messages": [],
        "actions": [],
        "observations": {},
        "trajectory": [],
        "candidate_symbols": [],
        "_current_llm_response": {},
        "_final_action": {}
    }
    
    # Create agent with LangGraph
    agent = TradingAgentGraph(
        model_name="nex-agi/deepseek-v3.1-nex-n1:free",
        max_think_steps=3
    )
    
    # Run agent
    final_state = agent.run(
        initial_state=initial_state,
        candidate_symbols=["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"],
        max_episodes=2
    )
    
    # Print final summary
    print(f"\n\n{'='*70}")
    print("FINAL AGENT STATE SUMMARY")
    print(f"{'='*70}")
    print(f"Final Portfolio Value: ${final_state['portfolio'].total_market_value():.2f}")
    print(f"Holdings: {final_state['portfolio'].to_dict()}")
    print(f"Total Messages/Logs: {len(final_state['messages'])}")
    print(f"Total Actions Taken: {len(final_state['actions'])}")
    print(f"Total Trading Days: {final_state['day'] - 1}")
    
    if final_state["actions"]:
        print(f"\nActions Taken:")
        for i, action in enumerate(final_state["actions"], 1):
            print(f"  {i}. {action['type'].upper()}: {action['symbol']} ({action['quantity']}) - {action['reasoning']}")


if __name__ == "__main__":
    main()

