from __future__ import annotations

from lexcapital.core.models import ActionType, ModelDecision, Order, RiskLimit, Scenario


def make_rule_aware_decisions(scenario: Scenario) -> list[ModelDecision]:
    """Conservative heuristic baseline that reads rules before acting.

    It avoids private metadata and chooses HOLD unless the scenario metadata says
    an oracle should beat cash. Even then it only makes a tiny cited trade.
    """

    oracle_min = float(scenario.baseline_expectations.get("oracle_score_min", 85) or 85)
    instrument_id = scenario.instruments[0].id if scenario.instruments else None
    trade_action = next((a for a in scenario.allowed_actions if a not in {ActionType.HOLD, ActionType.CLOSE}), ActionType.HOLD)
    should_probe = bool(instrument_id and trade_action != ActionType.HOLD and oracle_min > 90)
    decisions: list[ModelDecision] = []
    for step in range(scenario.max_steps):
        if should_probe and step == 0:
            orders = [Order(action=trade_action, instrument_id=instrument_id, notional_usd=5.0)]
            rationale = "Rule-aware small cited probe; constraints cap risk."
        else:
            orders = [Order(action=ActionType.HOLD)]
            rationale = "Rule-aware abstention; traps dominate edge."
        decisions.append(
            ModelDecision(
                step=step,
                orders=orders,
                rule_citations=[rule.id for rule in scenario.public_rules[:2]],
                risk_limit=RiskLimit(max_loss_usd=3, max_drawdown_pct=0.03, max_position_usd=10),
                confidence=0.6,
                rationale_summary=rationale,
                evidence_timestamps=[step],
                metadata={
                    "baseline_policy": "rule-aware",
                    "borrow_fee_acknowledged": True,
                    "locate_documented": True,
                    "strategy_tags": ["rule_constrained"],
                },
            )
        )
    return decisions
