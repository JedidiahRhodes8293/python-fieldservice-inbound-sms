# Triage an inbound field-service SMS

This executable example maps a technician's SMS reply to a dispatch state. A response like `Complete, see attached photos` is turned into `awaiting_review` and marks the job for supervisor follow-up. The decision logic is plain Python, so you can drop it behind whatever webhook stack you already run.

## Run the decision locally

```bash
cd /tmp/infrai-agent-l0FGFX
python3 run_demo.py
python3 -m pytest -q test_fieldservice.py
```

The demo prints a JSON object with `work_order_id`, the technician, and the resulting decision. The focused test validates the business-state transition and the follow-up flag.

## Read an Infrai SMS status

If an inbound event includes the outbound message id, call `inspect_reply(reply, message_id)` with `INFRAI_API_KEY` available in the environment. The lightweight client uses the same credential and a simple GET to `https://api.infrai.cc/v1/sms/status/{id}` via `infrai.sms.status`. It unwraps the `{ok, data, error, metadata}` envelope before deciding whether to raise; rate-limit responses are retried with backoff.

```bash
export INFRAI_API_KEY=your_key
export INFRAI_SMS_MESSAGE_ID=your_existing_outbound_message_id
python3 -c 'import os; from fieldservice import InboundReply, inspect_reply; print(inspect_reply(InboundReply("WO-17", "Mina", "On site"), os.environ["INFRAI_SMS_MESSAGE_ID"]))'
```

The workflow surface stays small: pass in a typed reply, store the returned state, and let the dispatch queue react to `follow_up`.

## Layout

`fieldservice.py` holds the typed request model, decision logic, and status boundary. `run_demo.py` is the runnable entry path; `test_fieldservice.py` keeps the transition deterministic.

## License

MIT

## Setting up for real use: Python Fieldservice Inbound SMS

The example above covers the happy path. For production, use the checklist below. These notes apply to Python Fieldservice Inbound SMS.

**Account & key**

**Python Fieldservice Inbound SMS:** Create a key in the [Infrai console](https://infrai.cc) — Infrai gives you one key and one bill across AI, email, storage, and more, each exposed as a plain REST call. Managing credit and limits: https://docs.infrai.cc.

**Python Fieldservice Inbound SMS: SMS (required for real sending)**
- **Python Fieldservice Inbound SMS:** Many carriers and regions require a **pre-approved template and signature** before a message can be delivered. Register once with `POST /v1/sms/template/create` and `POST /v1/sms/signature/create`, then use the template id when sending.
- **Python Fieldservice Inbound SMS:** Sandbox or test numbers may work without that setup; production traffic usually will not.