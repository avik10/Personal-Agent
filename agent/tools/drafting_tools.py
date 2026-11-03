"""Communication, Email Drafting, and Writing Polish Tools."""


def draft_email(recipient: str, subject: str, purpose: str, tone: str = "professional") -> str:
    """Prepare a structured draft template for an email given recipient, subject, purpose, and tone."""
    rec = recipient.strip() if recipient else "Recipient"
    sub = subject.strip() if subject else "Follow-up"
    pur = purpose.strip() if purpose else "General inquiry"
    tn = tone.strip().lower()

    if "casual" in tn or "friendly" in tn:
        salutation = f"Hi {rec},"
        closing = "Best regards,"
    elif "formal" in tn:
        salutation = f"Dear {rec},"
        closing = "Sincerely,"
    else:
        salutation = f"Dear {rec},"
        closing = "Kind regards,"

    template = (
        f"Subject: {sub}\n\n"
        f"{salutation}\n\n"
        f"I am writing regarding {pur}.\n\n"
        f"[Draft body addressing the key details clearly and courteously]\n\n"
        f"Please let me know if you need any additional information.\n\n"
        f"{closing}\n"
        f"[Your Name]"
    )
    return template


def polish_message(raw_text: str, target_tone: str = "clear and professional") -> str:
    """Format and frame a message for polishing by the LLM."""
    clean = raw_text.strip()
    return f"Text to polish ({target_tone}):\n{clean}"


def draft_meeting_agenda(topic: str, duration_mins: int = 30) -> str:
    """Generate a structured meeting agenda template with time allocations."""
    top = topic.strip() if topic else "Project Sync"
    dur = max(15, duration_mins)

    intro_time = max(5, int(dur * 0.15))
    discussion_time = int(dur * 0.60)
    actions_time = dur - intro_time - discussion_time

    agenda = (
        f"Agenda: {top} ({dur} Minutes)\n"
        f"1. Welcome & Context Alignment ({intro_time} mins)\n"
        f"   - Brief objectives and scope\n"
        f"2. Core Discussion & Strategy ({discussion_time} mins)\n"
        f"   - Key items, challenges, and solutions\n"
        f"3. Next Steps & Action Item Assignments ({actions_time} mins)\n"
        f"   - Ownership, deliverables, and deadlines"
    )
    return agenda
