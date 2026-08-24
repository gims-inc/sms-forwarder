from api.sms.webhook import WebhookService


def test_should_build_payload_without_error():
    # given
    service = WebhookService(endpoint="https://example.com/webhook")

    # when
    payload = service.build_payload(
        event="sms.saved",
        message="hello",
        sender="12345",
        device="family-phone",
        time="2026-03-04 14:41:00",
    )

    # then
    assert payload["event"] == "sms.saved"
    assert payload["sender"] == "12345"
    assert payload["device"] == "family-phone"
