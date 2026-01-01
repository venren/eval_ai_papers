# Evaluating AI Papers Through Implementation

Goal: Implement research papers, experiment with them, and measure real-world results.

## Implementations

| Paper | Description | Status | Details |
|-------|-------------|--------|---------|
| **ReACT** | Reasoning + Acting in LLMs for Trading | ✅ MVP | [Go to ReACT](./react/README.md) |

## What We Do

1. Pick an AI research paper
2. Implement it in code (not just theory)
3. Test on a real problem (e.g., trading)
4. Measure if it works better than baseline
5. Document findings

## Project Structure

```
eval_ai_papers/
├── react/              # ReACT paper implementation (trading agent)
├── requirements.txt    # Python dependencies
├── .env               # API keys (not committed)
└── README.md          # This file
```

## Getting Started

```bash
pip install -r requirements.txt
export OPENROUTER_API_KEY=sk-your-key
python -m react.demo_agent
```

---

**Currently exploring:** ReACT → RL integration → Sector-based portfolio comparison
