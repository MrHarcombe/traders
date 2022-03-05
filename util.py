from datetime import datetime, timezone

UTC_FORMAT = '%Y-%m-%dT%H:%M:%S.%f%z'
DISPLAY_FORMAT = ' %B, %Y'


def parse_datetime(dt):
    return datetime.strptime(dt, UTC_FORMAT)


def format_datetime(dt_text):
    dt = parse_datetime(dt_text)
    d = dt.day
    return str(d) + ('th' if 11<=d<=13 else {1:'st',2:'nd',3:'rd'}.get(d%10, 'th')) + datetime.strftime(dt, DISPLAY_FORMAT)


