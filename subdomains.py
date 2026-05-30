import tkinter as tk
from tkinter import messagebox, ttk
import requests
import concurrent.futures
import threading
import queue

class SubdomainFuzzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Subdomain Scanner and Fuzzer")
        self.root.geometry("600x500")
        
        # Title Label
        self.label = tk.Label(root, text="Subdomain Scanner and Fuzzer", font=("Arial", 16))
        self.label.pack(pady=10)
        
        # Domain Entry
        self.domain_label = tk.Label(root, text="Enter Domain:")
        self.domain_label.pack()
        self.domain_entry = tk.Entry(root, width=50)
        self.domain_entry.pack()

        # Start Button
        self.start_button = tk.Button(root, text="Start Fuzzing", command=self.start_fuzzing)
        self.start_button.pack(pady=10)

        # Progress Bar
        self.progress = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=10)

        # Results
        self.result_box = tk.Text(root, width=70, height=15)
        self.result_box.pack(pady=10)

        # Queue for thread-safe updates
        self.result_queue = queue.Queue()

    def start_fuzzing(self):
        domain = self.domain_entry.get().strip()
        if not domain:
            messagebox.showerror("Input Error", "Please enter a valid domain")
            return

        # Disable the start button to prevent multiple presses
        self.start_button.config(state=tk.DISABLED)
        
        # Start fuzzing in a separate thread
        threading.Thread(target=self.run_fuzzer, args=(domain,)).start()

    def run_fuzzer(self, domain):
        vulnerabilities = []
        subdomains = self.load_subdomains('subdomains.txt')

        # Progress reset
        self.progress["value"] = 0
        total_tasks = 5  # Number of fuzzing functions

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            futures.append(executor.submit(self.scan_subdomains, domain, subdomains, vulnerabilities))
            futures.append(executor.submit(self.fuzz_sql_injection, subdomains, vulnerabilities))
            futures.append(executor.submit(self.fuzz_xss, subdomains, vulnerabilities))
            futures.append(executor.submit(self.fuzz_rce, subdomains, vulnerabilities))
            futures.append(executor.submit(self.fuzz_param_pollution, subdomains, vulnerabilities))

            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                future.result()
                self.progress["value"] = ((i + 1) / total_tasks) * 100
                self.root.update_idletasks()

        self.result_queue.put(vulnerabilities)
        self.root.after(100, self.update_results)

    def update_results(self):
        try:
            vulnerabilities = self.result_queue.get_nowait()
        except queue.Empty:
            self.root.after(100, self.update_results)
            return

        self.show_results(vulnerabilities)
        self.start_button.config(state=tk.NORMAL)  # Enable the start button again

    def show_results(self, vulnerabilities):
        self.result_box.delete(1.0, tk.END)
        if not vulnerabilities:
            self.result_box.insert(tk.END, "No vulnerabilities found!\n")
        else:
            for vulnerability, remediation in vulnerabilities:
                self.result_box.insert(tk.END, f"Vulnerability: {vulnerability}\n")
                self.result_box.insert(tk.END, f"Remediation: {remediation}\n\n")

    def load_subdomains(self, filename):
        with open(filename, 'r') as file:
            return [line.strip() for line in file.readlines()]

    def scan_subdomains(self, domain, subdomains, vulnerabilities):
        for subdomain in subdomains:
            test_url = f"http://{subdomain}.{domain}"
            try:
                response = requests.get(test_url, timeout=3)
                if response.status_code == 200:
                    vulnerabilities.append(("Subdomain Found", f"Valid subdomain found: {test_url}"))
            except requests.exceptions.RequestException:
                continue

    def fuzz_sql_injection(self, subdomains, vulnerabilities):
        sql_payloads = self.load_payloads('sql.txt')
        for subdomain in subdomains:
            for payload in sql_payloads:
                test_url = f"http://{subdomain}{payload}"
                try:
                    response = requests.get(test_url, timeout=3)
                    if "syntax" in response.text:
                        vulnerabilities.append(("SQL Injection", f"Potential SQL Injection found on {subdomain} with payload: {payload}"))
                        break
                except requests.exceptions.RequestException:
                    continue

    def fuzz_xss(self, subdomains, vulnerabilities):
        xss_payloads = self.load_payloads('xss.txt')
        for subdomain in subdomains:
            for payload in xss_payloads:
                test_url = f"http://{subdomain}{payload}"
                try:
                    response = requests.get(test_url, timeout=3)
                    if "<script>" in response.text:
                        vulnerabilities.append(("XSS", f"Potential XSS vulnerability found on {subdomain} with payload: {payload}"))
                        break
                except requests.exceptions.RequestException:
                    continue

    def fuzz_rce(self, subdomains, vulnerabilities):
        rce_payloads = self.load_payloads('rce.txt')
        for subdomain in subdomains:
            for payload in rce_payloads:
                test_url = f"http://{subdomain}{payload}"
                try:
                    response = requests.get(test_url, timeout=3)
                    if "uid=" in response.text:
                        vulnerabilities.append(("Remote Code Execution", f"Potential RCE found on {subdomain} with payload: {payload}"))
                        break
                except requests.exceptions.RequestException:
                    continue

    def fuzz_param_pollution(self, subdomains, vulnerabilities):
        param_pollution_payloads = self.load_payloads('param_pollution.txt')
        for subdomain in subdomains:
            for payload in param_pollution_payloads:
                test_url = f"http://{subdomain}{payload}"
                try:
                    response = requests.get(test_url, timeout=3)
                    if "duplicate" in response.text:
                        vulnerabilities.append(("Parameter Pollution", f"Potential Parameter Pollution found on {subdomain} with payload: {payload}"))
                        break
                except requests.exceptions.RequestException:
                    continue

    def load_payloads(self, filename):
        with open(filename, 'r') as file:
            return [line.strip() for line in file.readlines()]

# Main function to run the GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = SubdomainFuzzerGUI(root)
    root.mainloop()
