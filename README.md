# 📡 SMS Forwarding customised for MPESA 

This tutorial shows you how to forward incoming SMS messages from your Android device to your own API server — allowing you to store, process, or use them in any way you want.

---
## ✨ Features

- ✅ Simple and lightweight  
- 🔒 Privacy-friendly (no data collection)  
- 🧼 Safe for Work (SFW)  
- 🤖 Android-only

---
## 📱 Installation

To begin, install the **SMS Forward** app on your Android device. It will automatically forward all incoming SMS messages to the API server you set up.

👉 [Download SMS Forward](https://play.google.com/store/apps/details?id=com.frzinapps.smsforward&pli=1)

> **Note:** The app is freemium — it includes both free and paid features. This tutorial covers free usage only.

---

# ⚙️ Run API Server Locally

You’ll need a server (a VPS or local server with public access) to receive the forwarded messages. The API code is included in this repository under the `API` folder.

### Step 1: Clone the Repository

```bash
git clone https://github.com/gims-inc/sms-forwarder
```

Go to the project directory

```bash
cd sms-forwarder/API
```

Install dependencies

```bash
python3 -m pip install -r requirements.txt
```

Start the server

```bash
uvicorn main:app --port 9999 --host 0.0.0.0
```

Congrats! You have now the API on your own server!
Now, we need to setup the [Android APP](https://play.google.com/store/apps/details?id=com.frzinapps.smsforward&pli=1) to make it runs with the **API**.


## 🚀 Deployment Guide

Now let’s connect the **SMS Forward** app with your API server.

### 📲 Step 1: Install the App

- Download and open the **SMS Forward** app  
  [SMS Forward App](https://play.google.com/store/apps/details?id=com.frzinapps.smsforward&pli=1)
- Accept the **Rules & Policies** when prompted.

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




**Step 3 — IIS setup:**

1. Open IIS Manager
2. Create a new site or application pointing to your project folder
3. Set the app pool to **No Managed Code** (since Python handles everything)
4. Give the app pool identity **read/write** permission on your project folder (so it can write the `.db` file)
5. Make sure port 80/443 is bound to your site

**Step 4 — Create the logs folder:**

```
myproject/
├── main.py
├── viewer.html
├── web.config
├── sms.db
└── logs\        ← create this folder
```

---

## Things to watch out for

**Permissions** — the IIS app pool user (`IIS AppPool\YourAppName`) needs write access to the project folder for the SQLite db. Right-click the folder → Properties → Security → Add the app pool user.

**Python path** — use the full absolute path to python.exe inside your virtualenv, e.g.:
```
C:\inetpub\wwwroot\smsapp\venv\Scripts\python.exe

```
