import datetime
import pytest
from unittest.mock import MagicMock
from apps.batches.notifications import get_due_events


def make_prefs(
    notify_tosna=True,
    notify_sg_check=True,
    notify_rack=True,
    notify_bottle=True,
):
    prefs = MagicMock()
    prefs.notify_tosna = notify_tosna
    prefs.notify_sg_check = notify_sg_check
    prefs.notify_rack = notify_rack
    prefs.notify_bottle = notify_bottle
    return prefs


def make_batch(
    pitch_yeast_date=None,
    secondary_date=None,
    bottling_date=None,
    fo_24h_done=False,
    fo_48h_done=False,
    fo_72h_done=False,
    fo_1_3_break_done=False,
    rack_secondary_done=False,
    bottled_done=False,
):
    batch = MagicMock()
    batch.pitch_yeast_date = pitch_yeast_date
    batch.secondary_date = secondary_date
    batch.bottling_date = bottling_date
    batch.fo_24h_done = fo_24h_done
    batch.fo_48h_done = fo_48h_done
    batch.fo_72h_done = fo_72h_done
    batch.fo_1_3_break_done = fo_1_3_break_done
    batch.rack_secondary_done = rack_secondary_done
    batch.bottled_done = bottled_done
    batch.name = "Test Batch"
    return batch


BASE_DATE = datetime.date(2026, 6, 10)


class TestGetDueEventsTosna:
    def test_24h_fires_on_correct_date(self):
        batch = make_batch(pitch_yeast_date=datetime.date(2026, 6, 9))
        prefs = make_prefs()
        events = get_due_events(batch, prefs, today=BASE_DATE)
        assert "TOSNA 24h nutrient addition" in events

    def test_48h_fires_on_correct_date(self):
        batch = make_batch(pitch_yeast_date=datetime.date(2026, 6, 8))
        prefs = make_prefs()
        events = get_due_events(batch, prefs, today=BASE_DATE)
        assert "TOSNA 48h nutrient addition" in events

    def test_72h_fires_on_correct_date(self):
        batch = make_batch(pitch_yeast_date=datetime.date(2026, 6, 7))
        prefs = make_prefs()
        events = get_due_events(batch, prefs, today=BASE_DATE)
        assert "TOSNA 72h nutrient addition" in events

    def test_24h_skipped_when_done(self):
        batch = make_batch(pitch_yeast_date=datetime.date(2026, 6, 9), fo_24h_done=True)
        prefs = make_prefs()
        events = get_due_events(batch, prefs, today=BASE_DATE)
        assert "TOSNA 24h nutrient addition" not in events

    def test_48h_skipped_when_done(self):
        batch = make_batch(pitch_yeast_date=datetime.date(2026, 6, 8), fo_48h_done=True)
        prefs = make_prefs()
        events = get_due_events(batch, prefs, today=BASE_DATE)
        assert "TOSNA 48h nutrient addition" not in events

    def test_72h_skipped_when_done(self):
        batch = make_batch(pitch_yeast_date=datetime.date(2026, 6, 7), fo_72h_done=True)
        prefs = make_prefs()
        events = get_due_events(batch, prefs, today=BASE_DATE)
        assert "TOSNA 72h nutrient addition" not in events

    def test_tosna_skipped_when_no_pitch_date(self):
        batch = make_batch(pitch_yeast_date=None)
        prefs = make_prefs()
        events = get_due_events(batch, prefs, today=BASE_DATE)
        assert not any("TOSNA" in e for e in events)

    def test_tosna_skipped_when_pref_off(self):
        batch = make_batch(pitch_yeast_date=datetime.date(2026, 6, 9))
        prefs = make_prefs(notify_tosna=False)
        events = get_due_events(batch, prefs, today=BASE_DATE)
        assert not any("TOSNA" in e for e in events)

    def test_no_false_positive_on_wrong_date(self):
        batch = make_batch(pitch_yeast_date=datetime.date(2026, 6, 5))
        prefs = make_prefs()
        events = get_due_events(batch, prefs, today=BASE_DATE)
        assert not any("TOSNA" in e for e in events)


class TestGetDueEventsSgCheck:
    def test_sg_check_fires_on_day_4(self):
        batch = make_batch(pitch_yeast_date=datetime.date(2026, 6, 6))
        prefs = make_prefs()
        events = get_due_events(batch, prefs, today=BASE_DATE)
        assert "1/3 sugar break gravity check" in events

    def test_sg_check_skipped_when_done(self):
        batch = make_batch(pitch_yeast_date=datetime.date(2026, 6, 6), fo_1_3_break_done=True)
        prefs = make_prefs()
        events = get_due_events(batch, prefs, today=BASE_DATE)
        assert "1/3 sugar break gravity check" not in events

    def test_sg_check_skipped_when_no_pitch_date(self):
        batch = make_batch(pitch_yeast_date=None)
        prefs = make_prefs()
        events = get_due_events(batch, prefs, today=BASE_DATE)
        assert "1/3 sugar break gravity check" not in events

    def test_sg_check_skipped_when_pref_off(self):
        batch = make_batch(pitch_yeast_date=datetime.date(2026, 6, 6))
        prefs = make_prefs(notify_sg_check=False)
        events = get_due_events(batch, prefs, today=BASE_DATE)
        assert "1/3 sugar break gravity check" not in events


class TestGetDueEventsRack:
    def test_rack_fires_on_secondary_date(self):
        batch = make_batch(secondary_date=BASE_DATE)
        prefs = make_prefs()
        events = get_due_events(batch, prefs, today=BASE_DATE)
        assert "Rack to secondary" in events

    def test_rack_skipped_when_done(self):
        batch = make_batch(secondary_date=BASE_DATE, rack_secondary_done=True)
        prefs = make_prefs()
        events = get_due_events(batch, prefs, today=BASE_DATE)
        assert "Rack to secondary" not in events

    def test_rack_skipped_when_no_secondary_date(self):
        batch = make_batch(secondary_date=None)
        prefs = make_prefs()
        events = get_due_events(batch, prefs, today=BASE_DATE)
        assert "Rack to secondary" not in events

    def test_rack_skipped_when_pref_off(self):
        batch = make_batch(secondary_date=BASE_DATE)
        prefs = make_prefs(notify_rack=False)
        events = get_due_events(batch, prefs, today=BASE_DATE)
        assert "Rack to secondary" not in events


class TestGetDueEventsBottle:
    def test_bottle_fires_on_bottling_date(self):
        batch = make_batch(bottling_date=BASE_DATE)
        prefs = make_prefs()
        events = get_due_events(batch, prefs, today=BASE_DATE)
        assert "Bottling day" in events

    def test_bottle_skipped_when_done(self):
        batch = make_batch(bottling_date=BASE_DATE, bottled_done=True)
        prefs = make_prefs()
        events = get_due_events(batch, prefs, today=BASE_DATE)
        assert "Bottling day" not in events

    def test_bottle_skipped_when_no_bottling_date(self):
        batch = make_batch(bottling_date=None)
        prefs = make_prefs()
        events = get_due_events(batch, prefs, today=BASE_DATE)
        assert "Bottling day" not in events

    def test_bottle_skipped_when_pref_off(self):
        batch = make_batch(bottling_date=BASE_DATE)
        prefs = make_prefs(notify_bottle=False)
        events = get_due_events(batch, prefs, today=BASE_DATE)
        assert "Bottling day" not in events


class TestGetDueEventsEmpty:
    def test_returns_empty_list_when_nothing_due(self):
        batch = make_batch()
        prefs = make_prefs()
        events = get_due_events(batch, prefs, today=BASE_DATE)
        assert events == []
