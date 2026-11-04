import os
import sys
import time
import random
import getpass
import pandas as pd
from datetime import datetime

from grok_client import GrokClient
from mailer import resolve_smtp_settings, test_smtp_credentials, send_email_with_attachment

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(BASE_DIR, "input")
ATTACHMENTS_DIR = os.path.join(BASE_DIR, "attachments")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
SENT_HISTORY_FILE = os.path.join(OUTPUT_DIR, "sent_history.csv")
MANUAL_REVIEW_FILE = os.path.join(OUTPUT_DIR, "manual_review.txt")

def ensure_directories():
    os.makedirs(INPUT_DIR, exist_ok=True)
    os.makedirs(ATTACHMENTS_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_sent_emails() -> set[str]:
    """Loads previously sent emails from history file to avoid duplicates."""
    if not os.path.exists(SENT_HISTORY_FILE):
        return set()
    try:
        df = pd.read_csv(SENT_HISTORY_FILE)
        if "Email" in df.columns:
            return set(df["Email"].dropna().str.strip().str.lower().unique())
    except Exception:
        pass
    return set()

def record_sent_email(email: str, name: str, company: str, subject: str):
    """Appends successful send record to sent_history.csv."""
    file_exists = os.path.exists(SENT_HISTORY_FILE)
    with open(SENT_HISTORY_FILE, "a", encoding="utf-8") as f:
        if not file_exists:
            f.write("Timestamp,Email,Name,Company,Subject\n")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        clean_subj = subject.replace('"', '""')
        f.write(f'"{timestamp}","{email}","{name}","{company}","{clean_subj}"\n')

def log_manual_review(row_dict: dict, reason: str):
    """Appends rows with missing details to manual_review.txt."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(MANUAL_REVIEW_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] REASON: {reason}\n")
        f.write(f"RAW DATA: {row_dict}\n")
        f.write("-" * 60 + "\n")

def find_or_prompt_contacts_file() -> str:
    """Finds contacts file in input folder or asks user to provide path."""
    candidates = [
        f for f in os.listdir(INPUT_DIR)
        if f.lower().endswith((".xlsx", ".xls", ".csv")) and not f.startswith("~")
    ]
    if len(candidates) == 1:
        auto_path = os.path.join(INPUT_DIR, candidates[0])
        print(f"\n[+] Found contacts file in input folder: {candidates[0]}")
        use_auto = input("Use this file? (Y/n): ").strip().lower()
        if use_auto in ("", "y", "yes"):
            return auto_path
    elif len(candidates) > 1:
        print("\n[+] Found multiple contact files in input folder:")
        for idx, f in enumerate(candidates, start=1):
            print(f"  {idx}. {f}")
        choice = input(f"Select file (1-{len(candidates)}) or press Enter to specify custom path: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(candidates):
            return os.path.join(INPUT_DIR, candidates[int(choice) - 1])

    while True:
        path = input("\nEnter path to your .xlsx or .csv contacts file (or drag & drop here): ").strip().strip('"').strip("'")
        if os.path.isfile(path) and path.lower().endswith((".xlsx", ".xls", ".csv")):
            return path
        print("[!] File not found or unsupported format. Please provide a valid .xlsx or .csv file.")

def find_or_prompt_resume_file() -> str:
    """Finds resume in attachments folder or asks user to provide path."""
    candidates = [
        f for f in os.listdir(ATTACHMENTS_DIR)
        if f.lower().endswith(".pdf")
    ]
    if len(candidates) == 1:
        auto_path = os.path.join(ATTACHMENTS_DIR, candidates[0])
        print(f"\n[+] Found resume in attachments folder: {candidates[0]}")
        use_auto = input("Use this resume? (Y/n): ").strip().lower()
        if use_auto in ("", "y", "yes"):
            return auto_path
    elif len(candidates) > 1:
        print("\n[+] Found multiple resumes in attachments folder:")
        for idx, f in enumerate(candidates, start=1):
            print(f"  {idx}. {f}")
        choice = input(f"Select resume (1-{len(candidates)}): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(candidates):
            return os.path.join(ATTACHMENTS_DIR, candidates[int(choice) - 1])

    while True:
        path = input("\nEnter path to your Resume PDF file (or drag & drop here): ").strip().strip('"').strip("'")
        if os.path.isfile(path) and path.lower().endswith(".pdf"):
            return path
        print("[!] File not found or not a PDF. Please provide a valid .pdf file.")

def countdown_timer(seconds: int):
    """Displays human-readable cooldown between emails."""
    for remaining in range(seconds, 0, -1):
        sys.stdout.write(f"\r[*] Anti-spam safety pause: {remaining}s remaining before next email...   ")
        sys.stdout.flush()
        time.sleep(1)
    sys.stdout.write("\r" + " " * 75 + "\r")
    sys.stdout.flush()

def main():
    ensure_directories()
    print("=" * 65)
    print("          LukMailer — AI-Powered Job Outreach Bot")
    print("=" * 65)
    print("Interactive setup: Provide your credentials and preferences below.\n")

    # 1. Candidate Info
    candidate_name = input("Your Full Name: ").strip()
    while not candidate_name:
        candidate_name = input("Please enter your Full Name: ").strip()

    target_role = input("Target Job Role (e.g. Full Stack Developer, Data Analyst): ").strip()
    while not target_role:
        target_role = input("Please enter your Target Job Role: ").strip()

    # 2. Email Credentials
    print("\n--- Sender Email Configuration ---")
    sender_email = input("Your Sending Email Address: ").strip()
    while "@" not in sender_email:
        sender_email = input("Invalid email. Enter your Sending Email Address: ").strip()

    host, port = resolve_smtp_settings(sender_email)
    print(f"[*] Detected SMTP Server: {host}:{port}")

    while True:
        sender_password = getpass.getpass("Email Password / App Password (input hidden): ").strip()
        if not sender_password:
            print("[!] Password cannot be empty.")
            continue
        print("[*] Testing SMTP credentials...")
        ok, msg = test_smtp_credentials(sender_email, sender_password, host, port)
        if ok:
            print("[✓] SMTP Authentication succeeded!\n")
            break
        else:
            print(f"[✗] {msg}")
            retry = input("Retry entering password? (Y/n): ").strip().lower()
            if retry not in ("", "y", "yes"):
                print("Exiting.")
                return

    # 3. Grok API Key
    print("--- Grok (xAI) API Configuration ---")
    while True:
        grok_key = getpass.getpass("Enter your Grok (xAI) API Key (input hidden): ").strip()
        if not grok_key:
            print("[!] API key cannot be empty.")
            continue
        print("[*] Testing Grok API connection...")
        grok = GrokClient(api_key=grok_key)
        ok, msg = grok.test_connection()
        if ok:
            print(f"[✓] {msg}!\n")
            break
        else:
            print(f"[✗] Grok connection failed: {msg}")
            retry = input("Retry entering Grok API key? (Y/n): ").strip().lower()
            if retry not in ("", "y", "yes"):
                print("Exiting.")
                return

    # 4. Contacts & Resume Paths
    contacts_path = find_or_prompt_contacts_file()
    resume_path = find_or_prompt_resume_file()

    # 5. Load Data
    print(f"\n[*] Loading contacts from {os.path.basename(contacts_path)}...")
    try:
        if contacts_path.lower().endswith(".csv"):
            df = pd.read_csv(contacts_path)
        else:
            df = pd.read_excel(contacts_path)
    except Exception as e:
        print(f"[!] Error loading file: {e}")
        return

    total_rows = len(df)
    print(f"[✓] Successfully loaded {total_rows} row(s). Columns: {list(df.columns)}")

    sent_emails = load_sent_emails()
    print(f"[*] Previously sent contacts logged: {len(sent_emails)}")

    # 6. Test / Dry-Run Mode
    print("\n--- Test & Preview Mode ---")
    test_mode = input("Would you like to send a single TEST email to your own inbox first? (Y/n): ").strip().lower()
    if test_mode in ("", "y", "yes") and total_rows > 0:
        first_row = df.iloc[0].to_dict()
        print("\n[*] Asking Grok to analyze and draft for sample row...")
        draft = grok.process_and_draft(first_row, candidate_name, target_role)

        if not draft.get("valid"):
            print(f"[!] Sample row was flagged invalid by Grok: {draft.get('reason')}")
        else:
            print("\n" + "=" * 50)
            print(f"SAMPLE EXTRACTED DATA:")
            print(f"  Recipient Name : {draft.get('recipient_name')}")
            print(f"  Recipient Email: {draft.get('recipient_email')}")
            print(f"  Company        : {draft.get('company')}")
            print(f"  Subject        : {draft.get('subject')}")
            print(f"\nSAMPLE BODY PREVIEW:\n{draft.get('body')}")
            print("=" * 50)

            send_test = input(f"\nSend this preview to your email ({sender_email})? (Y/n): ").strip().lower()
            if send_test in ("", "y", "yes"):
                print("[*] Sending test email...")
                ok, send_msg = send_email_with_attachment(
                    sender_name=candidate_name,
                    sender_email=sender_email,
                    password=sender_password,
                    recipient_email=sender_email,
                    subject=f"[TEST PREVIEW] {draft.get('subject')}",
                    body_text=draft.get("body"),
                    attachment_path=resume_path,
                    host=host,
                    port=port
                )
                if ok:
                    print(f"[✓] Test email sent! Check your inbox ({sender_email}).")
                else:
                    print(f"[!] Failed to send test: {send_msg}")

    # 7. Confirmation to Dispatch
    print("\n--- Ready for Live Dispatch ---")
    confirm = input(f"Begin processing {total_rows} contacts? (y/N): ").strip().lower()
    if confirm not in ("y", "yes"):
        print("[*] Operation cancelled by user.")
        return

    # 8. Main Loop
    success_count = 0
    skipped_count = 0
    quarantine_count = 0

    print("\nStarting automated outreach pipeline...\n")
    for index, row in df.iterrows():
        row_dict = row.to_dict()
        print(f"\n--- [{index + 1}/{total_rows}] Processing contact ---")

        # Check Grok extraction
        draft = grok.process_and_draft(row_dict, candidate_name, target_role)
        if not draft.get("valid"):
            reason = draft.get("reason", "Missing critical recruiter or company info")
            print(f"[!] QUARANTINED: {reason}")
            log_manual_review(row_dict, reason)
            quarantine_count += 1
            continue

        recipient_email = draft.get("recipient_email", "").strip().lower()
        recipient_name = draft.get("recipient_name", "Hiring Team")
        company = draft.get("company", "Company")
        subject = draft.get("subject", f"Application for {target_role} - {candidate_name}")
        body = draft.get("body", "")

        # Check if already sent
        if recipient_email in sent_emails:
            print(f"[*] SKIPPED: Already sent to {recipient_email} in previous session.")
            skipped_count += 1
            continue

        # Send email
        print(f"[*] Sending to: {recipient_name} ({recipient_email}) at {company}")
        print(f"[*] Subject: {subject}")
        ok, send_msg = send_email_with_attachment(
            sender_name=candidate_name,
            sender_email=sender_email,
            password=sender_password,
            recipient_email=recipient_email,
            subject=subject,
            body_text=body,
            attachment_path=resume_path,
            host=host,
            port=port
        )

        if ok:
            print(f"[✓] Successfully sent to {recipient_email}!")
            record_sent_email(recipient_email, recipient_name, company, subject)
            sent_emails.add(recipient_email)
            success_count += 1

            # Safety delay if more rows remain
            if index < total_rows - 1:
                delay = random.randint(35, 60)
                countdown_timer(delay)
        else:
            print(f"[✗] Failed to deliver: {send_msg}")
            log_manual_review(row_dict, f"SMTP Send Error: {send_msg}")
            quarantine_count += 1

    # 9. Summary Report
    print("\n" + "=" * 65)
    print("                    OUTREACH COMPLETE")
    print("=" * 65)
    print(f"  Total Contacts Evaluated : {total_rows}")
    print(f"  Successfully Sent        : {success_count}")
    print(f"  Skipped (Already Sent)   : {skipped_count}")
    print(f"  Quarantined for Review   : {quarantine_count}")
    print(f"  Sent History Log         : {SENT_HISTORY_FILE}")
    if quarantine_count > 0:
        print(f"  Manual Review File       : {MANUAL_REVIEW_FILE}")
    print("=" * 65)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[!] Process interrupted by user. Exiting safely.")

