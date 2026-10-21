"""LLM-guided PET-MAD pilot: LiNbF6 reference plus two prospective choices (LLM_PETMAD_PILOT_PLAN.md).

The LLM owns the next-material choice and a testable prediction; deterministic code owns menu
eligibility, feedback validation, information boundaries and accounting. State is a JSON file so the
loop can stop while physics is pending and resume later. Field contract: PILOT_CONTRACT.md.
"""
from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

PILOT_VERSION = "llm_petmad_pilot_v1"
STAGES = ("prior", "choose_2", "choose_3", "summary")
CONTACTS = ("cathode", "electrolyte")
RUN_STATUSES = {"valid", "failed", "pending"}
THERMO_FIELDS = ("penalty", "penalty_bin", "acceptable", "insulating", "band_gap_eV")
WEAK_TOLERANCE_J_M2 = 0.1     # reporting convention for "unresolved" weak contact, not an uncertainty
HTTP_ATTEMPT_CAP = 10
MAX_FORMAT_ATTEMPTS = 2       # per stage; every attempt is charged against the HTTP cap
MAX_HTTP_PER_CALL = 3         # make_llm default retries: worst-case HTTP attempts inside one call

SYSTEM_PROMPT = """You are a battery materials scientist choosing which coating to evaluate next with an
interatomic-potential (PET-MAD) interface calculation. Coatings sit between a LiCoO2 cathode and a Li6PS5Cl
electrolyte at 4 V. The fixed brief: favourable trade-offs between the frozen thermodynamic penalty (lower is
better) and the weaker of the two validated contact adhesion works W_adh (higher is better). Strong adhesion
cannot make a thermodynamically rejected coating acceptable. Use only the candidate cards and the feedback
you are shown; do not invent computed values. Answer with one JSON object in the requested schema."""


class Pending(Exception):
    """Required feedback is not yet terminal; save state and resume later."""


def digest(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def _finite(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def load_index(path):
    """Physical campaign index written by the PET-MAD side (schema in PILOT_CONTRACT.md)."""
    index = json.loads(Path(path).read_text())
    problems, seen = [], set()
    for key in ("schema_version", "checkpoint_sha256", "menu", "runs"):
        if key not in index:
            problems.append(f"index missing {key}")
    menu_ids = {c["candidate_id"] for c in index.get("menu", [])}
    for r in index.get("runs", []):
        rid = r.get("run_id")
        if rid in seen:
            problems.append(f"duplicate run_id {rid}")
        seen.add(rid)
        if r.get("candidate_id") not in menu_ids:
            problems.append(f"{rid}: candidate not in menu")
        if r.get("contact") not in CONTACTS or r.get("role") not in ("primary", "sensitivity"):
            problems.append(f"{rid}: bad contact/role")
        if r.get("status") not in RUN_STATUSES:
            problems.append(f"{rid}: bad status {r.get('status')!r}")
        if r.get("checkpoint_sha256") != index.get("checkpoint_sha256"):
            problems.append(f"{rid}: checkpoint differs from the campaign checkpoint")
        if r.get("status") == "valid" and not (_finite(r.get("W_adh_J_m2")) and _finite(r.get("joined_energy_eV"))):
            problems.append(f"{rid}: valid run without finite W_adh/joined energy")
        if r.get("status") == "failed" and not r.get("failure_reason"):
            problems.append(f"{rid}: failed run without failure_reason")
        if r.get("status") != "valid" and r.get("W_adh_J_m2") is not None:
            problems.append(f"{rid}: non-valid run carries a W_adh")
    if problems:
        raise ValueError("Invalid campaign index:\n  " + "\n  ".join(problems))
    return index


def thermo_card(table, candidate_id):
    row = next((r for r in table["results"] if r["candidate_id"] == candidate_id), None)
    if row is None:
        raise ValueError(f"{candidate_id} not in the frozen thermodynamic table")
    return {k: row.get(k) for k in THERMO_FIELDS}


def feedback_bundle(index, table, candidate_id):
    """Frozen primary feedback for one evaluated coating. Sensitivity values are withheld (pending)."""
    card = next(c for c in index["menu"] if c["candidate_id"] == candidate_id)
    runs = [r for r in index["runs"] if r["candidate_id"] == candidate_id]
    contacts = {}
    for contact in CONTACTS:
        primary = [r for r in runs if r["contact"] == contact and r["role"] == "primary"]
        if not primary or any(r["status"] == "pending" for r in primary):
            raise Pending(f"{candidate_id} {contact}: primary runs not terminal")
        valid = [r for r in primary if r["status"] == "valid"]
        chosen = min(valid, key=lambda r: r["joined_energy_eV"]) if valid else None  # frozen lowest-joined-energy rule
        contacts[contact] = dict(
            status="valid" if chosen else "failed", selected_run_id=chosen and chosen["run_id"],
            W_adh_J_m2=chosen and chosen["W_adh_J_m2"], W_sep_J_m2=chosen and chosen.get("W_sep_J_m2"),
            registries=[dict(run_id=r["run_id"], registry=r.get("registry"), status=r["status"],
                             W_adh_J_m2=r.get("W_adh_J_m2"), failure_reason=r.get("failure_reason")) for r in primary],
            warnings=sorted({w for r in primary for w in r.get("warnings", [])}))
    w = {c: contacts[c]["W_adh_J_m2"] for c in CONTACTS}
    both = all(v is not None for v in w.values())
    weaker = ("unresolved" if not both or abs(w["cathode"] - w["electrolyte"]) < WEAK_TOLERANCE_J_M2
              else min(CONTACTS, key=lambda c: w[c]))
    return dict(candidate_id=candidate_id, formula=card["formula"], thermo=thermo_card(table, candidate_id),
                contacts=contacts, weaker_contact=weaker, min_W_adh_J_m2=min(w.values()) if both else None,
                sensitivity=[dict(run_id=r["run_id"], contact=r["contact"], kind=r.get("sensitivity_kind"),
                                  status="pending") for r in runs if r["role"] == "sensitivity"],
                cost=dict(calculator_calls=sum(r.get("calculator_calls") or 0 for r in runs),
                          wall_seconds=sum(r.get("wall_seconds") or 0 for r in runs)),
                limitations=card.get("limitations", []))


def validate_decision(stage, response, remaining):
    """Check one parsed LLM response; raise ValueError with a reason the model can act on."""
    if not isinstance(response, dict):
        raise ValueError("Return one JSON object")
    if stage == "summary":
        if not isinstance(response.get("summary"), str) or not response["summary"].strip():
            raise ValueError("Return {'summary': str}")
        return response
    shortlist = response.get("ordered_shortlist")
    if (not isinstance(shortlist, list) or len(shortlist) != len(set(shortlist))
            or set(shortlist) != set(remaining)):
        raise ValueError(f"ordered_shortlist must rank exactly these unevaluated IDs once: {sorted(remaining)}")
    if not isinstance(response.get("hypothesis"), str) or not response["hypothesis"].strip():
        raise ValueError("Each decision needs a nonempty hypothesis")
    if stage == "prior":
        return response
    if response.get("selected_id") != shortlist[0]:
        raise ValueError("selected_id must be the first ID of ordered_shortlist")
    if response.get("predicted_weaker_contact") not in (*CONTACTS, "unresolved"):
        raise ValueError("predicted_weaker_contact must be cathode, electrolyte or unresolved")
    ranges = response.get("predicted_W_adh_J_m2")
    for c in CONTACTS:
        r = (ranges or {}).get(c)
        if not (isinstance(r, list) and len(r) == 2 and all(_finite(x) for x in r) and 0 <= r[0] <= r[1] <= 20):
            raise ValueError(f"predicted_W_adh_J_m2.{c} must be [low, high] in J/m2 with 0 <= low <= high <= 20")
    if not isinstance(response.get("change_trigger"), str) or not response["change_trigger"].strip():
        raise ValueError("change_trigger must name an observation that would change the next choice")
    if stage == "choose_3" and not (isinstance(response.get("supporting_observations"), list)
                                    and response["supporting_observations"]):
        raise ValueError("supporting_observations must cite the specific feedback behind this choice")
    return response


OUTPUT_SCHEMA = {
    "prior": '{"ordered_shortlist": [ids], "hypothesis": str}',
    "choose_2": ('{"ordered_shortlist": [ids], "selected_id": first id, "hypothesis": str, '
                 '"predicted_weaker_contact": "cathode"|"electrolyte"|"unresolved", '
                 '"predicted_W_adh_J_m2": {"cathode": [low, high], "electrolyte": [low, high]}, "change_trigger": str}'),
    "choose_3": ('{"ordered_shortlist": [ids], "selected_id": first id, "hypothesis": str, '
                 '"predicted_weaker_contact": "cathode"|"electrolyte"|"unresolved", '
                 '"predicted_W_adh_J_m2": {"cathode": [low, high], "electrolyte": [low, high]}, '
                 '"change_trigger": str, "supporting_observations": [str]}'),
    "summary": '{"summary": str}',
}


class Pilot:
    """Resumable state machine. One instance per state file; every stage record is hashed and kept."""

    def __init__(self, state_path, index_path, table_path, *, reference_id, http_cap=HTTP_ATTEMPT_CAP,
                 max_http_per_call=MAX_HTTP_PER_CALL, allow_small_menu=False, include_prior=True):
        self.path, self.index_path, self.table_path = Path(state_path), Path(index_path), Path(table_path)
        self.table = json.loads(self.table_path.read_text())
        if self.path.exists():
            self.state = json.loads(self.path.read_text())
            return
        index = load_index(self.index_path)
        feasible = [c["candidate_id"] for c in index["menu"] if c.get("feasible")]
        if reference_id not in feasible:
            raise ValueError("Reference must be a feasible menu item")
        if len(feasible) - 1 < 3 and not allow_small_menu:
            raise ValueError(f"Only {len(feasible) - 1} unevaluated alternatives; report before live calls")
        self.state = dict(
            pilot_version=PILOT_VERSION, created_at=_now(), reference_id=reference_id, feasible=feasible,
            menu_sha256=digest(index["menu"]), table_sha256=self.table["sha256"], http_cap=http_cap,
            max_http_per_call=max_http_per_call,
            http_attempts_used=0, stages=[], evaluated=[reference_id], selected=[],
            plan=[s for s in STAGES if include_prior or s != "prior"], status="running")
        self._save()

    def _save(self):
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.state, indent=2, allow_nan=False))
        tmp.replace(self.path)

    def next_stage(self):
        done = {s["stage"] for s in self.state["stages"] if s.get("parsed") is not None or s.get("failed")}
        return next((s for s in self.state["plan"] if s not in done), None)

    def _cards(self, index):
        return [dict(candidate_id=c["candidate_id"], formula=c["formula"], thermo=thermo_card(self.table, c["candidate_id"]),
                     descriptors=c.get("descriptors", {}), limitations=c.get("limitations", []))
                for c in index["menu"] if c["candidate_id"] in self.state["feasible"]]

    def _revealed(self, index, stage):
        """Coatings whose feedback this stage may see; raises Pending until each is terminal."""
        upto = {"prior": [], "choose_2": [self.state["reference_id"]],
                "choose_3": [self.state["reference_id"], *self.state["selected"][:1]],
                "summary": [self.state["reference_id"], *self.state["selected"][:2]]}[stage]
        return [feedback_bundle(index, self.table, cid) for cid in upto]

    def run_stage(self, llm):
        stage = self.next_stage()
        if stage is None:
            return None
        index = load_index(self.index_path)
        if digest(index["menu"]) != self.state["menu_sha256"]:
            raise ValueError("Menu changed after the pilot started")
        bundles = self._revealed(index, stage)  # may raise Pending (state unchanged)
        for b in bundles:
            if b["candidate_id"] not in self.state["evaluated"]:
                self.state["evaluated"].append(b["candidate_id"])
        remaining = [c for c in self.state["feasible"] if c not in self.state["evaluated"] and c not in self.state["selected"]]
        user = dict(stage=stage, brief="Choose by the fixed brief; give falsifiable predictions before any energy exists.",
                    candidates=self._cards(index), evaluated=self.state["evaluated"], unevaluated=remaining,
                    feedback=bundles, output_schema=OUTPUT_SCHEMA[stage])
        feedback = ""
        for attempt in range(MAX_FORMAT_ATTEMPTS):
            # Hard ceiling: refuse a call whose worst-case transport retries could exceed the cap.
            if self.state["http_attempts_used"] + self.state["max_http_per_call"] > self.state["http_cap"]:
                self.state["status"] = "stopped: HTTP attempt cap reached"
                self._save()
                return None
            prompt = json.dumps({**user, "validation_feedback": feedback}, sort_keys=True)
            record = dict(stage=stage, attempt=attempt, prompt=prompt, feedback_sha256=[digest(b) for b in bundles],
                          started_at=_now(), parsed=None)
            try:
                response = llm(SYSTEM_PROMPT, prompt)
                record["response"] = response
                record["parsed"] = validate_decision(stage, response, remaining)
            except Exception as exc:
                feedback = f"{type(exc).__name__}: {exc}"
                record["error"] = feedback
            meta = getattr(llm, "last_metadata", None)
            record["llm_metadata"] = meta
            self.state["http_attempts_used"] += (meta or {}).get("http_attempts", 1)
            record["frozen_at"] = _now()
            record["record_sha256"] = digest({k: v for k, v in record.items() if k != "record_sha256"})
            self.state["stages"].append(record)
            if record["parsed"] is not None:
                if stage in ("choose_2", "choose_3"):
                    self.state["selected"].append(record["parsed"]["selected_id"])
                if stage == "summary":
                    self.state["status"] = "complete"
                self._save()
                return record
            self._save()
        self.state["stages"].append(dict(stage=stage, failed=True, reason="format attempts exhausted", at=_now()))
        self.state["status"] = f"stopped: {stage} failed validation"
        self._save()
        return None

    def assessment(self):
        """Deterministic prediction checks and the decision comparison (descriptive only)."""
        index = load_index(self.index_path)
        decisions = {s["stage"]: s["parsed"] for s in self.state["stages"] if s.get("parsed")}
        rows = []
        for stage in ("choose_2", "choose_3"):
            if stage not in decisions:
                continue
            d = decisions[stage]
            try:
                b = feedback_bundle(index, self.table, d["selected_id"])
            except Pending:
                rows.append(dict(stage=stage, candidate_id=d["selected_id"], status="pending"))
                continue
            checks = {}
            for c in CONTACTS:
                lo, hi = d["predicted_W_adh_J_m2"][c]
                obs = b["contacts"][c]["W_adh_J_m2"]
                checks[c] = dict(predicted=[lo, hi], width=hi - lo, observed=obs,
                                 in_range=None if obs is None else lo <= obs <= hi,
                                 miss=None if obs is None else max(lo - obs, obs - hi, 0.0))
            rows.append(dict(stage=stage, candidate_id=d["selected_id"], contacts=checks,
                             weaker_predicted=d["predicted_weaker_contact"], weaker_observed=b["weaker_contact"],
                             weaker_agrees=None if b["weaker_contact"] == "unresolved"
                             else d["predicted_weaker_contact"] == b["weaker_contact"]))
        comparison = None
        if "choose_2" in decisions and "choose_3" in decisions:
            initial = [c for c in decisions["choose_2"]["ordered_shortlist"] if c != decisions["choose_2"]["selected_id"]]
            comparison = dict(initial_next=initial[0] if initial else None, chosen=decisions["choose_3"]["selected_id"],
                              changed=bool(initial) and initial[0] != decisions["choose_3"]["selected_id"],
                              note="Decision comparison at a common information state; the unchosen coating has no measured outcome.")
        return dict(predictions=rows, decision_comparison=comparison, http_attempts_used=self.state["http_attempts_used"])


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
