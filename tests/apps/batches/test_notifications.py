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


import pytest
from unittest.mock import patch
from django.contrib.auth import get_user_model
from apps.accounts.models import UserNotificationPrefs
from apps.batches.models import Batch

User = get_user_model()

TODAY = datetime.date(2026, 6, 10)


@pytest.fixture
def opted_in_user(db):
    u = User.objects.create_user(
        username='brewer1', email='brewer1@example.com', password='pass',
        is_approved=True,
    )
    UserNotificationPrefs.objects.create(
        user=u,
        email_notifications=True,
        notify_tosna=True,
        notify_sg_check=True,
        notify_rack=True,
        notify_bottle=True,
    )
    return u


@pytest.fixture
def opted_out_user(db):
    u = User.objects.create_user(
        username='brewer2', email='brewer2@example.com', password='pass',
        is_approved=True,
    )
    UserNotificationPrefs.objects.create(user=u, email_notifications=False)
    return u


@pytest.fixture
def batch_with_24h_due(opted_in_user):
    return Batch.objects.create(
        user=opted_in_user,
        name='Wildflower Mead',
        batch_size='5.0',
        og='1.110',
        primary_date=datetime.date(2026, 6, 1),
        pitch_yeast_date=datetime.date(2026, 6, 9),  # +1 day = TODAY
    )


@pytest.mark.django_db
class TestSendBatchNotificationsCommand:
    def _call_command(self, today=TODAY):
        from django.core.management import call_command
        with patch('apps.batches.management.commands.send_batch_notifications.date') as mock_date:
            mock_date.today.return_value = today
            mock_date.side_effect = lambda *a, **kw: datetime.date(*a, **kw)
            call_command('send_batch_notifications')

    def test_sends_email_to_opted_in_user_with_due_events(
        self, opted_in_user, batch_with_24h_due
    ):
        with patch('apps.batches.management.commands.send_batch_notifications.send_mail') as mock_send:
            self._call_command()
            assert mock_send.call_count == 1
            call_args = mock_send.call_args
            assert opted_in_user.email in call_args.kwargs.get('recipient_list', call_args.args[3] if len(call_args.args) > 3 else [])

    def test_email_subject_contains_date(self, opted_in_user, batch_with_24h_due):
        with patch('apps.batches.management.commands.send_batch_notifications.send_mail') as mock_send:
            self._call_command()
            call_args = mock_send.call_args
            subject = call_args.kwargs.get('subject', call_args.args[0] if call_args.args else '')
            assert '2026-06-10' in subject

    def test_no_email_for_opted_out_user(self, opted_out_user):
        Batch.objects.create(
            user=opted_out_user,
            name='Opted Out Mead',
            batch_size='5.0',
            og='1.100',
            primary_date=datetime.date(2026, 6, 1),
            pitch_yeast_date=datetime.date(2026, 6, 9),
        )
        with patch('apps.batches.management.commands.send_batch_notifications.send_mail') as mock_send:
            self._call_command()
            mock_send.assert_not_called()

    def test_no_email_when_no_events_due(self, opted_in_user):
        Batch.objects.create(
            user=opted_in_user,
            name='Old Mead',
            batch_size='5.0',
            og='1.100',
            primary_date=datetime.date(2026, 5, 1),
            pitch_yeast_date=datetime.date(2026, 5, 11),
        )
        with patch('apps.batches.management.commands.send_batch_notifications.send_mail') as mock_send:
            self._call_command()
            mock_send.assert_not_called()

    def test_no_email_for_user_with_no_email_address(self, db):
        u = User.objects.create_user(
            username='noemail', email='', password='pass', is_approved=True,
        )
        UserNotificationPrefs.objects.create(user=u, email_notifications=True, notify_tosna=True)
        Batch.objects.create(
            user=u,
            name='No Email Mead',
            batch_size='5.0',
            og='1.100',
            primary_date=datetime.date(2026, 6, 1),
            pitch_yeast_date=datetime.date(2026, 6, 9),
        )
        with patch('apps.batches.management.commands.send_batch_notifications.send_mail') as mock_send:
            self._call_command()
            mock_send.assert_not_called()

    def test_send_error_is_logged_not_raised(self, opted_in_user, batch_with_24h_due):
        with patch('apps.batches.management.commands.send_batch_notifications.send_mail',
                   side_effect=Exception("SMTP down")):
            with patch('apps.batches.management.commands.send_batch_notifications.logger') as mock_logger:
                self._call_command()
                mock_logger.error.assert_called_once()

    def test_bottled_batch_excluded(self, opted_in_user):
        Batch.objects.create(
            user=opted_in_user,
            name='Bottled Mead',
            batch_size='5.0',
            og='1.100',
            primary_date=datetime.date(2026, 6, 1),
            pitch_yeast_date=datetime.date(2026, 6, 9),
            bottled_done=True,
        )
        with patch('apps.batches.management.commands.send_batch_notifications.send_mail') as mock_send:
            self._call_command()
            mock_send.assert_not_called()
