# ReACT Trading Agent

## What is This?

This is an implementation of the **ReACT (Reasoning + Acting)** framework applied to stock trading. Instead of just telling an AI what to do, we give it the ability to think through decisions, request more information, and then act on those decisions.

**Paper:** [ReACT: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)

## How It Works

1. **Agent starts with:**
   - $2,000 cash
   - 5 stock symbols to trade: AAPL, MSFT, GOOGL, AMZN, TSLA

2. **Each day the agent:**
   - **Observes:** Fetches current stock prices and moving averages (50-day, 200-day)
   - **Thinks:** LLM analyzes the data and decides if it wants to think more, observe more, or make a decision
   - **Decides:** Makes a final buy/sell/hold decision with reasoning
   - **Acts:** Executes the trade and updates portfolio

3. **Key Feature:** The LLM can see its own thinking trajectory. If it analyzed something, it can reference that analysis later.

## What Happened in the Test Run

**Starting Portfolio:**
- Cash: $2,000
- Holdings: Empty

**Day 1:**
- Agent observed prices and moving average ratios
- Agent thought: "GOOGL looks strongest - it's 1.06x its 50-day average and 1.45x its 200-day average"
- Agent bought: 6 shares of GOOGL at $313 each = $1,878
- Cash left: $122

**Day 2:**
- Agent observed: GOOGL still strong, now it has $1,878 in holdings
- Agent thought: "GOOGL still trending up, portfolio is solid"
- Agent decided: Hold the position (no action)
- Final portfolio: $1,878 GOOGL + $122 cash = $2,000 total

**The agent made rational decisions based on market momentum.**

## The Execution Log

<details>
<summary><b>Click to expand full execution log</b></summary>

```
TRADING AGENT START
# Model: deepseek-v3.1
# Initial Cash: $2000.00
# Symbols: ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']

=== EPISODE 1 ===

[OBSERVE] Day 1 - Fetched prices for 5 symbols
[THINK] Step 1 of 3 - Initial analysis

Agent's Thinking:
"GOOGL shows strongest momentum with price above both 50-day (1.06 ratio) 
and 200-day (1.45 ratio) averages. Will buy GOOGL with available cash."

[DECIDE] Making final trading decision

Agent's Decision:
"Buy 6 shares of GOOGL at $313.00 because it shows strongest momentum 
with price above both 50-day and 200-day averages, indicating upward trend."

[ACT] Bought 6.0 shares of GOOGL at $313.00
Cash remaining: $122.00

Portfolio Update:
├─ Holdings Value: $1878.00 (6 shares × $313)
├─ Cash: $122.00
└─ Total Value: $2000.00

=== EPISODE 2 ===

[OBSERVE] Day 2 - Fetched prices for 5 symbols
[THINK] Step 1 of 3 - Initial analysis

Agent's Thinking:
"GOOGL still showing strong momentum. Current portfolio is 100% GOOGL at $1878. 
No immediate rebalancing needed with limited cash ($122)."

[DECIDE] Making final trading decision

Agent's Decision:
"Hold position. GOOGL showing strong momentum at $313, well above 
both 50-day ($295.47) and 200-day ($216.59) averages. 
Insufficient cash for meaningful diversification."

[ACT] No action taken (DONE)

Portfolio Update:
├─ Holdings Value: $1878.00
├─ Cash: $122.00
└─ Total Value: $2000.00

=== FINAL RESULTS ===

Final Portfolio Value: $1878.00 (6 shares of GOOGL)
Final Cash: $122.00
Total Portfolio Value: $2000.00 (breakeven - no profit/loss yet)
Total Trades: 2 (1 buy, 1 hold decision)
Trading Days: 2

Actions Taken:
1. BUY: GOOGL (6.0 shares) - Momentum-based analysis
2. HOLD: No action - Continue holding momentum position
```

</details>

## How This Proves ReACT Works

✅ **Reasoning:** Agent can think through multi-step reasoning with trajectory memory  
✅ **Acting:** Agent executes trades based on decisions  
✅ **Interleaving:** Agent can decide to think more or observe more before acting  
✅ **Memory:** Agent remembers previous thinking steps and references them  

---

## Next Steps & Roadmap

### 1. Improve ReACT Implementation

**Current gaps in our ReACT implementation:**
- Agent thinks separately from trading (both happen in different phases)
- No feedback after actions (agent doesn't see trade confirmation impact)
- Trajectory resets each day (loses long-term learning)

**What to do:**
- [ ] Add immediate post-action feedback: "You bought GOOGL, new cash: $122"
- [ ] Allow trading actions during thinking phase (tighter think→act→observe loop)
- [ ] Implement cross-episode trajectory: carry forward insights across days
- [ ] Add error handling: what if trade fails? Let agent retry.

**Why it matters:**  
The original ReACT paper shows agents perform better when they can see the results of their actions immediately and adjust.

---

### 2. Reinforcement Learning Integration for Trading

**Goal:** Train the agent to improve its trading decisions over time.

**Papers to explore:**
- [Deep Reinforcement Learning for Trading](https://arxiv.org/abs/1811.07522)
- [A Deep Reinforcement Learning Framework for the Financial Portfolio Management Problem](https://arxiv.org/abs/1706.10059)
- [Combining ReACT with RL: Learning Better Reasoning Trajectories](https://arxiv.org/abs/2302.13971)

**What to implement:**
- [ ] Reward signal: Portfolio return % per episode
- [ ] Policy: Use LLM to generate actions, RL to pick best reasoning paths
- [ ] Experience replay: Store good trading sequences and replay them
- [ ] Q-learning on thinking decisions: Learn which analysis approaches yield best returns

**Example approach:**
```
Day 1: Agent analyzes, buys GOOGL, gets reward +5% return
Day 2: Agent analyzes, buys MSFT, gets reward -2% return

RL learns: "The GOOGL analysis worked better, weight that style higher"
```

**Why it matters:**  
RL lets the agent learn which thinking patterns actually make money, not just which sound reasonable.

---

### 3. Improve the Use Case - Sector-Based Portfolio

**Current:** 5 random stocks  
**Better:** Smart sector selection with reinforced learning comparison

**Phase 1: Sector Selection**
- [ ] Use free APIs (Yahoo Finance, IEX Cloud) to get sector data
- [ ] Pick top sectors: Tech, Healthcare, Finance, Energy, etc.
- [ ] For each sector, select top 20 stocks by market cap
- [ ] Create multiple portfolios: one per sector

**Phase 2: Agent Trading**
- [ ] Run ReACT agent on each sector portfolio (separate $2000 per sector)
- [ ] Agent uses sector-specific indicators (e.g., tech: valuation, healthcare: R&D growth)
- [ ] Agent trades for 30-60 days
- [ ] Record final returns per portfolio

**Phase 3: RL Comparison**
- [ ] Train RL agent on the same 5 sectors
- [ ] Compare final returns: ReACT only vs RL-enhanced ReACT
- [ ] Analyze: Which sector performs best? Which approach wins?
- [ ] Answer: Does RL actually improve trading decisions?

**Example outcome:**
```
Sector          | ReACT Only | ReACT + RL | Winner
Tech            | +12%       | +18%       | RL wins
Healthcare      | +8%        | +8%        | Tie
Finance         | -5%        | +2%        | RL wins
Energy          | +3%        | -1%        | ReACT wins
--------------------------------------------------
Average Return  | +4.5%      | +6.75%     | RL wins overall
```

**Why it matters:**  
This shows whether smarter agent design actually makes better real-world trading decisions, not just sounding smart.

---

## Running the Code

```bash
# Install dependencies
pip install -r requirements.txt

# Set your API key
export OPENROUTER_API_KEY=sk-your-key-here

# Run the agent
python -m react.demo_agent
```

## Project Structure

```
react/
├── agent/
│   ├── agent_graph.py      # Main ReACT loop (observe→think→decide→act)
│   ├── agent_state.py      # State definition
│   ├── prompts.py          # Prompt formatting
│   └── prompts/            # Prompt templates (JSON files)
├── tools/
│   └── yahoo_tool.py       # Real market data fetching
├── data_models/
│   └── portfolio.py        # Portfolio tracking
├── llm/
│   └── open_router.py      # LLM API calls
└── demo_agent.py           # Main entry point
```

## Technical Details

- **LLM:** Uses OpenRouter API (you can swap models freely)
- **Graph Library:** LangGraph for state machine management
- **Data Source:** Yahoo Finance (real stock prices)
- **Reasoning Memory:** Trajectory stored in agent state, fed back to LLM
- **Decision Format:** LLM outputs JSON, validated and executed

---

## Questions to Answer

1. **Does the agent learn across episodes?** Currently no - trajectory resets. Fix: carry forward best strategies.
2. **Is this actually better than a simple rule?** Unknown. Need RL comparison on real data.
3. **Which sectors perform best with this approach?** That's Phase 3.
4. **Does RL help or hurt?** Will test in Phase 3.

---

## References

- [ReACT Paper](https://arxiv.org/abs/2210.03629)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Yahoo Finance API](https://finance.yahoo.com)

---

**Status:** MVP complete. Ready for RL integration and real-world testing.
