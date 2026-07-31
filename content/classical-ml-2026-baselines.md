---
Title: The Baseline That Refuses to Die
Date: 2026-07-31 09:30
Category: AI
Tags:
- ml
- tabular
- foundation-models
- xgboost
- forecasting
- benchmarks
- gpu
Slug: classical-ml-2026-baselines
Author: Sam Reghenzi
Summary: For a decade, gradient-boosted trees owned tabular machine learning. In the last twelve months tabular foundation models finally — and decisively — beat them on TabArena. But the lesson practitioners are drawing ("stop using trees") is almost the opposite of what the evidence supports, because almost nobody runs the comparison correctly. A field guide to baselines, benchmarking discipline, and the GPU crunch in 2026.
---


For roughly a decade, tabular machine learning had a boring, reliable answer. Someone would hand you a CSV — churn labels, credit defaults, sensor readings, insurance claims — and you would reach for a gradient-boosted tree. XGBoost, LightGBM, or CatBoost. Every eighteen months a deep learning paper would claim to have finally beaten the trees, practitioners would find the comparison unfair, and boosting would keep its throne.

That era ended sometime in the last twelve months, and it ended more decisively than most people realize. But the conclusion practitioners are drawing from it — *stop using trees* — is close to the opposite of what the evidence supports.

---

## What actually changed

The venue for this argument is now TabArena, a living, Elo-rated benchmark over 51 curated tabular datasets with proper tuning protocols and repeated splits. It is the first tabular benchmark designed by people who had clearly been burned by bad tabular benchmarks.

On that board, tabular foundation models — pretrained transformers that do in-context learning over your rows, no gradient steps required — now hold every top single-model slot. In Prior Labs' own technical report, TabPFN-3 in its default configuration lands around 1677 Elo, with a "thinking" variant well above that; AutoGluon's four-hour multi-model ensemble pipeline sits at 1695. The best trees, tuned *and* post-hoc ensembled, come in around LightGBM 1440, CatBoost 1414, XGBoost 1387. On the small-data slice, the foundation model gets to a statistical tie with the four-hour AutoGluon pipeline in a single forward pass.

Then on June 30, 2026, Google Research released TabFM, a zero-shot tabular foundation model that also beats heavily tuned trees on TabArena — reportedly by solving the pretraining-data problem with large-scale synthetic table generation.

---

## The comparison nobody runs

Here is the uncomfortable part. Almost every team that has "evaluated foundation models against XGBoost" this year did not run a comparison. They ran a demo.

The typical version looks like this: load the dataset, call a foundation model's `predict`, compare against an XGBoost with roughly default hyperparameters and a single train/test split, observe that the foundation model wins by two points of AUC, and write it up. This is exactly the mistake the tabular deep learning literature spent 2021–2024 making in the other direction, and it is worth being precise about the failure modes, because they compound.

**Tuning budget parity.** The two families have asymmetric returns on tuning: a foundation model's default is often within noise of its tuned version, while a GBDT's default sits well below tuned, and tuned-plus-ensembled is another step above that. "50 Optuna trials each" hands one side a budget it cannot spend and the other side less than production practice. State the budget in wall-clock or dollars, and report defaults and tuned separately.

**Ensembling parity.** Post-hoc weighted ensembling of configurations is nearly free accuracy and it reorders tabular leaderboards. If the challenger's number is 32 blended forward passes and the tree's is one fitted model, you are comparing a committee to an individual. Ensemble both or neither.

**Split protocol and metric.** Single splits on 5–50k-row tables have standard deviations large enough to swallow every effect size in this debate: use repeated CV, multiple outer seeds, confidence intervals on everything. If the intervals overlap you have a preference, not a result. And drop accuracy — score AUC-PR on imbalanced problems, and log loss or Brier plus a reliability curve wherever downstream decisions consume the probabilities. Trees and pretrained transformers calibrate differently, and a better-ranking, worse-calibrated model can win your benchmark while costing you money.

**Pretraining contamination.** The most under-checked failure of the new regime. For a model pretrained on a large corpus of tables, "zero-shot performance on a public dataset" is a claim about leakage as much as about generalization — the forecasting community built explicit non-leaking splits into GIFT-Eval and now flags leaking models on the board precisely because this bit them. If you are benchmarking on `adult` or `covertype`, you are not measuring what you think. Evaluate on *your* data; it is the only evaluation that answers your actual question anyway.

**Cost as a first-class axis.** Plot accuracy against serving cost. The numbers that matter are training time per 1,000 samples, prediction latency per row at your concurrency, and whether inference needs a GPU. On published TabArena timings foundation models are far cheaper to *train* than a tuned tree sweep, and trees are far cheaper to *serve* — which dominates depends on your retraining cadence and request volume, and no leaderboard can tell you that.

**Where the gap comes from.** Aggregate Elo hides the mechanism, and the mechanism is documented: the advantage concentrates under data scarcity and complex interactions, and erodes or reverses on large, predominantly numeric tables. Pretrained models bring learned priors over table structure; boosting extracts dataset-specific signal iteratively. Given enough rows, the boosting exhausts the available signal and the prior stops adding anything. Benchmark work keeps converging on the same conclusion — performance is driven by *feature structure*, not model complexity or row count — and CatBoost remains the safest pick when categoricals dominate.

![DeltaW](/images/baselining-tabular-2026.png)

### A protocol worth actually running

If you want a defensible answer for your own problem, this takes an afternoon:

1. **Fix the harness before you look at any model.** Repeated stratified CV, ≥5 outer seeds, metrics derived from the downstream decision, confidence intervals mandatory.
2. **Establish the floor.** Logistic regression or a default random forest on your real preprocessing. Skipping this is how teams celebrate a foundation model that beat a broken pipeline — and a surprising number of "hard" problems turn out to be linear-plus-noise.
3. **Establish the reference.** LightGBM or CatBoost: defaults, then a fixed wall-clock tuning budget, then tuned-plus-ensembled. Three numbers, not one.
4. **Add the zero-shot challenger.** One forward pass from a tabular foundation model. Nearly free, and under ~10k rows it will often win outright.
5. **Plot the frontier, don't rank the models.** Metric against serving cost, then pick the point that fits your constraints rather than the top of a list.
6. **Score the non-quantitative axes explicitly.** Auditability, drift behaviour, retraining ergonomics, vendor dependency, deployability. Write them down as requirements before the numbers seduce you.

Step 6 is where foundation model pilots quietly die. In regulated settings — credit scoring, underwriting, clinical decision support — a documented GBDT with monotonic constraints, stable attributions, and a reproducible training run clears model risk review. A third-party pretrained transformer with opaque failure modes and a shifting version history is a much harder conversation, and you will have it again every time the vendor ships a checkpoint.

---

## Time series is a genuinely different story

The tabular argument and the forecasting argument get conflated constantly, and they should not be. In forecasting, the split is not old-versus-new — it is about whether you have history.

For true **zero-shot** forecasting, pretrained models have a structural advantage that trees cannot replicate. Chronos, TimesFM, Moirai-2, Sundial, and TabPFN-TS all forecast a series they have never seen. Moirai-2 ranks near the top of GIFT-Eval among non-leaking models, trained on tens of billions of observations across many domains. If you have forty thousand new series with no usable history and need something serving tomorrow, that is where you start, and it isn't close.

But when you have sufficient in-domain history, exogenous covariates — prices, promotions, weather, calendar effects, holidays — and a hierarchy to reconcile, feature-engineered gradient boosting remains competitive and often better. The M5 pattern (one global GBDT over lag and calendar features across all series) has not been dethroned by anything for that class of problem. One striking data point: when Google DeepMind pointed an automated code-search system at GIFT-Eval, it outperformed the entire leaderboard — foundation models included — and the solutions it discovered converged strongly on gradient boosting and ensemble/decomposition methods. An unbiased search over the space of forecasting approaches walked toward boosting.

Recent work frames this as a break-even analysis rather than a ranking, which is the right frame: foundation models need GPU infrastructure, have opaque failure modes, and can underperform on highly domain-specific data, while boosting and classical smoothing methods are interpretable, run on CPUs, and carry decades of empirical validation. The break-even point is essentially a function of how much relevant history you have per series.

---

## The constraint nobody budgeted for

There is an unglamorous reason this matters more in 2026 than it would have in 2024: GPUs are not a commodity you can assume.

The 2026 crunch is not one shortage but a stack of them — HBM, CoWoS packaging, wafer capacity, data center power, cloud allocation — all tight at once. Data-center GPU lead times are reported at 36 to 52 weeks, hyperscalers have locked up much of the allocation on multi-year commitments, and teams shut out of reserved pools land on on-demand pricing at multiples of budget. In some regions the binding constraint has shifted again, to grid interconnection.

This is not an argument that foundation models are bad. It is an argument that "needs a GPU at inference time" is a line item with scarcity risk attached, currently priced by the market rather than by your infra team. A model that serves at microsecond latency on CPUs you already own carries option value that appears in no accuracy table. If your churn model is a LightGBM on commodity hardware, capacity planning is solved; if it needs an accelerator per replica, you are competing for allocation against every LLM workload in your company — and losing.

---

## So: what do you actually do

Keep a GBDT — LightGBM or CatBoost — as a mandatory baseline, permanently. Not out of nostalgia, but because it is the instrument that tells you whether your problem is hard or whether you are making it hard. It trains on a laptop, it tells you which features matter, and it will catch the leakage in your pipeline before a foundation model launders it into a suspiciously good score.

Add a zero-shot tabular foundation model as a second free shot. On small and medium tables it frequently wins with no tuning and the cost of finding out is one forward pass. Treat it as a strong candidate, not a replacement.

Random forests specifically occupy narrower ground than XGBoost does. They remain worth having for immediate baselining, for quantile-based uncertainty estimates, for small noisy datasets where boosting overfits, and as ensemble members. They are rarely the final answer any more.

And then decide on your data, with your metric, at your cost point — not on a leaderboard. The frontier is moving fast enough that any specific recommendation here has a shelf life of about two quarters. The evaluation discipline does not.

---

### Sources

- TabArena: A Living Benchmark for Machine Learning on Tabular Data — https://arxiv.org/pdf/2506.16791 · live board: https://tabarena.ai
- TabPFN-3 Technical Report (leaderboard tables, timings) — https://arxiv.org/pdf/2605.13986
- Hollmann et al., "Accurate predictions on small data with a tabular foundation model," *Nature* 637
- Google TabFM release coverage and the ensembling caveat — https://ai-crucible.com/articles/tabfm-ensembling-wins-even-for-tables/
- Tabular model benchmark across 19 datasets (feature-structure findings) — https://aimultiple.com/tabular-models
- GIFT-Eval: A Benchmark for General Time Series Forecasting Model Evaluation — https://arxiv.org/abs/2410.10393
- "When Do Foundation Models Pay Off? A Break-Even Analysis of Pretrained Time Series Forecasters" — https://arxiv.org/html/2607.04919v1
- "An AI system to help scientists write expert-level empirical software" (GIFT-Eval result converging on gradient boosting) — https://arxiv.org/pdf/2509.06503
- Schmitt, "Deep Learning vs. Gradient Boosting: benchmarking for credit scoring" — https://arxiv.org/pdf/2205.10535
- GPU and compute supply constraints, 2026 — https://www.apollo.com/wealth/insights-news/insights/2026/06/growing-compute-shortage · https://vexxhost.com/blog/gpu-capacity-crisis-ai-infrastructure-2026/ · https://inflect.com/blog/data-center-power-shortage-2026-why-grid-capacity-is-now-the-bigger-constraint-than-gpus
