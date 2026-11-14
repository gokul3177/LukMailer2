# LukMailer — AI-Powered HR Outreach Bot

LukMailer is a portable, terminal-based cold email automation tool designed for job seekers. It uses Grok (xAI) to automatically analyze recruiter spreadsheets (regardless of column layout), draft high-converting, personalized cold pitches, attach your resume PDF, and dispatch emails via SMTP with spam-safe delays.

---

## 🚀 Key Features

- **Flexible Operation (Interactive or Automated):** Run interactively or save your settings to a local `.env` file to skip repetitive manual prompts and send automatically.
- **Universal Spreadsheet Parsing:** Grok automatically identifies recruiter names, email addresses, companies, and roles from any `.xlsx` or `.csv` column layout.
- **Smart Quarantine Filter:** If an email is missing, malformed, or company info cannot be determined, it skips sending and logs the row to `output/manual_review.txt`.
- **Direct PDF Resume Attachment:** Automatically attaches your resume to every outgoing email.
- **Anti-Spam Human Jitter:** Enforces a 35–60 second randomized pause between emails to protect your domain and sender reputation.
- **Deduplication:** Tracks all sent messages in `output/sent_history.csv` so you never accidentally email the same recruiter twice.
- **Dry-Run / Test Mode:** Sends a test email to your own inbox first so you can inspect the draft and attachment before live sending.

---

## 📁 Folder Structure

```
d:/LukMailer/
├── input/                  <-- Drop your contacts file here (.xlsx or .csv)
├── attachments/            <-- Drop your resume.pdf here
├── output/
│   ├── sent_history.csv    <-- Log of sent outreach
│   └── manual_review.txt   <-- Quarantined contacts with missing data
├── grok_client.py          <-- Grok (xAI API) extraction & pitch generator
├── mailer.py               <-- SMTP sender & PDF attachment handler
├── main.py                 <-- Interactive CLI entry point
└── requirements.txt        <-- Python dependencies
```

---

## 🛠️ Setup & Requirements

### 1. Install Dependencies
Ensure Python 3.10+ is installed, then run:
```bash
pip install -r requirements.txt
```

### 2. Prepare Your Files
1. Copy your recruiter list (`.xlsx` or `.csv`) into `input/`.
2. Copy your resume (`.pdf`) into `attachments/`.

### 3. Google App Password (If using Gmail)
1. Go to your [Google Account Security Settings](https://myaccount.google.com/security).
2. Enable **2-Step Verification**.
3. Search for or navigate to **[App Passwords](https://myaccount.google.com/apppasswords)**.
4. Generate a new App Password named `LukMailer` (a 16-character code like `abcd efgh ijkl mnop`).
5. Use this 16-character code when prompted in the terminal.

---

## ▶️ Running the Application

In your terminal or command prompt:
```bash
cd d:\LukMailer
python main.py
```

Follow the on-screen prompts:
1. Enter your **Full Name** and **Target Role**.
2. Enter your **Sending Email** and **App Password**.
3. Enter your **Grok (xAI) API Key**.
4. Confirm detected files and opt into the **Test Preview**.
5. Confirm to begin outreach!

