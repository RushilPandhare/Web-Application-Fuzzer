import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import requests
import concurrent.futures
import threading
import os

# GUI Initialization
class VirtualHostFuzzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Virtual Host Fuzzer")
        self.root.geometry("800x600")
        
        # Title Label
        self.label = tk.Label(root, text="Virtual Host Fuzzer", font=("Arial", 16))
        self.label.pack(pady=10)
        
        # URL Entry
        self.url_label = tk.Label(root, text="Enter Base URL:")
        self.url_label.pack()
        self.url_entry = tk.Entry(root, width=60)
        self.url_entry.pack()

        # Load Payloads Button
        self.load_payloads_button = tk.Button(root, text="Load Payload Files", command=self.load_payload_files)
        self.load_payloads_button.pack(pady=5)
        
        # User-Defined Test Cases
        self.custom_test_label = tk.Label(root, text="Custom Test Cases (one per line):")
        self.custom_test_label.pack()
        self.custom_test_cases = tk.Text(root, height=5, width=60)
        self.custom_test_cases.pack(pady=5)

        # Start Button
        self.start_button = tk.Button(root, text="Start Fuzzing", command=self.start_fuzzing)
        self.start_button.pack(pady=10)

        # Progress Bar
        self.progress = ttk.Progressbar(root, orient="horizontal", length=600, mode="determinate")
        self.progress.pack(pady=10)

        # Results
        self.result_box = tk.Text(root, width=80, height=15)
        self.result_box.pack(pady=10)

        # Payload File Paths
        self.payload_files = {
            'admin': '',
            'backup': '',
            'hidden': '',
            'complex': ''
        }

    def load_payload_files(self):
        filepaths = filedialog.askopenfilenames(title="Select Payload Files", filetypes=[("Text files", "*.txt")])
        for filepath in filepaths:
            filename = os.path.basename(filepath)
            if "admin" in filename:
                self.payload_files['admin'] = filepath
            elif "backup" in filename:
                self.payload_files['backup'] = filepath
            elif "hidden" in filename:
                self.payload_files['hidden'] = filepath
            elif "complex" in filename:
                self.payload_files['complex'] = filepath

    def start_fuzzing(self):
        url = self.url_entry.get()
        if not url:
            messagebox.showerror("Input Error", "Please enter a valid URL")
            return

        # Start fuzzing in a separate thread
        threading.Thread(target=self.run_fuzzer, args=(url,)).start()

    def run_fuzzer(self, url):
        vulnerabilities = []

        # Progress reset
        self.progress["value"] = 0

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            if self.payload_files['admin']:
                futures.append(executor.submit(self.test_admin_access, url, vulnerabilities))
            if self.payload_files['backup']:
                futures.append(executor.submit(self.test_backup_files, url, vulnerabilities))
            if self.payload_files['hidden']:
                futures.append(executor.submit(self.test_hidden_files, url, vulnerabilities))
            if self.payload_files['complex']:
                futures.append(executor.submit(self.test_complex_payloads, url, vulnerabilities))

            # Add custom test cases
            custom_test_cases = self.custom_test_cases.get("1.0", tk.END).strip().split('\n')
            for test_case in custom_test_cases:
                if test_case:
                    futures.append(executor.submit(self.test_custom_case, url, test_case, vulnerabilities))

            total_tasks = len(futures)
            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                future.result()
                self.progress["value"] = ((i + 1) / total_tasks) * 100
                self.root.update_idletasks()

        self.show_results(vulnerabilities)

    def show_results(self, vulnerabilities):
        self.result_box.delete(1.0, tk.END)
        if not vulnerabilities:
            self.result_box.insert(tk.END, "No vulnerabilities found!\n")
        else:
            for vulnerability, remediation in vulnerabilities:
                self.result_box.insert(tk.END, f"Vulnerability: {vulnerability}\n")
                self.result_box.insert(tk.END, f"Remediation: {remediation}\n\n")

    def test_admin_access(self, url, vulnerabilities):
        if not self.payload_files['admin']:
            return
        with open(self.payload_files['admin'], 'r') as file:
            admin_payloads = file.readlines()

        for payload in admin_payloads:
            test_url = f"{url}/{payload.strip()}"
            try:
                response = requests.get(test_url, timeout=5)
                if response.status_code == 200:
                    vulnerabilities.append(("Admin Panel Accessible", "Restrict access to sensitive admin URLs and use proper authentication."))
                    break
            except requests.RequestException:
                continue

    def test_backup_files(self, url, vulnerabilities):
        if not self.payload_files['backup']:
            return
        with open(self.payload_files['backup'], 'r') as file:
            backup_payloads = file.readlines()

        for payload in backup_payloads:
            test_url = f"{url}/{payload.strip()}"
            try:
                response = requests.get(test_url, timeout=5)
                if response.status_code == 200:
                    vulnerabilities.append(("Backup Files Accessible", "Ensure that backup files are stored securely and not exposed to the public."))
                    break
            except requests.RequestException:
                continue

    def test_hidden_files(self, url, vulnerabilities):
        if not self.payload_files['hidden']:
            return
        with open(self.payload_files['hidden'], 'r') as file:
            hidden_payloads = file.readlines()

        for payload in hidden_payloads:
            test_url = f"{url}/{payload.strip()}"
            try:
                response = requests.get(test_url, timeout=5)
                if response.status_code == 200:
                    vulnerabilities.append(("Hidden or Debug Files Accessible", "Ensure that hidden or debug files are not exposed and remove unnecessary files."))
                    break
            except requests.RequestException:
                continue

    def test_complex_payloads(self, url, vulnerabilities):
        if not self.payload_files['complex']:
            return
        with open(self.payload_files['complex'], 'r') as file:
            complex_payloads = file.readlines()

        for payload in complex_payloads:
            test_url = f"{url}/{payload.strip()}"
            try:
                response = requests.get(test_url, timeout=5)
                if response.status_code == 200:
                    vulnerabilities.append(("Improper Isolation or Directory Traversal", "Ensure proper isolation between web applications and restrict directory access."))
                    break
            except requests.RequestException:
                continue

    def test_custom_case(self, url, test_case, vulnerabilities):
        test_url = f"{url}/{test_case.strip()}"
        try:
            response = requests.get(test_url, timeout=5)
            if response.status_code == 200:
                vulnerabilities.append((f"Custom Test Case Triggered: {test_case}", "Analyze the custom test case result for potential issues."))
        except requests.RequestException:
            pass

# Main function to run the GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = VirtualHostFuzzerGUI(root)
    root.mainloop()
