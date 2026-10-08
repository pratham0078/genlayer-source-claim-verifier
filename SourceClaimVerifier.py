# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *
import json
import typing


class SourceClaimVerifier(gl.Contract):
    """
    Reusable GenLayer primitive for source-grounded claim verification.
    Validators independently repeat the verification and must agree
    on the substantive verdict.
    """

    results: TreeMap[str, str]

    def __init__(self):
        pass

    @gl.public.write
    def verify_claim(
        self,
        claim_id: str,
        claim: str,
        source_url: str
    ) -> typing.Any:

        if not claim_id:
            raise gl.vm.UserError("claim_id cannot be empty")

        if not claim:
            raise gl.vm.UserError("claim cannot be empty")

        if not (
            source_url.startswith("http://")
            or source_url.startswith("https://")
        ):
            raise gl.vm.UserError(
                "source_url must use http:// or https://"
            )

        def leader_fn():
            response = gl.nondet.web.get(source_url)
            source_text = response.body.decode("utf-8")

            prompt = f"""
You are a source-grounded claim verification agent.

Determine whether the CLAIM is supported by the SOURCE CONTENT.

CLAIM:
{claim}

SOURCE CONTENT:
{source_text}

Return ONLY valid JSON:

{{
  "verdict": "TRUE",
  "evidence": "short evidence from the source",
  "reason": "brief explanation"
}}

Allowed verdicts:
TRUE
FALSE
INCONCLUSIVE

Rules:
1. Use only information in the supplied source.
2. Do not use outside knowledge.
3. Do not assume missing facts.
4. Return INCONCLUSIVE when evidence is insufficient.
"""

            raw = gl.nondet.exec_prompt(prompt)
            return json.loads(raw)

        def validator_fn(leader_result) -> bool:
            if not isinstance(leader_result, gl.vm.Return):
                return False

            validator_data = leader_fn()
            leader_data = leader_result.calldata

            if not isinstance(leader_data, dict):
                return False

            if not isinstance(validator_data, dict):
                return False

            allowed = {
                "TRUE",
                "FALSE",
                "INCONCLUSIVE",
            }

            leader_verdict = leader_data.get("verdict")
            validator_verdict = validator_data.get("verdict")

            if leader_verdict not in allowed:
                return False

            if validator_verdict not in allowed:
                return False

            return leader_verdict == validator_verdict

        result = gl.vm.run_nondet_unsafe(
            leader_fn,
            validator_fn
        )

        self.results[claim_id] = json.dumps(
            {
                "claim_id": claim_id,
                "claim": claim,
                "source_url": source_url,
                "verdict": result["verdict"],
                "evidence": result.get("evidence", ""),
                "reason": result.get("reason", ""),
            },
            sort_keys=True
        )

        return result["verdict"]

    @gl.public.view
    def get_result(self, claim_id: str) -> str:
        return self.results[claim_id]
