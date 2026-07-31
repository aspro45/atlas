# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
"""
ATLAS - AI-Verified Places Registry
===================================
A living map. Anyone drops a pin: a place name, a description and a public
source that documents it. To confirm a pin, the contract reads the source and a
validator set decides (Equivalence Principle) whether the place is real and
matches the claim. Verified pins glow; rejected myths stay grey. Coordinates are
stored as strings so signed/fractional values are exact and on-chain.

Status: PENDING(0) -> VERIFIED(1) | REJECTED(2)
"""

from genlayer import *
from dataclasses import dataclass
import json
import typing


PENDING = 0
VERIFIED = 1
REJECTED = 2


@allow_storage
@dataclass
class Place:
    submitter: Address
    name: str
    description: str
    category: str
    lat: str
    lng: str
    proof_url: str
    status: u8
    rationale: str


class Atlas(gl.Contract):
    places: DynArray[Place]

    def __init__(self) -> None:
        pass

    @gl.public.write
    def add_place(self, name: str, description: str, category: str, lat: str, lng: str, proof_url: str) -> int:
        if len(name.strip()) == 0:
            raise gl.vm.UserError("a name is required")
        if len(description.strip()) == 0:
            raise gl.vm.UserError("a description is required")
        if len(proof_url.strip()) == 0:
            raise gl.vm.UserError("a source URL is required")
        if not self._is_num(lat) or not self._is_num(lng):
            raise gl.vm.UserError("latitude and longitude must be numbers")
        p = self.places.append_new_get()
        p.submitter = gl.message.sender_address
        p.name = name
        p.description = description
        p.category = category if len(category.strip()) else "landmark"
        p.lat = lat
        p.lng = lng
        p.proof_url = proof_url
        p.status = u8(PENDING)
        p.rationale = ""
        return len(self.places) - 1

    @gl.public.write
    def verify(self, place_id: int) -> None:
        """Read the source; validators agree whether the place is real and matches."""
        p = self._get(place_id)
        if p.status != PENDING:
            raise gl.vm.UserError("this pin is already settled")

        name = p.name
        desc = p.description
        lat = p.lat
        lng = p.lng
        url = p.proof_url

        def leader_fn() -> str:
            page = ""
            try:
                page = gl.nondet.web.get(url).body.decode("utf-8")[:6000]
            except Exception:
                page = "(source unreachable)"
            prompt = (
                f"A contributor pinned a place on a map.\n"
                f"Name: {name}\n"
                f"Description: {desc}\n"
                f"Coordinates: {lat}, {lng}\n\n"
                f"Source document:\n{page}\n\n"
                "Based strictly on the source, is this a REAL, existing place that "
                "matches the name and description? Treat myths, legends and fiction "
                "as not real. Reply with ONLY JSON: {\"verified\": true} or "
                "{\"verified\": false}, plus a short \"reason\"."
            )
            return gl.nondet.exec_prompt(prompt)

        def validator_fn(leader_res) -> bool:
            if not isinstance(leader_res, gl.vm.Return):
                return False
            return self._decision_of(leader_res.calldata)[0] == self._decision_of(leader_fn())[0]

        result = gl.vm.run_nondet_unsafe(leader_fn, validator_fn)
        ok, reason = self._decision_of(result)
        p.rationale = reason[:300]
        p.status = u8(VERIFIED) if ok else u8(REJECTED)

    # ------------------------------------------------------------------ views
    @gl.public.view
    def get_place_count(self) -> int:
        return len(self.places)

    @gl.public.view
    def get_place(self, place_id: int) -> dict:
        p = self._get(place_id)
        return {
            "submitter": p.submitter.as_hex,
            "name": p.name,
            "description": p.description,
            "category": p.category,
            "lat": p.lat,
            "lng": p.lng,
            "proof_url": p.proof_url,
            "status": int(p.status),
            "rationale": p.rationale,
        }

    # -------------------------------------------------------------- internals
    def _get(self, place_id: int) -> Place:
        if place_id < 0 or place_id >= len(self.places):
            raise gl.vm.UserError("no such place")
        return self.places[place_id]

    def _is_num(self, s: str) -> bool:
        try:
            float(s)
            return True
        except (ValueError, TypeError):
            return False

    def _decision_of(self, result: typing.Any) -> tuple:
        data = result
        if isinstance(data, str):
            data = self._extract_json(data)
        if not isinstance(data, dict):
            return (False, "")
        raw = data.get("verified", None)
        reason = str(data.get("reason", ""))
        if isinstance(raw, bool):
            return (raw, reason)
        if isinstance(raw, str):
            return (raw.strip().lower() == "true", reason)
        return (False, reason)

    def _extract_json(self, text: str) -> typing.Any:
        try:
            return json.loads(text)
        except (ValueError, TypeError):
            pass
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start:end + 1])
            except (ValueError, TypeError):
                return None
        return None
