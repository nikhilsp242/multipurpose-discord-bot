import discord
from datetime import datetime, timezone

def get_account_age(member: discord.Member):
    account_created_at = member.created_at.replace(tzinfo=timezone.utc)
    current_utc_datetime = datetime.now(timezone.utc)
    account_age = current_utc_datetime - account_created_at

    total_seconds = int(account_age.total_seconds())
    minutes = (total_seconds // 60) % 60
    hours = (total_seconds // 3600) % 24
    days = account_age.days

    # Estimate months and years
    years = days // 365
    days %= 365
    months = days // 30
    days %= 30

    parts = []
    if years: parts.append(f"{years}y")
    if months: parts.append(f"{months}mo")
    if days: parts.append(f"{days}d")
    if hours: parts.append(f"{hours}h")
    if minutes: parts.append(f"{minutes}m")

    return " ".join(parts) if parts else "Just Created"
