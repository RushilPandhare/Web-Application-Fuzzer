# Web Application Fuzzer (WAF)

A collection of Python desktop tools with Tkinter GUIs for authorized security testing. The suite helps discover common web vulnerabilities such as SQL injection, XSS, remote code execution, parameter pollution, exposed paths, virtual host issues, and subdomains.

**Important:** Only use these tools against systems you own or have explicit written permission to test. Unauthorized scanning may be illegal.

## Features

| Tool | Script | Capabilities |
|------|--------|----------------|
| **Unified launcher** | `Virtual/hmm.py` | Menu for all fuzzers in one app |
| **URL Fuzzer** | `url.py` | SQLi, XSS, RCE, parameter pollution |
| **Hidden Directories** | `hid_dir.py` | Directory/path discovery |
| **API Endpoint Fuzzer** | `api.py` | SQLi, XSS via `input` param; auth & HTTPS checks |
| **Virtual Host Fuzzer** | `host.py` | Admin, backup, hidden, and traversal-style paths |
| **Subdomain Scanner** | `subdomains.py` | Subdomain enumeration + injection fuzzing |

## Requirements

- Python 3.10+ (3.12 recommended)
- Tkinter (usually included with Python; on some Linux installs use `python3-tk`)
- Python packages: `requests`, `dnspython` (for DNS features in `Virtual/hmm.py`)

## Installation

Clone or download the project, then from the project root:

```bash
cd /path/to/WAF

# Optional: create a virtual environment
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

pip install requests dnspython
```

> **Note:** The bundled `abc/` folder is a Windows virtual environment from another machine. On macOS or Linux, create a new `venv` as shown above instead of using `abc/`.

## Quick start

Run everything from the **project root** so wordlist files (`sql.txt`, `directories.txt`, etc.) load correctly.

### Recommended: unified launcher

```bash
python3 Virtual/hmm.py
```

Choose a fuzzer from the main menu.

### Run individual tools

```bash
python3 url.py          # URL parameter fuzzing
python3 hid_dir.py      # Hidden directory discovery
python3 api.py          # API endpoint fuzzing
python3 host.py         # Virtual host / sensitive path checks
python3 subdomains.py   # Subdomain scanning
python3 Virtual/virtual.py   # Standalone virtual host fuzzer (simpler)
```

Each command opens a GUI window.

## Project structure

```
WAF/
├── Virtual/
│   ├── hmm.py              # Main launcher (all fuzzers)
│   └── virtual.py          # Standalone virtual host fuzzer
├── url.py                  # URL parameter fuzzer
├── hid_dir.py              # Hidden directory fuzzer
├── api.py                  # API endpoint fuzzer
├── host.py                 # Virtual host fuzzer
├── subdomains.py           # Subdomain scanner
├── sql.txt                 # SQL injection payloads (url.py, subdomains.py)
├── xss.txt                 # XSS payloads
├── rce.txt                 # RCE payloads
├── param_pollution.txt     # Parameter pollution payloads
├── directories.txt         # Directory wordlist (hid_dir.py)
├── subdomains.txt          # Subdomain prefixes
├── admin_payloads.txt      # Admin paths (host.py)
├── backup_payloads.txt
├── hidden_payloads.txt
├── complex_payloads.txt
├── sql_payloads.txt        # Optional uploads for API fuzzer
├── xss_payloads.txt
└── testing_detatils.txt    # Example test targets
```

## Usage guide

### 1. URL Fuzzer (`url.py`)

Tests SQL injection, XSS, RCE, and parameter pollution by appending payloads from wordlists to your URL:

```python
requests.get(url + payload)
```

**URL format**

| Test type | Enter in URL field | Example |
|-----------|-------------------|---------|
| SQL / XSS / RCE | Base URL ending at the injection point (often after `=`) | `https://example.com/search?q=` |
| Parameter pollution | Base path without extra query | `https://example.com/page` |

- Include `http://` or `https://`, or omit the scheme to default to `http://`.
- Do **not** put attack strings in the URL field; those come from the `.txt` wordlists.

**Example**

```
https://localhost/abc.php?id=
http://localhost/def.php?user=
```

There is no manual payload field in `url.py`. Edit `sql.txt`, `xss.txt`, `rce.txt`, or `param_pollution.txt` to add payloads (one per line).

---

### 2. Hidden Directories Fuzzer (`hid_dir.py`)

Probes paths from `directories.txt` against a base URL.

**URL format:** `http(s)://host` or `http(s)://host/app` (scheme optional; defaults to `http://`).

**Example:** `https://juice-shop.herokuapp.com`

Requests are sent as: `{url}/{payload}`

---

### 3. API Endpoint Fuzzer (`api.py` or menu in `hmm.py`)

Sends payloads as the query parameter `input`:

```python
requests.get(url, params={"input": payload})
```

**API URL field:** Full endpoint URL.

```
https://example.com/api/search
http://vulnweb.com/endpoint
```

**Manual SQL payload** — raw injection string only (no URL, no `input=`):

```
' OR '1'='1
' OR 1=1 --
admin' --
```

**Manual XSS payload** — raw markup/script only:

```
<script>alert(1)</script>
"><img src=x onerror=alert(1)>
```

You can also upload `.txt` files with one payload per line (`sql_payloads.txt`, `xss_payloads.txt`).

Also checks: invalid Bearer token (improper auth) and non-HTTPS URLs.

---

### 4. Virtual Host Fuzzer (`host.py` or `Virtual/virtual.py`)

Tests paths from `admin_payloads.txt`, `backup_payloads.txt`, `hidden_payloads.txt`, and `complex_payloads.txt`.

**Base URL format:** `http(s)://host` or `http(s)://host/path`

**Example:** `http://vulnweb.com`

In `hmm.py`, **Custom Test Cases** accept one path segment per line (no leading slash):

```
admin
wp-login.php
secret
```

---

### 5. URL Fuzzer in `hmm.py` (menu item)

Different from `url.py`. Appends payloads as **path segments**:

```
{base_url}/{payload}
```

**Base URL:** `https://example.com` or `https://example.com/app`

**Manual URL payload:** path segment only, e.g. `admin`, `.env`, `backup` (not SQL/XSS strings).

---

### 6. Subdomain Scanner (`subdomains.py`)

**Domain field:** apex domain only (no `http://`).

```
example.com
rushil.com
```

Uses prefixes from `subdomains.txt` and builds URLs like `http://{prefix}.{domain}`.

---

## Wordlist file format

All payload files use **plain text, one entry per line**:

```text
' OR '1'='1
<script>alert(1)</script>
admin
wp-admin
```

Blank lines are generally ignored or skipped. Lines are trimmed with `.strip()` before use.

## Example test targets

From `testing_detatils.txt` (use only if authorized):

| Target | Suggested tool |
|--------|----------------|
| `https://juice-shop.herokuapp.com` | Hidden dirs, URL params |
| `rushil.com` | Subdomains |
| Local `abc.php`, `def.php` | URL fuzzer (`?id=`, `?user=`) |
| `vulnweb.com` | Virtual host, API |

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `FileNotFoundError` for `.txt` files | Run scripts from the project root directory |
| Tkinter / `_tkinter` missing | Install Python with Tk support or `python3-tk` |
| `abc` venv fails on Mac/Linux | Create a new `venv` and `pip install requests dnspython` |
| No results | Confirm the target is reachable, URL format matches the tool, and you have permission to test |

## Limitations

- Detection is heuristic (keyword/status-code matching), not a replacement for professional scanners.
- Results may include false positives and miss real issues.
- `subdomains.py` builds `http://` URLs only for discovered hosts.
- GUI tools use GET requests only for most injection tests.

