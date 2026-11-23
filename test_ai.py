from llm_service import analyze_ticket

ticket = (
    "I was charged twice for my monthly subscription. "
    "Please help me get this resolved."
)

result = analyze_ticket(ticket)

print("\n--- AI TICKET ANALYSIS ---")
for key, value in result.items():
    print(f"{key}: {value}")