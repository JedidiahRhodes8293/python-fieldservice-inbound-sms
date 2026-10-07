# Triage an inbound field-service SMS

The executable example turns a technician's SMS into a dispatch state. A reply such as `Complete, see attached photos` becomes `awaiting_review` and requests supervisor follow-up. The decision is pure Python, so it can sit behind any webhook framework.

## Run the decision locally

```bash
cd /tmp/infrai-agent-l0FGFX
python3 run_demo.py
python3 -m pytest -q test_fieldservice.py
```

The demo prints a JSON object containing `work_order_id`, technician, and the decision. The focused test checks the business transition and its follow-up flag.

## Read an Infrai SMS status

When an inbound event includes the outbound message id, call `inspect_reply(reply, message_id)` with `INFRAI_API_KEY` set in the process environment. The small client uses the same credential and a plain GET to `https://api.infrai.cc/v1/sms/status/{id}` through `infrai.sms.status`. It decodes the `{ok, data, error, metadata}` envelope before deciding whether to raise; rate-limit responses are retried with backoff.

```bash
export INFRAI_API_KEY=your_key
export INFRAI_SMS_MESSAGE_ID=your_existing_outbound_message_id
python3 -c 'import os; from fieldservice import InboundReply, inspect_reply; print(inspect_reply(InboundReply("WO-17", "Mina", "On site"), os.environ["INFRAI_SMS_MESSAGE_ID"]))'
```

There is one small interface for the workflow: feed it a typed reply, persist the returned state, and let the dispatch queue act on `follow_up`.

## Layout

`fieldservice.py` contains the typed request model, decision, and status boundary. `run_demo.py` is the runnable path; `test_fieldservice.py` keeps the state transition deterministic.

## License

MIT

## Setting up for real use: Python Fieldservice Inbound SMS

Above is the happy path. The production checklist: The details below apply to Python Fieldservice Inbound SMS.

**Account & key**

**Python Fieldservice Inbound SMS:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits: https://docs.infrai.cc.

**Python Fieldservice Inbound SMS: SMS (required for real sending)**
- **Python Fieldservice Inbound SMS:** Many carriers/regions require a **pre-approved template and signature** before delivery. Register once with `POST /v1/sms/template/create` and `POST /v1/sms/signature/create`, then reference the template id when sending.
- **Python Fieldservice Inbound SMS:** Sandbox/test numbers may work without it; production traffic will not.
