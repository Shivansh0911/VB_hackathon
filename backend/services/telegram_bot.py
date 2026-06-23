"""
CivicPulse Telegram Bot — free, no billing.
Citizens can list issues and confirm with a photo directly from Telegram.

Setup:
  1. Open Telegram → search @BotFather → /newbot
  2. Name: CivicPulse  |  Username: civicpulseai_bot (or any available)
  3. Copy the token → add as TELEGRAM_BOT_TOKEN env var on Render
"""
import os
import base64
from typing import Dict

from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes,
)

from database import get_all_issues, get_issue
from agents.confirmation_agent import process_confirmation

# In-memory: tracks which issue a user is currently confirming
_pending: Dict[int, int] = {}  # chat_id → issue_id

CATEGORY_ICONS = {
    "POTHOLE": "🕳️", "STREETLIGHT": "💡", "WATER_LEAKAGE": "💧",
    "GARBAGE": "🗑️", "BROKEN_FOOTPATH": "🚶", "DRAINAGE": "🌊",
    "TREE_FALLEN": "🌳", "ROAD_DAMAGE": "🛣️", "OTHER": "⚠️",
}
STATUS_EMOJI = {
    "DISCOVERED": "🔍", "CONFIRMED": "✅", "ESCALATED": "📨", "RESOLVED": "✔️",
}


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏙️ *CivicPulse*\n\n"
        "I surface civic issues discovered by AI across Bengaluru, Mumbai & Hyderabad.\n\n"
        "📋 /issues — see current issues\n"
        "📸 /confirm <id> — validate an issue with a photo\n\n"
        "_AI discovers · You confirm · Agents escalate to government_",
        parse_mode="Markdown",
    )


async def cmd_issues(update: Update, context: ContextTypes.DEFAULT_TYPE):
    issues = get_all_issues()
    if not issues:
        await update.message.reply_text("No issues yet. Try again in a minute while discovery runs.")
        return

    # Top 8, prioritise DISCOVERED (needs confirmations) over already escalated
    top = sorted(issues, key=lambda x: (x["status"] == "ESCALATED", -x["confidence_score"]))[:8]

    lines = ["*Active Civic Issues:*\n"]
    for issue in top:
        icon = CATEGORY_ICONS.get(issue["category"], "⚠️")
        status = STATUS_EMOJI.get(issue["status"], "🔍")
        needed = max(0, 5 - issue["confirmation_count"])
        suffix = f"  _(needs {needed} more)_" if issue["status"] == "DISCOVERED" and needed > 0 else ""
        lines.append(f"{status} *#{issue['id']}* {icon} {issue['title']}\n   📍 _{issue['location_name']}_{suffix}\n")

    lines.append("Send /confirm <id> to validate with your photo")
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def cmd_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "Usage: /confirm <issue\\_id>\nExample: /confirm 3\n\nSend /issues to see IDs.",
            parse_mode="Markdown",
        )
        return

    try:
        issue_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Please send a valid number. Example: /confirm 3")
        return

    issue = get_issue(issue_id)
    if not issue:
        await update.message.reply_text(f"Issue #{issue_id} not found. Send /issues to see available ones.")
        return

    if issue["status"] in ("ESCALATED", "RESOLVED"):
        await update.message.reply_text(
            f"Issue #{issue_id} is already {issue['status']} — nothing to confirm."
        )
        return

    _pending[update.effective_chat.id] = issue_id
    icon = CATEGORY_ICONS.get(issue["category"], "⚠️")

    await update.message.reply_text(
        f"📸 *Confirming Issue \\#{issue_id}*\n\n"
        f"{icon} {issue['title']}\n"
        f"📍 _{issue['location_name']}_\n\n"
        f"Send a *photo* of what you see at this location\\.\n"
        f"Or send /skip to confirm without a photo\\.",
        parse_mode="MarkdownV2",
    )


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    issue_id = _pending.get(chat_id)

    if not issue_id:
        await update.message.reply_text(
            "Send /confirm <id> first to start confirming an issue.\nSend /issues to see IDs."
        )
        return

    await update.message.reply_text("🔍 Gemini is validating your photo...")

    photo_file = await (update.message.photo[-1]).get_file()
    photo_bytes = await photo_file.download_as_bytearray()
    photo_b64 = base64.b64encode(bytes(photo_bytes)).decode("utf-8")

    result = await process_confirmation(issue_id, photo_b64, "Confirmed via Telegram")
    _pending.pop(chat_id, None)

    if not result["success"]:
        await update.message.reply_text(f"⚠️ {result['error']}")
        return

    validation = result.get("validation", {})
    valid = validation.get("valid", True)
    confidence = validation.get("confidence", 50)
    reasoning = validation.get("reasoning", "")
    count = result["new_confirmation_count"]
    needed = max(0, 5 - count)

    if valid:
        msg = f"✅ *Photo validated by Gemini!*\nConfidence: {confidence}%\n_{reasoning}_\n\nConfirmations: {count}/5"
    else:
        msg = f"⚠️ *Photo didn't match — still recorded*\n_{reasoning}_\n\nConfirmations: {count}/5"

    if result.get("ready_for_escalation"):
        msg += "\n\n🚨 *Threshold reached\\! Escalating to authorities now\\.\\.\\.*"
    elif needed > 0:
        msg += f"\n_{needed} more needed to escalate_"

    await update.message.reply_text(msg, parse_mode="Markdown")


async def cmd_skip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    issue_id = _pending.get(chat_id)

    if not issue_id:
        await update.message.reply_text("Send /confirm <id> first.")
        return

    result = await process_confirmation(issue_id, "", "Confirmed via Telegram (no photo)")
    _pending.pop(chat_id, None)

    if not result["success"]:
        await update.message.reply_text(f"⚠️ {result['error']}")
        return

    count = result["new_confirmation_count"]
    needed = max(0, 5 - count)
    msg = f"✅ Confirmation recorded (no photo)\nConfirmations: {count}/5"
    if result.get("ready_for_escalation"):
        msg += "\n\n🚨 Threshold reached! Escalating to authorities now..."
    elif needed > 0:
        msg += f"\n_{needed} more needed to escalate_"

    await update.message.reply_text(msg, parse_mode="Markdown")


def build_application(token: str) -> Application:
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("issues", cmd_issues))
    app.add_handler(CommandHandler("list", cmd_issues))
    app.add_handler(CommandHandler("confirm", cmd_confirm))
    app.add_handler(CommandHandler("skip", cmd_skip))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    return app
