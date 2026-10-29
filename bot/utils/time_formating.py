def format_time(time):
    hours = time//60
    mins = time%60
    
    parts = []

    if hours:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if mins:
        parts.append(f"{mins} minute{'s' if mins != 1 else ''}")
    return ", ".join(parts) if parts else "0 minutes"

def format_afk_duration(elapsed):
    mins, secs = divmod(int(elapsed), 60)
    hours, mins = divmod(mins, 60)
    days, hours = divmod(hours, 24)

    days_str = f"{days} day{'s' if days != 1 else ''}" if days > 0 else ""

    hours_str = f"{hours} hour{'s' if hours != 1 else ''}" if hours > 0 else ""

    minutes_str = (
        f"{mins} minute{'s' if mins != 1 else ''}" if mins > 0 else ""
    )

    seconds_str = (
        f"{secs} second{'s' if secs != 1 else ''}" if secs > 0 else ""
    )

    components = [
        comp for comp in [days_str, hours_str, minutes_str, seconds_str] if comp
    ]
    formatted_duration = (
        ", ".join(components[:-1])
        + (" and " if len(components) > 1 else "")
        + components[-1]
    )

    return formatted_duration