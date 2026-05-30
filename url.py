import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import threading
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

def load_payloads(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file.readlines()]

sql_payloads = load_payloads('sql.txt')
xss_payloads = load_payloads('xss.txt')
rce_payloads = load_payloads('rce.txt')
param_pollution_payloads = load_payloads('param_pollution.txt')

def send_request(url, payload):
    try:
        response = requests.get(url + payload)
        return response.text
    except Exception as e:
        return str(e)

def check_vulnerabilities(url, payloads, keywords, progress, max_value):
    results = []
    step = 100 / max_value
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(send_request, url, payload): payload for payload in payloads}
        for future in as_completed(futures):
            payload = futures[future]
            try:
                response_text = future.result()
                for keyword in keywords:
                    if keyword in response_text:
                        results.append(f"Potential vulnerability with payload: {payload}")
                        break
            except Exception as e:
                results.append(f"Error with payload {payload}: {e}")
            progress['value'] += step
            root.update_idletasks()
    return results

def fuzz_url():
    url = url_entry.get()
    if not url:
        messagebox.showwarning("Input Error", "Please enter a URL")
        return

    if not url.startswith("http://") and not url.startswith("https://"):
        url = "http://" + url

    result_text.config(state=tk.NORMAL)
    result_text.delete(1.0, tk.END)
    progress['value'] = 0

    total_payloads = len(sql_payloads) + len(xss_payloads) + len(rce_payloads) + len(param_pollution_payloads)
    
    threading.Thread(target=run_fuzzing, args=(url, total_payloads)).start()

def run_fuzzing(url, total_payloads):
    sql_keywords = ["syntax error", "SQL syntax", "mysql_fetch_array"]
    xss_keywords = ["<script>", "javascript:", "alert("]
    rce_keywords = ["uid=", "id=", "whoami", "uname -a"]
    param_pollution_keywords = ["duplicate", "conflict", "parameter"]

    sql_results = check_vulnerabilities(url, sql_payloads, sql_keywords, progress, total_payloads)
    xss_results = check_vulnerabilities(url, xss_payloads, xss_keywords, progress, total_payloads)
    rce_results = check_vulnerabilities(url, rce_payloads, rce_keywords, progress, total_payloads)
    param_pollution_results = check_vulnerabilities(url, param_pollution_payloads, param_pollution_keywords, progress, total_payloads)

    root.after(0, update_result_text, sql_results, xss_results, rce_results, param_pollution_results)

def update_result_text(sql_results, xss_results, rce_results, param_pollution_results):
    def insert_results(title, results):
        if not results:
            result_text.insert(tk.END, f"No {title} vulnerabilities found.\n")
        else:
            result_text.insert(tk.END, "\n".join(results) + "\n")

    insert_results("SQL Injection", sql_results)
    insert_results("XSS", xss_results)
    insert_results("Remote Code Execution", rce_results)
    insert_results("Parameter Pollution", param_pollution_results)
    
    result_text.config(state=tk.DISABLED)

    # Add remediation and mitigation strategies
    remediation = {
        "SQL Injection": "Use prepared statements and parameterized queries. Validate and sanitize all user inputs.",
        "XSS": "Escape user inputs and use appropriate output encoding. Implement Content Security Policy (CSP).",
        "Remote Code Execution": "Limit the execution permissions of the application. Validate all inputs and outputs strictly.",
        "Parameter Pollution": "Validate and sanitize parameters. Implement proper input validation and use unique parameter names."
    }

    remediation_message = "\nRemediation and Mitigation Strategies:\n"
    for vuln_type, strategy in remediation.items():
        remediation_message += f"{vuln_type}:\n{strategy}\n\n"

    # Show messagebox with results and remediation
    messagebox.showinfo("Fuzzing Results and Remediation", remediation_message)
    
    # Insert the remediation strategies into the text widget
    result_text.config(state=tk.NORMAL)
    result_text.insert(tk.END, remediation_message)
    result_text.config(state=tk.DISABLED)

# GUI Setup
root = tk.Tk()
root.title("URL Fuzzer")

# Create and configure the progress bar style
style = ttk.Style(root)
style.configure("blue.Horizontal.TProgressbar",
                troughcolor='white',
                background='royalblue',  # Ensure this is the desired blue color
                thickness=20)

ttk.Label(root, text="Enter URL:").grid(row=0, column=0, padx=10, pady=10)
url_entry = ttk.Entry(root, width=50)
url_entry.grid(row=0, column=1, padx=10, pady=10)

fuzz_button = ttk.Button(root, text="Fuzz URL", command=fuzz_url)
fuzz_button.grid(row=1, column=1, pady=10)

result_text = tk.Text(root, height=20, width=80)
result_text.grid(row=2, column=0, columnspan=2, padx=10, pady=10)
result_text.config(state=tk.DISABLED)

progress = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate", style="blue.Horizontal.TProgressbar")
progress.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

root.mainloop()
