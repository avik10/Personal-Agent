"""Personal Finance, Expense Tracking, and Budget Management Tools."""

import json
from datetime import datetime
from typing import Dict, List, Optional
from config.settings import EXPENSES_FILE, STORAGE_DIR


def _load_finance_data() -> dict:
    if not EXPENSES_FILE.exists():
        return {"expenses": [], "budgets": {}}
    try:
        with open(EXPENSES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                return {"expenses": [], "budgets": {}}
            data.setdefault("expenses", [])
            data.setdefault("budgets", {})
            return data
    except Exception:
        return {"expenses": [], "budgets": {}}


def _save_finance_data(data: dict) -> None:
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    with open(EXPENSES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def log_expense(amount: float, category: str = "general", description: str = "") -> str:
    """Log an expense with amount, category (e.g. food, groceries, travel, bills, shopping), and optional description.
    
    Examples:
    - log_expense(amount=450.0, category='groceries', description='milk, bread, vegetables')
    - log_expense(amount=120.0, category='travel', description='auto rickshaw fare')
    """
    try:
        amt = float(amount)
        if amt <= 0:
            return "Expense amount must be greater than zero."

        data = _load_finance_data()
        expenses = data.get("expenses", [])
        new_id = (max([e.get("id", 0) for e in expenses], default=0)) + 1
        now = datetime.now()

        item = {
            "id": new_id,
            "amount": amt,
            "category": category.strip().lower() if category else "general",
            "description": description.strip(),
            "date": now.strftime("%Y-%m-%d"),
            "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
        }
        expenses.append(item)
        data["expenses"] = expenses
        _save_finance_data(data)

        cat_total = sum(e["amount"] for e in expenses if e.get("category") == item["category"])
        budget_limit = data.get("budgets", {}).get(item["category"])
        budget_msg = f" (Category Total: ₹{cat_total:.2f}" + (f" / Budget: ₹{budget_limit:.2f})" if budget_limit else ")")

        desc_str = f" for '{description}'" if description else ""
        return f"Logged expense #{new_id}: ₹{amt:.2f} under [{item['category']}]{desc_str}.{budget_msg}"
    except Exception as e:
        return f"Error logging expense: {e}"


def get_expense_summary(period: str = "this_month") -> str:
    """Get total expense breakdown by category for a period ('today', 'this_month', or 'all')."""
    data = _load_finance_data()
    expenses = data.get("expenses", [])
    if not expenses:
        return "No expenses recorded yet."

    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    month_prefix = now.strftime("%Y-%m")

    p = period.lower().strip()
    if p == "today":
        filtered = [e for e in expenses if e.get("date") == today_str]
        label = f"Today ({today_str})"
    elif p in ("all", "total"):
        filtered = expenses
        label = "All Time"
    else:
        filtered = [e for e in expenses if str(e.get("date", "")).startswith(month_prefix)]
        label = f"This Month ({now.strftime('%B %Y')})"

    if not filtered:
        return f"No expenses found for {label}."

    total_amount = sum(e.get("amount", 0.0) for e in filtered)
    cat_breakdown: Dict[str, float] = {}
    for e in filtered:
        cat = e.get("category", "general")
        cat_breakdown[cat] = cat_breakdown.get(cat, 0.0) + e.get("amount", 0.0)

    lines = [f"Expense Summary ({label}):", f"• Total Spent: ₹{total_amount:.2f}", "• Breakdown by Category:"]
    for cat, amt in sorted(cat_breakdown.items(), key=lambda x: x[1], reverse=True):
        pct = (amt / total_amount) * 100 if total_amount > 0 else 0
        budget = data.get("budgets", {}).get(cat)
        budget_info = f" (Budget: ₹{budget:.2f})" if budget else ""
        lines.append(f"  - {cat.capitalize()}: ₹{amt:.2f} ({pct:.1f}%){budget_info}")

    return "\n".join(lines)


def list_expenses(limit: int = 10) -> str:
    """List the most recent recorded expenses."""
    data = _load_finance_data()
    expenses = data.get("expenses", [])
    if not expenses:
        return "No expenses recorded."

    recent = sorted(expenses, key=lambda x: x.get("timestamp", ""), reverse=True)[:limit]
    lines = [f"Recent Expenses (Last {len(recent)}):"]
    for e in recent:
        desc = f" - {e['description']}" if e.get("description") else ""
        lines.append(f"  #{e['id']} [{e.get('date')}]: ₹{e['amount']:.2f} ({e['category']}){desc}")
    return "\n".join(lines)


def set_budget(category: str, monthly_limit: float) -> str:
    """Set a monthly budget spending limit for a specific category (e.g. food, travel, shopping)."""
    try:
        lim = float(monthly_limit)
        if lim <= 0:
            return "Budget limit must be greater than zero."
        data = _load_finance_data()
        budgets = data.setdefault("budgets", {})
        cat_key = category.strip().lower()
        budgets[cat_key] = lim
        _save_finance_data(data)
        return f"Monthly budget for '{cat_key}' set to ₹{lim:.2f}."
    except Exception as e:
        return f"Error setting budget: {e}"
