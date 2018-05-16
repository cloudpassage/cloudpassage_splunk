from datetime import datetime, timedelta

def past_date(ago):
    date = (datetime.now() - timedelta(days=ago)).strftime("%Y-%m-%d")
    return date

def get_start_date(input_items, checkpoint):
    if checkpoint:
        return checkpoint
    if "events_start_date" in input_items:
        return input_items["events_start_date"]
    return past_date(89)
