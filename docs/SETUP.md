## Running locally

```bash
cd sms-forwarder-service
mkdir -p data

python3.11 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'

# start
api
# or
PYTHONPATH=src python -m api.start
```

Create a `.env` file in the project root to load configuration automatically:

```env
SMS_DB=/home/dev0/Projects/sms-forwarder-service/data/sms.db
SMS_WEBHOOK_URL=https://example.com/webhook
SMS_WEBHOOK_RETRIES=3
LOG_LEVEL=INFO
TELEMETRY_ENABLED=false
```

The app loads `.env` automatically from the repository root at startup.