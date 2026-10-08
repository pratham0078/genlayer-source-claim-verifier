# SourceClaimVerifier

A reusable GenLayer Intelligent Contract primitive for decentralized,
source-grounded claim verification.

## Purpose

SourceClaimVerifier lets an application submit a claim and a source URL.
GenLayer validators independently analyze the source and must agree on
the substantive verdict.

## Verdicts

- TRUE: the source supports the claim.
- FALSE: the source contradicts the claim.
- INCONCLUSIVE: the source does not contain enough evidence.

## Consensus design

The leader retrieves the source and produces a structured result.
Validators independently repeat the source-grounded analysis.

Consensus is based on the meaningful `verdict` field rather than exact
natural-language wording. This is intentional: two validators can reach
the same conclusion while writing different evidence or explanations.

## Reusable use cases

- source and news verification
- DAO governance evidence checks
- document verification
- agent-to-agent verification
- research workflows
- prediction-market resolution helpers
- policy and compliance checks

## Safety considerations

The source itself is not automatically truthful. Applications should
consider source reputation, changing web content, malicious webpages,
prompt injection, and the consequences of an INCONCLUSIVE result.

## Testing

Run fast unit tests in Direct Mode and consensus/integration tests in
GenLayer Studio before deployment.
