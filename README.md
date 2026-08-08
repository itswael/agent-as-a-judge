# Agent-as-a-Judge (Agricultural Answer Evaluation)

A multi-agent LLM-as-judge framework, built with [LangGraph](https://www.langchain.com/langgraph),
that compares two agricultural-chatbot answers to the same farmer question —
one generated with minimal context and one generated with additional
context (soil, weather, location, crop stage, etc.) — and produces a
structured, evidence-based judgment of which answer is better and why.

This is original research/evaluation tooling, not a copy of the general
"Agent-as-a-Judge" literature; the domain, metrics, and agent pipeline here
are purpose-built for judging an agricultural advisory chatbot.

## How it works

The evaluation runs as a LangGraph state graph of specialized agents, each
implemented as its own class under `src/agents/`:

1. **Evaluation Planner** (`planner_agent.py`) — classifies the question
   (agronomic category, risk level) and selects which metrics apply.
2. **Claim Extractor** (`claim_extractor_agent.py`) — pulls checkable claims
   (fertilizer, dosage, timing, safety, etc.) out of both answers.
3. **Evidence Checker**, **Metric Tool**, and **Context Impact** agents run
   in parallel (`agent_judge_graph.py` uses a `ThreadPoolExecutor`) to
   validate claims against supplied context, score each answer on the
   selected metrics, and assess how much the extra context actually helped.
4. **Final Decision Agent** (`final_decision_agent.py`) — combines a
   deterministic weighted score (from `configs/metric_weights.yaml`) with
   LLM reasoning to pick a winner (`minimum_context_answer`,
   `agricultural_chatbot_answer`, or `tie`) with a confidence score and
   explanation.

There's also `src/graph/simplified_agent_judge_graph.py`, a leaner/faster
variant of the same pipeline.

### Metrics (`metrics/`)

Each metric is its own LLM-graded rubric, weighted and combined
deterministically in the final decision step:

- `specificity.py` — does the answer address the exact question with
  concrete details rather than generic advice?
- `actionability.py` — is the guidance practically implementable in the
  field (evaluated against the agronomic "4R" framework: right source,
  rate, time, place)?
- `conciseness.py` — does the answer avoid unnecessary verbosity?
- `safety_risk_awareness.py` — does the answer flag safety/risk
  considerations (chemicals, dosage, weather, etc.) when relevant?
- `comparative_winner_reasoning.py` — a direct head-to-head comparison.

Weights are configured in `configs/metric_weights.yaml` and must sum to 1.0.

### Output

`src/export_results.py` writes, per row: a full execution trace, a clean
summary, and a context-impact-focused record (all as JSON under `outputs/`),
plus an aggregate `summary_results.csv` / `.xlsx` across the whole dataset.

## Tech stack

- Python, [LangGraph](https://www.langchain.com/langgraph) / [LangChain](https://www.langchain.com/) (`langchain_openai.ChatOpenAI`)
- Pandas / openpyxl for reading the input dataset and writing result tables
- PyYAML for metric-weight configuration
- pytest for tests (`test_metric_fusion.py`)
- Works against any OpenAI-compatible chat completion endpoint (the judge
  model and endpoint are configured in `JudgeClient`)

## Setup

```bash
pip install -r requirements.txt
```

Create a `.env` file with the API credentials for your LLM endpoint
(`OPENAI_API_KEY` is read by `src/judge_client.py`; the endpoint/model are
set where `JudgeClient` is constructed in `main.py`).

Input data is an Excel file with the columns `QUESTIONS`,
`ANSWERS GIVEN BY CHATBOT WITH MINIMUM CONTEXT`, and
`ANSWERS GIVEN BY AGRICULTURAL CHATBOT` (see `src/dataset_loader.py`).

## Usage

```bash
python main.py
```

This loads the configured dataset, runs every row through the agent graph,
prints a per-row summary (winner, confidence, context value score) to the
console, and writes detailed JSON/CSV/Excel output to `outputs/`.

Run tests with:

```bash
pytest
```

## License

MIT — see [LICENSE](LICENSE).
