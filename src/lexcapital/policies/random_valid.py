from __future__ import annotations

from lexcapital.core.models import ActionType, ModelDecision, Order, RiskLimit, Scenario


def _first_tradable_instrument(scenario: Scenario) -> str | None:
    return scenario.instruments[0].id if scenario.instruments else None


def _trade_action(scenario: Scenario) -> ActionType:
    for action in scenario.allowed_actions:
        if action != ActionType.HOLD:
            return action
    return ActionType.HOLD


def make_random_valid_decisions(scenario: Scenario, seed: int | None = None) -> list[ModelDecision]:
    """Deterministic low-risk valid baseline.

    The policy name is random-valid, but benchmark reproducibility matters more
    than fake randomness: with a seed it deterministically alternates HOLD and a
    tiny allowed trade. The tiny notional keeps it replay-safe across packs.
    """

    instrument_id = _first_tradable_instrument(scenario)
    trade_action = _trade_action(scenario)
    decisions: list[ModelDecision] = []
    offset = int(seed or 0) % 2
    for step in range(scenario.max_steps):
        if instrument_id and trade_action != ActionType.HOLD and (step + offset) % 2 == 1:
            orders = [Order(action=trade_action, instrument_id=instrument_id, notional_usd=1.0)]
            rationale = "Seeded random-valid tiny allowed trade."
        else:
            orders = [Order(action=ActionType.HOLD)]
            rationale = "Seeded random-valid HOLD."
        decisions.append(
            ModelDecision(
                step=step,
                orders=orders,
                rule_citations=[scenario.public_rules[0].id] if scenario.public_rules else [],
                risk_limit=RiskLimit(max_loss_usd=2, max_drawdown_pct=0.02, max_position_usd=5),
                confidence=0.45,
                rationale_summary=rationale,
                evidence_timestamps=[step],
                metadata={"baseline_policy": "random-valid", "seed": seed},
            )
        )
    return decisions
