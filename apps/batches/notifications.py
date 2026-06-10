import datetime


def get_due_events(batch, prefs, today: datetime.date) -> list[str]:
    events: list[str] = []

    if prefs.notify_tosna and batch.pitch_yeast_date:
        if not batch.fo_24h_done and batch.pitch_yeast_date + datetime.timedelta(days=1) == today:
            events.append("TOSNA 24h nutrient addition")
        if not batch.fo_48h_done and batch.pitch_yeast_date + datetime.timedelta(days=2) == today:
            events.append("TOSNA 48h nutrient addition")
        if not batch.fo_72h_done and batch.pitch_yeast_date + datetime.timedelta(days=3) == today:
            events.append("TOSNA 72h nutrient addition")

    if prefs.notify_sg_check and batch.pitch_yeast_date:
        if not batch.fo_1_3_break_done and batch.pitch_yeast_date + datetime.timedelta(days=4) == today:
            events.append("1/3 sugar break gravity check")

    if prefs.notify_rack and batch.secondary_date:
        if not batch.rack_secondary_done and batch.secondary_date == today:
            events.append("Rack to secondary")

    if prefs.notify_bottle and batch.bottling_date:
        if not batch.bottled_done and batch.bottling_date == today:
            events.append("Bottling day")

    return events
