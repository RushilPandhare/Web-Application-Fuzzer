import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import requests
import concurrent.futures
import threading

# GUI Initialization
class APIFuzzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("API Endpoint Fuzzer")
        self.root.geometry("600x600")
        
        # Title Label
        self.label = tk.Label(root, text="API Endpoint Fuzzer", font=("Arial", 16))
        self.label.pack(pady=10)
        
        # URL Entry
        self.url_label = tk.Label(root, text="Enter API URL:")
        self.url_label.pack()
        self.url_entry = tk.Entry(root, width=50)
        self.url_entry.pack()

        # SQL Payload File Upload
        self.sql_file_button = tk.Button(root, text="Upload SQL Payload File", command=self.load_sql_file)
        self.sql_file_button.pack(pady=5)
        
        # XSS Payload File Upload
        self.xss_file_button = tk.Button(root, text="Upload XSS Payload File", command=self.load_xss_file)
        self.xss_file_button.pack(pady=5)
        
        # Manual SQL Payload Entry
        self.manual_sql_label = tk.Label(root, text="Enter Manual SQL Payload:")
        self.manual_sql_label.pack()
        self.manual_sql_entry = tk.Entry(root, width=50)
        self.manual_sql_entry.pack(pady=5)

        # Manual XSS Payload Entry
        self.manual_xss_label = tk.Label(root, text="Enter Manual XSS Payload:")
        self.manual_xss_label.pack()
        self.manual_xss_entry = tk.Entry(root, width=50)
        self.manual_xss_entry.pack(pady=5)

        # Start Button
        self.start_button = tk.Button(root, text="Start Fuzzing", command=self.start_fuzzing)
        self.start_button.pack(pady=10)

        # Progress Bar
        self.progress = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=10)

        # Results
        self.result_box = tk.Text(root, width=70, height=10)
        self.result_box.pack(pady=10)

        # Variables to store file paths
        self.sql_payloads_file = None
        self.xss_payloads_file = None

    def load_sql_file(self):
        self.sql_payloads_file = filedialog.askopenfilename(title="Select SQL Payload File", filetypes=(("Text Files", "*.txt"), ("All Files", "*.*")))
        if self.sql_payloads_file:
            messagebox.showinfo("File Selected", f"SQL payload file selected: {self.sql_payloads_file}")
    
    def load_xss_file(self):
        self.xss_payloads_file = filedialog.askopenfilename(title="Select XSS Payload File", filetypes=(("Text Files", "*.txt"), ("All Files", "*.*")))
        if self.xss_payloads_file:
            messagebox.showinfo("File Selected", f"XSS payload file selected: {self.xss_payloads_file}")

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

        # Using ThreadPoolExecutor to run the fuzzer tests concurrently
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(self.test_sql_injection, url, vulnerabilities),
                executor.submit(self.test_xss_attack, url, vulnerabilities),
                executor.submit(self.test_improper_auth, url, vulnerabilities),
                executor.submit(self.test_insecure_data_transmission, url, vulnerabilities)
            ]

            total_tasks = len(futures)
            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                future.result()  # Wait for the future to complete
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

    def test_sql_injection(self, url, vulnerabilities):
        # Get manual payload
        manual_payload = self.manual_sql_entry.get()

        # Load from file if present
        sql_payloads = []
        if self.sql_payloads_file:
            with open(self.sql_payloads_file, 'r') as file:
                sql_payloads = file.readlines()

        # Add manual payload to the list
        if manual_payload:
            sql_payloads.append(manual_payload)

        for payload in sql_payloads:
            response = requests.get(url, params={"input": payload.strip()})
            if any(error in response.text for error in ["SQL syntax", "mysql_fetch_array", "database error", "You have an error in your SQL"]):
                vulnerabilities.append((f"SQL Injection with payload: {payload.strip()}", "Use parameterized queries and ORM to prevent SQL injection."))
                break  # Stop after detecting the first vulnerability to save time

    def test_xss_attack(self, url, vulnerabilities):
        # Get manual payload
        manual_payload = self.manual_xss_entry.get()

        # Load from file if present
        xss_payloads = []
        if self.xss_payloads_file:
            with open(self.xss_payloads_file, 'r') as file:
                xss_payloads = file.readlines()

        # Add manual payload to the list
        if manual_payload:
            xss_payloads.append(manual_payload)

        for payload in xss_payloads:
            response = requests.get(url, params={"input": payload.strip()})
            if any(marker in response.text for marker in ["<script>", "<img", "onerror", "alert", "<iframe>"]):
                vulnerabilities.append((f"XSS Attack with payload: {payload.strip()}", "Sanitize inputs and use Content Security Policy (CSP) to prevent XSS."))
                break  # Stop after detecting the first vulnerability to save time

    def test_improper_auth(self, url, vulnerabilities):
        headers = {'Authorization': 'Bearer invalid_token'}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            vulnerabilities.append(("Improper Authentication", "Ensure proper token validation and authentication mechanisms."))

    def test_insecure_data_transmission(self, url, vulnerabilities):
        if not url.startswith("https"):
            vulnerabilities.append(("Insecure Data Transmission", "Use HTTPS for secure communication to avoid interception."))

# Main function to run the GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = APIFuzzerGUI(root)
    root.mainloop()
