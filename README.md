# SMS Forwarder Service

A small API service for receiving forwarded SMS entries, storing them in SQLite, exposing them for viewing, and sending webhook notifications.

>Customised for MPESA 


## Features

- FastAPI app built with router-based structure
- SQLite persistence
- Basic request and service logging
- OpenTelemetry monitoring hooks
- Webhook support through HTTP POST requests

## Run locally

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

## Run with Docker

```bash
docker compose up --build
```

## 🚀 Deployment Guide

Now let’s connect the **SMS Forward** app with your API server.

### 📲 Step 1: Install the App

- Download and open the **SMS Forward** app  
  [SMS Forward App](https://play.google.com/store/apps/details?id=com.frzinapps.smsforward&pli=1)
- Accept the **Rules & Policies** when prompted.

> **Note:** The app is freemium — it includes both free and paid features. This tutorial covers free usage only.


### ⚙️ Step 2: Set Up a Forwarding Rule

1. Tap the **"+"** button at the bottom of the home screen.
2. Choose **"Incoming SMS/RCS"** as the trigger.
3. Tap the **"+"** icon at the top.
4. Select **"URL"** and set the method to **GET**.

### 🌐 Step 3: Enter Your API Endpoint

In the URL field, enter your server URL like this:
```http://your-server:9999/forward?msg={msg}&time={time}&in-number={in-number}&filter-name={filter-name}```

> Replace `your-server` with your actual server IP or domain.

### ✅ Step 4: Finalize

- Tap **"OK"** to save the action.
- Tap **"Next"** until you reach the **Summary** screen.
- Tap **"Done"** to complete the setup.

## 📥 View Received Messages

Once set up, all forwarded SMS messages will be stored in memory and viewable at:

```http://your-server:9999/messages```

## 🎉 Done!

You’re now forwarding SMS messages from your Android device to your own FastAPI server.


Want to expand this project? Add database support, or anything you want! — feel free to contribute or open issues! 


## Health check

```bash
curl http://localhost:8000/health
```

## Environment variables

- `SMS_DB` - SQLite database path
- `SMS_WEBHOOK_URL` - optional webhook endpoint
- `SMS_WEBHOOK_RETRIES` - retry count for webhook delivery
- `LOG_LEVEL` - logging level, such as INFO or DEBUG
- `TELEMETRY_ENABLED` - set to `true` to enable telemetry
- `TELEMETRY_EXPORTER_ENDPOINT` - OTLP exporter endpoint
