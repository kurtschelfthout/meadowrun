import datetime
from pprint import pprint
from typing import Tuple, List

import pytz
import threading
import time
import asyncio

from nextbeat.time_event_publisher import (
    TimeEventPublisher,
    TimeOfDayPayload,
    _timedelta_to_str,
    PytzTzInfo,
)
import nextbeat.event_log


# these need to be tuned to make the tests run fast, but avoid false negatives
_TIME_DELAY = 0.1
_TIME_INCREMENT = datetime.timedelta(seconds=1)


def test_call_at():
    # this uses the higher level interface (TimeEventPublisher) but mostly tests the low
    # level functionality of _CallAt and whether it's robust to different
    # sequences of events

    # test basic callback functionality

    event_loop = asyncio.new_event_loop()

    event_log = nextbeat.event_log.EventLog(event_loop)
    p = TimeEventPublisher(event_loop, event_log.append_event)
    now = pytz.utc.localize(datetime.datetime.utcnow())

    task = event_loop.create_task(p.main_loop())
    threading.Thread(
        target=lambda: event_loop.run_until_complete(task), daemon=True
    ).start()

    try:
        p.point_in_time_trigger(now)  # called
        p.point_in_time_trigger(now - _TIME_INCREMENT)  # called
        p.point_in_time_trigger(now + 3 * _TIME_INCREMENT)  # not called

        time.sleep(_TIME_DELAY)
        assert len(event_log._event_log) == 2

        now = pytz.utc.localize(datetime.datetime.utcnow())
        p.point_in_time_trigger(now)  # called

        time.sleep(_TIME_DELAY)
        assert len(event_log._event_log) == 3

        p.point_in_time_trigger(now + 3 * _TIME_INCREMENT)  # not called
        p.point_in_time_trigger(now - _TIME_INCREMENT)  # called

        time.sleep(_TIME_DELAY)

        assert len(event_log._event_log) == 4
    finally:
        task.cancel()


def test_call_at_callbacks_before_running():
    # test adding callbacks before running

    event_loop = asyncio.new_event_loop()

    event_log = nextbeat.event_log.EventLog(event_loop)
    p = TimeEventPublisher(event_loop, event_log.append_event)
    now = pytz.utc.localize(datetime.datetime.utcnow())

    p.point_in_time_trigger(now)  # called
    p.point_in_time_trigger(now - _TIME_INCREMENT)  # called
    p.point_in_time_trigger(now + _TIME_INCREMENT)  # not called

    assert len(event_log._event_log) == 0

    task = event_loop.create_task(p.main_loop())
    threading.Thread(
        target=lambda: event_loop.run_until_complete(task), daemon=True
    ).start()

    try:
        time.sleep(_TIME_DELAY)

        assert len(event_log._event_log) == 2
    finally:
        task.cancel()


def _dt_to_str(dt):
    return dt.strftime("%Y-%m-%d-%H-%M-%S-%f-%z-%Z")


def _date_to_str(dt):
    return dt.strftime("%Y-%m-%d")


def test_time_event_publisher_point_in_time():
    """Test TimeEventPublisher.point_in_time_trigger"""
    event_loop = asyncio.new_event_loop()

    event_log = nextbeat.event_log.EventLog(event_loop)
    p = TimeEventPublisher(event_loop, event_log.append_event)
    now = pytz.utc.localize(datetime.datetime.utcnow())

    task = event_loop.create_task(p.main_loop())
    threading.Thread(
        target=lambda: event_loop.run_until_complete(task), daemon=True
    ).start()

    try:
        tz_ldn = pytz.timezone("Europe/London")
        tz_ny = pytz.timezone("America/New_York")
        tz_la = pytz.timezone("America/Los_Angeles")

        dts = [
            now.astimezone(tz_ny) - _TIME_INCREMENT,
            now.astimezone(tz_la) + _TIME_INCREMENT,
            now.astimezone(tz_ldn) + _TIME_INCREMENT,
            now.astimezone(tz_ldn) + 2 * _TIME_INCREMENT,
        ]

        for dt in dts:
            p.point_in_time_trigger(dt)

        # It's important to compare the results in string format because we care about
        # what timezone a datetime is in, and datetime equality does not care about the
        # timezone
        dt_strings = [_dt_to_str(dt) for dt in dts]

        time.sleep(_TIME_DELAY)

        assert 1 == len(event_log._event_log)
        assert dt_strings[0] == _dt_to_str(event_log._event_log[0].payload)

        time.sleep(_TIME_INCREMENT.total_seconds())

        assert 3 == len(event_log._event_log)
        # make sure that 2 times with the same point in time but different timezones
        # create separate events
        assert 3 == len(event_log._topic_name_to_events)
        assert set(dt_strings[:3]) == set(
            _dt_to_str(e.payload) for e in event_log._event_log
        )

        time.sleep(_TIME_INCREMENT.total_seconds())

        assert 4 == len(event_log._event_log)
        assert set(dt_strings) == set(
            _dt_to_str(e.payload) for e in event_log._event_log
        )

        pprint(dt_strings)
    finally:
        task.cancel()


def test_time_event_publisher_time_of_day():
    """Test TimeEventPublisher.time_of_day_trigger"""
    _test_time_event_publisher_time_of_day()


def test_time_event_publisher_time_of_day_daylight_savings():
    """
    Test TimeEventPublisher.time_of_day_trigger in a case where we're crossing a
    daylight savings boundary.
    """

    # New Zealand daylight savings time ended on 2021-04-04 at 3am, clocks turned
    # backward 1 hour at that point
    test_dt = pytz.timezone("Pacific/Auckland").localize(
        datetime.datetime(2021, 4, 4, 14, 0, 0)
    )
    nextbeat.time_event_publisher._TEST_TIME_OFFSET = test_dt.timestamp() - time.time()
    try:
        _test_time_event_publisher_time_of_day()
    finally:
        nextbeat.time_event_publisher._TEST_TIME_OFFSET = 0


def _test_time_event_publisher_time_of_day():
    event_loop = asyncio.new_event_loop()

    event_log = nextbeat.event_log.EventLog(event_loop)
    p = TimeEventPublisher(event_loop, event_log.append_event)

    task = event_loop.create_task(p.main_loop())
    threading.Thread(
        target=lambda: event_loop.run_until_complete(task), daemon=True
    ).start()

    try:
        tz_hi = pytz.timezone("Pacific/Honolulu")
        tz_nz = pytz.timezone("Pacific/Auckland")

        now = nextbeat.time_event_publisher._utc_now()
        now_rounded = (
            datetime.datetime(
                year=now.year,
                month=now.month,
                day=now.day,
                hour=now.hour,
                minute=now.minute,
                second=now.second,
                tzinfo=now.tzinfo,
            )
            + datetime.timedelta(seconds=1)
        )

        # this should make sure we're very close to now_rounded and possibly a little
        # bit after it
        time.sleep(
            max(now_rounded.timestamp() - nextbeat.time_event_publisher._time_time(), 0)
        )

        day_delta = datetime.timedelta(days=1)

        now_hi = now_rounded.astimezone(tz_hi)
        today_hi = now_hi.date()
        today_dt_hi = tz_hi.localize(
            datetime.datetime.combine(today_hi, datetime.time())
        )
        yesterday_dt_hi = tz_hi.localize(
            datetime.datetime.combine(today_hi - day_delta, datetime.time())
        )
        tomorrow_dt_hi = tz_hi.localize(
            datetime.datetime.combine(today_hi + day_delta, datetime.time())
        )

        now_nz = now_rounded.astimezone(tz_nz)
        today_nz = now_nz.date()
        today_dt_nz = tz_nz.localize(
            datetime.datetime.combine(today_nz, datetime.time())
        )
        yesterday_dt_nz = tz_nz.localize(
            datetime.datetime.combine(today_nz - day_delta, datetime.time())
        )
        tomorrow_dt_nz = tz_nz.localize(
            datetime.datetime.combine(today_nz + day_delta, datetime.time())
        )

        expected_payloads: List[Tuple[str, str, str, str]] = []

        def payload_to_strs(payload: TimeOfDayPayload) -> Tuple[str, str, str, str]:
            return (
                _timedelta_to_str(payload.local_time_of_day),
                payload.time_zone.zone,
                _date_to_str(payload.date),
                _dt_to_str(payload.point_in_time),
            )

        def add_trigger_and_payload(
            # the current time in the local timezone
            now_local: datetime.datetime,
            # midnight of the date you want to trigger for in the local timezone
            date_dt_local: datetime.datetime,
            # any jitter you want to add
            time_increment: datetime.timedelta,
            # the local timezone
            time_zone: PytzTzInfo,
        ):
            time_of_day = now_local - date_dt_local + time_increment
            p.time_of_day_trigger(time_of_day, time_zone)
            expected_payloads.append(
                (
                    _timedelta_to_str(time_of_day),
                    time_zone.zone,
                    _date_to_str(date_dt_local.date()),
                    _dt_to_str(time_zone.normalize(date_dt_local + time_of_day)),
                )
            )

        # not called
        p.time_of_day_trigger(now_hi - today_dt_hi - 3 * _TIME_INCREMENT, tz_hi)
        p.time_of_day_trigger(now_nz - today_dt_nz - 3 * _TIME_INCREMENT, tz_nz)

        add_trigger_and_payload(now_hi, today_dt_hi, _TIME_INCREMENT, tz_hi)
        # duplicate should be ignored
        p.time_of_day_trigger(now_hi - today_dt_hi + _TIME_INCREMENT, tz_hi)
        add_trigger_and_payload(now_hi, yesterday_dt_hi, _TIME_INCREMENT, tz_hi)
        add_trigger_and_payload(now_nz, tomorrow_dt_nz, _TIME_INCREMENT, tz_nz)

        add_trigger_and_payload(now_hi, tomorrow_dt_hi, 2 * _TIME_INCREMENT, tz_hi)
        add_trigger_and_payload(now_nz, today_dt_nz, 2 * _TIME_INCREMENT, tz_nz)
        add_trigger_and_payload(now_nz, yesterday_dt_nz, 2 * _TIME_INCREMENT, tz_nz)

        assert 0 == len(event_log._event_log)

        time.sleep(_TIME_INCREMENT.total_seconds() + _TIME_DELAY)

        assert 3 == len(event_log._event_log)
        assert set(expected_payloads[:3]) == set(
            payload_to_strs(e.payload) for e in event_log._event_log
        )

        time.sleep(_TIME_INCREMENT.total_seconds())
        assert 6 == len(event_log._event_log)
        assert set(expected_payloads) == set(
            payload_to_strs(e.payload) for e in event_log._event_log
        )

        pprint(expected_payloads)
    finally:
        task.cancel()