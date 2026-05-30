import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import threading
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

def load_payloads(filename):
    try:
        with open(filename, 'r') as file:
            return [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        messagebox.showerror("File Error", f"Wordlist file '{filename}' not found.")
        return []

# Load directory payloads from a wordlist file (e.g., 'directories.txt')
directory_payloads = load_payloads('directories.txt')

def send_request(url, payload):
    try:
        response = requests.get(url + "/" + payload, timeout=10)  # Timeout added for hanging requests
        if response.status_code == 200:
            return f"Found: {url}/{payload}"
        elif response.status_code == 403:
            return f"Forbidden: {url}/{payload}"
        else:
            return None
    except requests.RequestException as e:
        return f"Error with payload {payload}: {e}"

def check_directories(url, payloads, progress, max_value):
    results = []
    step = 100 / max_value if max_value else 1  # Avoid division by zero
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(send_request, url, payload): payload for payload in payloads}
        for future in as_completed(futures):
            payload = futures[future]
            try:
                result = future.result()
                if result:
                    results.append(result)
            except Exception as e:
                results.append(f"Error with payload {payload}: {e}")
            progress['value'] += step
            root.update_idletasks()
    return results

def fuzz_url():
    url = url_entry.get().strip()
    if not url:
        messagebox.showwarning("Input Error", "Please enter a URL")
        return

    if not url.startswith("http://") and not url.startswith("https://"):
        url = "http://" + url

    result_text.config(state=tk.NORMAL)
    result_text.delete(1.0, tk.END)
    progress['value'] = 0

    threading.Thread(target=run_fuzzing, args=(url, len(directory_payloads))).start()

def run_fuzzing(url, total_payloads):
    if not directory_payloads:
        root.after(0, update_result_text, ["No payloads to test."])
        return

    results = check_directories(url, directory_payloads, progress, total_payloads)
    root.after(0, update_result_text, results)

def update_result_text(results):
    result_text.config(state=tk.NORMAL)
    if not results:
        result_text.insert(tk.END, "No hidden directories found.\n")
    else:
        result_text.insert(tk.END, "\n".join(results) + "\n")
    result_text.config(state=tk.DISABLED)

# GUI Setup
root = tk.Tk()
root.title("Hidden Directory Fuzzer")

# Configure the grid to be responsive
root.grid_rowconfigure(2, weight=1)
root.grid_columnconfigure(1, weight=1)

ttk.Label(root, text="Enter URL:").grid(row=0, column=0, padx=10, pady=10, sticky="W")
url_entry = ttk.Entry(root, width=50)
url_entry.grid(row=0, column=1, padx=10, pady=10, sticky="EW")

fuzz_button = ttk.Button(root, text="Fuzz URL", command=fuzz_url)
fuzz_button.grid(row=1, column=1, pady=10, sticky="E")

result_text = tk.Text(root, height=20, width=80)
result_text.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="NSEW")
result_text.config(state=tk.DISABLED)

# Progress bar
progress = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate", style="green.Horizontal.TProgressbar")
progress.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="EW")

style = ttk.Style(root)
style.configure("green.Horizontal.TProgressbar", troughcolor='white', background='green')

root.mainloop()
