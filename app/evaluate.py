import json
import sys
from pathlib import Path

from app.classifier import classify_ticket


def evaluate(path: Path) -> None:
    tickets = json.loads(path.read_text(encoding="utf-8-sig"))

    if not tickets:
        raise SystemExit("The evaluation dataset is empty.")

    team_correct = 0
    priority_correct = 0
    both_correct = 0
    failures = 0
    critical_total = sum(
        ticket["expected_priority"] == "critical" for ticket in tickets
    )
    critical_correct = 0

    for ticket in tickets:
        try:
            result, _ = classify_ticket(ticket["text"])
        except Exception as error:
            failures += 1
            print(f"Ticket {ticket['id']}: classification failed: {error}")
            continue

        team_match = result.team == ticket["expected_team"]
        priority_match = result.priority == ticket["expected_priority"]

        team_correct += team_match
        priority_correct += priority_match
        both_correct += team_match and priority_match

        if ticket["expected_priority"] == "critical":
            critical_correct += result.priority == "critical"

        if not (team_match and priority_match):
            print(
                f"Ticket {ticket['id']}: "
                f"expected {ticket['expected_team']}/{ticket['expected_priority']}; "
                f"received {result.team}/{result.priority}"
            )

    total = len(tickets)

    # Failed requests count as incorrect classifications.
    print(f"\nTickets: {total}")
    print(f"API/processing failures: {failures}")
    print(f"Team accuracy: {team_correct / total:.1%}")
    print(f"Priority accuracy: {priority_correct / total:.1%}")
    print(f"Both correct: {both_correct / total:.1%}")

    if critical_total:
        print(
            f"Critical recall: "
            f"{critical_correct}/{critical_total} "
            f"({critical_correct / critical_total:.1%})"
        )


if __name__ == "__main__":
    dataset = Path(
        sys.argv[1] if len(sys.argv) > 1 else "data/eval_set.json"
    )
    evaluate(dataset)
