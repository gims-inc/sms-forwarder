from api.sms.router import parse_time


def test_should_parse_sms_time_to_sqlite_format():
    # given
    raw_value = "03/04/26, 2:41 PM"

    # when
    result = parse_time(raw_value)

    # then
    assert result == "2026-03-04 14:41:00"
