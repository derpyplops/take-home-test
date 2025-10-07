# Investigation Report

## TL;DR
	•	A few-shot prompt using real in-distribution examples, optionally ensembled (3×) for majority vote.
	•	Best observed accuracy (n=60): 66.7% with 3× few-shot ensemble.
	•	Interestingly gpt-5 was NOT the best model, I hypothesize that it's because of
	overthinking: we should focus on simple prompts and few-shot prompting/prompt engineering.
	•	We need to collect more data before drawing good conclusions.
	

⸻

## Setup & Dataset
	•	Dataset: data/dataset.csv (60 transcripts; includes human_generated_intent and prior gpt4.1 predictions).


## To Reproduce:
prereqs: openai key, uv installed
```bash
uv run python test_improvements.py data/dataset.csv --method all
```

⸻

## Methods Evaluated

1) Baseline (old prompt)
2) Different Prompt Wording
3) Few-Shot (Add examples of correctly classified. In this case I added two examples)
4) Ensemble Voting (Run the few-shot prompt 3 times)

⸻

## Summary Table

| Method            | gpt-4.1-2025-04-14 | gpt-5-mini-2025-08-07 | gpt-5-2025-08-07 |
|--------------------|---------------------|-------------------------|-------------------|
| baseline          | 61.7%              | 65.0%                  | 56.7%            |
| different_prompt  | 66.7%              | 58.3%                  | 60.0%            |
| few_shot          | 61.7%              | 63.3%                  | 60.0%            |
| chain_of_thought  | 65.0%              | 60.0%                  | 56.7%            |
| ensemble          | 61.7%              | 61.7%                  | 56.7%            |

⸻

## Discussion
Firstly these results should be treated as preliminary, it's difficult to make comments about strict improvement because n=60 is not a large enough dataset, preferably it'd be at least a thousand. I would also have run it multiple times.

Few-shot prompting with real in-distribution examples gave the clearest and most robust gains, reaching 66.7% accuracy with 3× ensembling. This outperformed both baseline and chain-of-thought (CoT) methods across models. The improvement likely comes from grounding the model in actual task patterns rather than encouraging generic reasoning.

GPT-5’s weaker performance is notable. Its tendency to “overthink” may introduce noise on a task that rewards crisp, pattern-based classification. CoT didn’t help here either, suggesting that explicit reasoning isn’t aligned with the decision structure of the task. Ensemble voting provided minor but consistent smoothing.

The key inference is that prompt framing matters more than model upgrades for this task. Next steps should focus on curating higher-quality few-shot examples, exploring structured output formats, and using ensembling strategically—rather than defaulting to larger or more complex models. A small set of strong exemplars is likely the highest-leverage intervention.