import tkinter as tk
from tkinter import messagebox, ttk
import requests
import concurrent.futures
import threading

# GUI Initialization
class VirtualHostFuzzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Virtual Host Fuzzer")
        self.root.geometry("600x400")
        
        # Title Label
        self.label = tk.Label(root, text="Virtual Host Fuzzer", font=("Arial", 16))
        self.label.pack(pady=10)
        
        # URL Entry
        self.url_label = tk.Label(root, text="Enter Base URL:")
        self.url_label.pack()
        self.url_entry = tk.Entry(root, width=50)
        self.url_entry.pack()

        # Start Button
        self.start_button = tk.Button(root, text="Start Fuzzing", command=self.start_fuzzing)
        self.start_button.pack(pady=10)

        # Progress Bar
        self.progress = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=10)

        # Results
        self.result_box = tk.Text(root, width=70, height=10)
        self.result_box.pack(pady=10)

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
            futures.append(executor.submit(self.test_admin_access, url, vulnerabilities))
            futures.append(executor.submit(self.test_backup_files, url, vulnerabilities))
            futures.append(executor.submit(self.test_hidden_files, url, vulnerabilities))
            futures.append(executor.submit(self.test_complex_payloads, url, vulnerabilities))

            total_tasks = len(futures)
            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                future.result()
                self.progress["value"] = ((i+1)/total_tasks) * 100
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
        with open('admin_payloads.txt', 'r') as file:
            admin_payloads = file.readlines()

        for payload in admin_payloads:
            test_url = f"{url}/{payload.strip()}"
            response = requests.get(test_url)
            if response.status_code == 200:
                vulnerabilities.append(("Admin Panel Accessible", "Restrict access to sensitive admin URLs and use proper authentication."))
                break

    def test_backup_files(self, url, vulnerabilities):
        with open('backup_payloads.txt', 'r') as file:
            backup_payloads = file.readlines()

        for payload in backup_payloads:
            test_url = f"{url}/{payload.strip()}"
            response = requests.get(test_url)
            if response.status_code == 200:
                vulnerabilities.append(("Backup Files Accessible", "Ensure that backup files are stored securely and not exposed to the public."))
                break

    def test_hidden_files(self, url, vulnerabilities):
        with open('hidden_payloads.txt', 'r') as file:
            hidden_payloads = file.readlines()

        for payload in hidden_payloads:
            test_url = f"{url}/{payload.strip()}"
            response = requests.get(test_url)
            if response.status_code == 200:
                vulnerabilities.append(("Hidden or Debug Files Accessible", "Ensure that hidden or debug files are not exposed and remove unnecessary files."))
                break

    def test_complex_payloads(self, url, vulnerabilities):
        with open('complex_payloads.txt', 'r') as file:
            complex_payloads = file.readlines()

        for payload in complex_payloads:
            test_url = f"{url}/{payload.strip()}"
            response = requests.get(test_url)
            if response.status_code == 200:
                vulnerabilities.append(("Improper Isolation or Directory Traversal", "Ensure proper isolation between web applications and restrict directory access."))
                break

# Main function to run the GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = VirtualHostFuzzerGUI(root)
    root.mainloop()
