"""Executable Atlas V2 permissions and review-lifecycle tests."""

import json
from pathlib import Path


CONTRACT = str(Path(__file__).resolve().parents[1] / "contracts" / "atlas_v2.py")


def _deploy_record(deploy, vm, owner):
    vm.sender = owner
    contract = deploy(CONTRACT)
    record_id = contract.create_place("Rabat tower", "A documented public landmark", "landmark", "34.0209", "-6.8416", "https://example.com")
    return contract, str(record_id)


def _mock_review(vm):
    vm.mock_llm(
        r"Atlas V2, a GenLayer",
        json.dumps({
            "verdict": "verified",
            "outcomeStatus": "verified",
            "score": 86,
            "confidenceBps": 8500,
            "accuracyBps": 8400,
            "authenticityBps": 8600,
            "priorityStrengthBps": 8100,
            "coordinateMatchBps": 9000,
            "existenceBps": 9100,
            "feasibilityBps": 8200,
            "marketBps": 7600,
            "executionRiskBps": 2100,
            "supportBps": 8700,
            "edgeConsistencyBps": 8300,
            "summary": "Public evidence supports the reviewed record.",
            "publicSummary": "Public evidence supports the reviewed record.",
            "rationale": "The independent source and record align.",
            "reasoningDigest": "Source-backed review completed.",
            "recommendedNextStep": "finalize_after_review",
            "riskFlags": [],
            "sourceScores": [],
            "sourceCredibility": [],
            "signalCredibility": [],
            "supportingSignalIds": [],
            "contradictingSignalIds": [],
            "supportingCitationIds": [],
            "conflictingCitationIds": [],
            "supportingEvidenceIds": [],
            "conflictingEvidenceIds": [],
            "contradictionIds": [],
            "revisionRisks": [],
            "missingEvidence": [],
        }),
    )


def _mock_ruling(vm, pattern, ruling, revised):
    vm.mock_llm(
        pattern,
        json.dumps({
            "ruling": ruling,
            "revisedVerdict": revised,
            "confidenceDeltaBps": -1100 if revised == "rejected" else 900,
            "scoreDelta": -20 if revised == "rejected" else 18,
            "reason": "The filing provides controlling public evidence.",
            "reasoningDigest": "The reviewed outcome was revised.",
            "riskFlags": [],
        }),
    )


def test_owner_and_protocol_permissions_execute(
    deploy, direct_vm, direct_alice, direct_bob
):
    contract, record_id = _deploy_record(deploy, direct_vm, direct_alice)

    direct_vm.sender = direct_bob
    with direct_vm.expect_revert("admin_only"):
        contract.set_atlas_standard("A controlled mapping standard")

    direct_vm.sender = direct_bob
    with direct_vm.expect_revert("record_operator_only"):
        contract.add_source(record_id, "https://example.org", "registry", "Independent place source")
    with direct_vm.expect_revert("record_operator_only"):
        contract.review_place_with_genlayer(record_id)


def test_challenge_and_appeal_revise_record_before_finalization(
    deploy, direct_vm, direct_alice, direct_bob
):
    contract, record_id = _deploy_record(deploy, direct_vm, direct_alice)
    direct_vm.sender = direct_alice
    _mock_review(direct_vm)
    contract.review_place_with_genlayer(record_id)
    contract.open_challenge_window(record_id)

    direct_vm.sender = direct_bob
    challenge_id = contract.submit_challenge(
        record_id,
        "A newer source contradicts the reviewed result.",
        "https://example.org/challenge",
    )

    direct_vm.sender = direct_alice
    with direct_vm.expect_revert("open_filing_blocks_finalize"):
        contract.finalize_place(record_id)

    _mock_ruling(direct_vm, r"Atlas V2 challenge", "accepted", "rejected")
    contract.resolve_challenge_with_genlayer(record_id, challenge_id)
    record = json.loads(contract.get_place_record(record_id))
    assert record["verdict"] == "rejected"

    direct_vm.sender = direct_bob
    appeal_id = contract.submit_appeal(
        record_id,
        "A final publication restores the original result.",
        "https://example.net/appeal",
    )

    direct_vm.sender = direct_alice
    with direct_vm.expect_revert("open_filing_blocks_finalize"):
        contract.finalize_place(record_id)

    _mock_ruling(direct_vm, r"Atlas V2 appeal", "granted", "verified")
    contract.resolve_appeal_with_genlayer(record_id, appeal_id)
    contract.finalize_place(record_id)

    record = json.loads(contract.get_place_record(record_id))
    assert record["status"] == "FINALIZED"
    assert record["verdict"] == "verified"
    assert record["challengeIds"] == [challenge_id]
    assert record["appealIds"] == [appeal_id]
