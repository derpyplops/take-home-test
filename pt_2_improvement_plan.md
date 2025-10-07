## Summary

The 4-week plan can be broken down into 3 sections that can mostly be parallelized
1. Improving Classification Accuracy
2. Decreasing oversight cost
3. Investigating third party solutions

Assumptions:
- We have an infinite budget. 
- No adding more intents
- intent definitions are correct
### Improving Classification Accuracy

This part is generally the most straightforward.

Try improving the classifier:
- try **different prompts** wordings to elicit better performance
- try few-shot prompting: adding more concrete examples
- try asking the model to **think more**
	- use gpt5 instead of gpt4.1
- try **ensembling**:
	- use 3 different prompts / models, ask them to vote.

Test all the approaches on a suitably large test set, the current one is too small.

### Decreasing Oversight Cost

We can decrease oversight cost by only reviewing the most suspicious or the most dangerous classifications. 

#### Uncertainty

We can use a heuristic for uncertainty. Some prospective methods:
1. asking the model to output uncertainty
2. if using ensemble, we can use disagreement as a proxy for uncertainty

By using any of these methods, we can audit only the top N responses where N is our human auditing budget.

#### Dangerousness

We also introduce a notion that some follow-up actions have worse potential consequences. Map each intent to a follow-up **risk tier** and require different confidence + evidence rules:

- **Tier A (lowest risk, reversible):** “email/WhatsApp/SMS follow-up,” “send info pack.”
- **Tier B (medium):** “call back” at a specific time, “wrong number” updates.
- **Tier C (high, state-changing):** “not interested,” “no action needed,” “immediate hangup,” “voicemail.”

Then set a **budgeted triage** target: e.g., “≤20% manual review.” Then, either manually or automatically adjust thresholds weekly to hit the budget while keeping a post-hoc sampled error rate under a cap (e.g., <1% for auto-executed actions).

This is a good observability metric: on the x-axis we have the accuracy (% correctly classified) and on the y-axis we use % audited.

### Third Party

We should also investigate third party solutions to see if any of them work out of the box for our purposes. Google Dialogflow CX seems promising.

### Time budgeting

Given 4 weeks (20 man hours) to do this, I would suggest spending
2 weeks on improvement
1 week on decreasing cost
0.5 weeks researching alternatives
0.5 weeks buffer time