import json
from fieldservice import InboundReply, inspect_reply


reply = InboundReply("WO-17", "Mina", "Complete, see attached photos", photo_count=3)
print(json.dumps(inspect_reply(reply), indent=2))
