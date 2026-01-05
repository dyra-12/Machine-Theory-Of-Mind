# Limitations and Scope Boundaries

This repository presents a methodological and theoretical proof-of-concept for belief-based social reasoning in artificial agents. The limitations described below reflect **intentional scope boundaries** chosen to isolate core mechanisms, rather than shortcomings of the proposed framework.

---

## 1. Stylized Interaction Environment

The negotiation environment used in this work is intentionally simplified:

- Interactions are short-horizon and structured
- Action spaces are discrete and fully enumerable
- Observer behavior is controlled rather than learned from humans

### Rationale
This design isolates the effects of belief-based social inference without confounding factors such as language generation, long-term strategy learning, or dataset bias. Richer environments may introduce additional sources of variance that obscure the contribution of social belief modeling.

### Implication
The results demonstrate **mechanistic plausibility and structured trade-offs**, not direct readiness for deployment in complex real-world settings.

---

## 2. Simulated Observer Models

Social perception is modeled using simulated observer functions rather than data-driven human models:

- Observers map actions to perceived warmth and competence
- Normative preferences are explicitly parameterized
- Adversarial and noisy observers are synthetically defined

### Rationale
This choice enables controlled experimentation and reproducibility while allowing systematic stress-testing of belief updates under norm shifts and adversarial feedback.

### Implication
The framework is **observer-agnostic by design**; replacing simulated observers with learned or human-grounded models is a natural extension rather than a conceptual limitation.

---

## 3. Greedy Decision-Making Without Policy Learning

The MToM agent does not learn a parametric policy:

- Actions are evaluated locally at each decision step
- Adaptation arises from belief updates, not weight optimization
- No long-horizon planning or policy gradients are used

### Rationale
This separation ensures that observed behavioral adaptation can be attributed to social inference dynamics, not implicit learning effects.

### Implication
While policy learning could improve efficiency in larger state spaces, it would reduce interpretability and complicate attribution. Integrating MToM with learned policies remains an **open research direction**.

---

## 4. Diagnostic Evaluation Metrics

The Social Intelligence Quotient (SIQ) is used exclusively as a post hoc evaluation metric:

- SIQ is not optimized during decision-making
- Components are computed from interaction traces
- Weights reflect evaluative priorities rather than normative prescriptions

### Rationale
Treating SIQ diagnostically prevents reward hacking and preserves its role as an interpretive tool rather than a behavioral objective.

### Implication
SIQ should be understood as a **comparative lens** for analyzing social behavior, not a universal or exhaustive measure of social intelligence.

---

## 5. Scale of Human Evaluation

The human-in-the-loop study is intentionally a pilot evaluation:

- Sample size is modest (N = 25)
- Interactions are text-based and short
- No demographic stratification is performed

### Rationale
The pilot is designed to validate **perceptual relevance**—whether belief-based social reasoning produces human-noticeable effects—rather than to establish population-level generalization.

### Implication
The observed perceptual gains motivate larger, demographically diverse studies, but do not constitute definitive human-subject validation.

---

## 6. Scope of Ethical Claims

This work does not claim to enforce ethical behavior or fairness guarantees:

- Ethical consistency is evaluated diagnostically
- No hard constraints are imposed during action selection
- Normative judgments are context-dependent

### Rationale
Encoding ethics as rigid constraints risks masking trade-offs and undermining transparency. The present framework emphasizes **analysis over enforcement**.

### Implication
Ethical alignment remains a multi-dimensional problem; MToM contributes tools for reasoning about social perception rather than solving normative ethics.

---

## 7. Generalization Beyond the Studied Domain

Generalization is evaluated across structured environment variants but not across radically different task domains.

### Rationale
The focus is on validating the mechanism of belief-conditioned social reasoning rather than task-specific transfer performance.

### Implication
Applying MToM to language-based, embodied, or multi-party interaction settings is a **promising direction for future work**.

---

## Summary

The limitations outlined above reflect **deliberate modeling and evaluation choices** intended to maximize interpretability, reproducibility, and theoretical clarity. Within this scoped setting, the results provide strong evidence that explicit belief-based modeling of social perception yields structured, analyzable, and human-relevant social behavior.

### Future Directions

Future work will extend this framework to:

- Richer environments
- Learned observer models
- Longer-term human interaction

Building on the methodological foundations established here.