import pendulum

def format_time(time: int):
    """
    Formats a given time (in seconds) to format (days)d(hours)h(minutes)m(seconds)s

    Time step wont be present if its 0 (120 would just be 2m instead of 2m0s)
    """
    minutes, seconds = divmod(time, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    time = f'{days}d' if days > 0 else ''
    time += f'{hours}h' if hours > 0 else ''
    time += f'{minutes}m' if minutes > 0 else ''
    time += f'{seconds}s' if seconds > 0 else ''
    return time

def format_date(dt: pendulum.datetime):
    """Formats a given datetime object to format YYYY-MM-DD hh:mm"""
    return dt.strftime('%Y-%m-%d %H:%M')

def timezone_diff(self, tz1: str, tz2: str):
    """
    Returns the difference of hours of given timezones

    Result can be negative which means tz2 is ahead of tz1
    """
    return (pendulum.now(tz1).offset - pendulum.now(tz2).offset) // 3600