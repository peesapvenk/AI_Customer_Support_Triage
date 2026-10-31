
from app.classifier import classify_ticket


def main():
    ticket = input("Enter support ticket: ").strip()

    if not ticket:
        print("Ticket cannot be empty.")
        return

    result, usage = classify_ticket(ticket)

    print("\n--- Classification ---")
    print(f"Team: {result.team}")
    print(f"Priority: {result.priority}")
    print(f"Reason: {result.reason}")
    print(f"Suggested reply: {result.suggested_reply}")

    print ("\n--- Technical Stats ---")
    print("Input tokens:", usage.input_tokens)
    print("Output tokens:", usage.output_tokens)
    print("Total tokens:", usage.total_tokens)


if __name__ == "__main__":
    main()