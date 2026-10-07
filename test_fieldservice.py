from fieldservice import InboundReply, decide_dispatch


def test_completed_reply_with_photos_requests_review():
    decision = decide_dispatch(InboundReply("WO-17", "Mina", "Complete, see attached photos", 3))
    assert decision.status == "awaiting_review"
    assert decision.follow_up is True
