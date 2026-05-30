import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import threading
import requests
import concurrent.futures
import socket
from urllib.parse import urlparse
import dns.resolver
import os

class WebAppFuzzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Web Application Fuzzer")
        self.root.geometry("600x400")

        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Title Label
        self.label = tk.Label(self.main_frame, text="Web Application Fuzzer", font=("Arial", 20, "bold"), fg="blue")
        self.label.pack(pady=20)

        # Buttons for choosing fuzzer
        self.api_button = tk.Button(self.main_frame, text="API Endpoints Fuzzer", font=("Arial", 14), width=30, height=2, bg="lightgreen", command=self.open_api_fuzzer)
        self.api_button.pack(pady=10)

        self.vhost_button = tk.Button(self.main_frame, text="Virtual Host Fuzzer", font=("Arial", 14), width=30, height=2, bg="lightblue", command=self.open_vhost_fuzzer)
        self.vhost_button.pack(pady=10)

        self.url_fuzzer_button = tk.Button(self.main_frame, text="URL Fuzzer", font=("Arial", 14), width=30, height=2, bg="lightcoral", command=self.open_url_fuzzer)
        self.url_fuzzer_button.pack(pady=10)

        self.hidden_dirs_button = tk.Button(self.main_frame, text="Hidden Directories Fuzzer", font=("Arial", 14), width=30, height=2, bg="lightpink", command=self.open_hidden_dirs_fuzzer)
        self.hidden_dirs_button.pack(pady=10)
        
        self.subdomains_button = tk.Button(self.main_frame, text="Subdomains Fuzzer", font=("Arial", 14), width=30, height=2, bg="lightyellow", command=self.open_subdomains_fuzzer)
        self.subdomains_button.pack(pady=10)

        # Placeholders for the fuzzer GUIs
        self.api_fuzzer_gui = None
        self.vhost_fuzzer_gui = None
        self.url_fuzzer_gui = None
        self.hidden_dirs_fuzzer_gui = None
        self.subdomains_fuzzer_gui = None

    def open_api_fuzzer(self):
        if self.api_fuzzer_gui is None:
            self.api_fuzzer_gui = APIFuzzerGUI(self.root)
        self.main_frame.pack_forget()
        self.api_fuzzer_gui.frame.pack(fill=tk.BOTH, expand=True)

    def open_vhost_fuzzer(self):
        if self.vhost_fuzzer_gui is None:
            self.vhost_fuzzer_gui = VirtualHostFuzzerGUI(self.root)
        self.main_frame.pack_forget()
        self.vhost_fuzzer_gui.frame.pack(fill=tk.BOTH, expand=True)

    def open_url_fuzzer(self):
        if self.url_fuzzer_gui is None:
            self.url_fuzzer_gui = URLFuzzerGUI(self.root)
        self.main_frame.pack_forget()
        self.url_fuzzer_gui.frame.pack(fill=tk.BOTH, expand=True)

    def open_hidden_dirs_fuzzer(self):
        if self.hidden_dirs_fuzzer_gui is None:
            self.hidden_dirs_fuzzer_gui = HiddenDirectoriesFuzzerGUI(self.root)
        self.main_frame.pack_forget()
        self.hidden_dirs_fuzzer_gui.frame.pack(fill=tk.BOTH, expand=True)
        
    def open_subdomains_fuzzer(self):
        if self.subdomains_fuzzer_gui is None:
            self.subdomains_fuzzer_gui = SubdomainsFuzzerGUI(self.root)
        self.main_frame.pack_forget()
        self.subdomains_fuzzer_gui.frame.pack(fill=tk.BOTH, expand=True)


class HiddenDirectoriesFuzzerGUI:
    def __init__(self, root):
        self.root = root

        # Frame for Hidden Directories Fuzzer GUI
        self.frame = tk.Frame(root)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Title Label
        self.label = tk.Label(self.frame, text="Hidden Directories Fuzzer", font=("Arial", 16))
        self.label.pack(pady=10)

        # URL Entry
        self.url_label = tk.Label(self.frame, text="Enter URL:")
        self.url_label.pack()
        self.url_entry = tk.Entry(self.frame, width=50)
        self.url_entry.pack()

        # Load Payload Files Button
        self.load_payload_button = tk.Button(self.frame, text="Load Payload Files", command=self.load_payload_files)
        self.load_payload_button.pack(pady=5)

        # Custom Payloads Text Area
        self.custom_payload_label = tk.Label(self.frame, text="Custom Payloads:")
        self.custom_payload_label.pack()
        self.custom_payload_text = tk.Text(self.frame, height=5, width=50)
        self.custom_payload_text.pack(pady=5)

        # Fuzz URL Button
        self.fuzz_button = tk.Button(self.frame, text="Fuzz URL", command=self.fuzz_url)
        self.fuzz_button.pack(pady=10)

        # Progress Bar
        self.progress = ttk.Progressbar(self.frame, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=10)

        # Results Text Area
        self.result_text = tk.Text(self.frame, width=70, height=10)
        self.result_text.pack(pady=10)

        # Variables to store payload files and payloads
        self.payload_files = []
        self.payloads = []

    def load_payload_files(self):
        self.payload_files = filedialog.askopenfilenames(title="Select Payload Files", filetypes=[("Text files", "*.txt")])
        if self.payload_files:
            messagebox.showinfo("Files Loaded", f"Payload files loaded: {', '.join(self.payload_files)}")
            self.payloads = self._load_payloads(self.payload_files)

    def _load_payloads(self, filenames):
        payloads = []
        for filename in filenames:
            try:
                with open(filename, 'r') as file:
                    payloads.extend(line.strip() for line in file.readlines())
            except FileNotFoundError:
                messagebox.showerror("File Error", f"Payload file '{filename}' not found.")
        return payloads

    def fuzz_url(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Input Error", "Please enter a URL")
            return

        if not url.startswith("http://") and not url.startswith("https://"):
            url = "http://" + url

        if not self.payloads:
            messagebox.showwarning("No Payloads", "No payloads loaded. Please load files or add custom payloads.")
            return

        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.progress["value"] = 0

        threading.Thread(target=self.run_fuzzing, args=(url, len(self.payloads))).start()

    def run_fuzzing(self, url, total_payloads):
        results = self.check_directories(url, self.payloads, self.progress, total_payloads)
        self.root.after(0, self.update_result_text, results)

    def update_result_text(self, results):
        self.result_text.config(state=tk.NORMAL)
        if not results:
            self.result_text.insert(tk.END, "No hidden directories found.\n")
        else:
            self.result_text.insert(tk.END, "\n".join(results) + "\n")
        self.result_text.config(state=tk.DISABLED)

    def check_directories(self, url, payloads, progress, max_value):
        results = []
        step = 100 / max_value if max_value else 1  # Avoid division by zero
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(self.send_request, url, payload): payload for payload in payloads}
            for future in concurrent.futures.as_completed(futures):
                payload = futures[future]
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                except Exception as e:
                    results.append(f"Error with payload {payload}: {e}")
                progress['value'] += step
                self.root.update_idletasks()
        return results

    def send_request(self, url, payload):
        try:
            response = requests.get(url + "/" + payload, timeout=10)
            if response.status_code == 200:
                return f"Found: {url}/{payload}"
            elif response.status_code == 403:
                return f"Forbidden: {url}/{payload}"
            else:
                return None
        except requests.RequestException as e:
            return f"Error with payload {payload}: {e}"


class SubdomainsFuzzerGUI:
    def __init__(self, root):
        self.root = root

        # Frame for Subdomains Fuzzer GUI
        self.frame = tk.Frame(root)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Title Label
        self.label = tk.Label(self.frame, text="Subdomains Fuzzer", font=("Arial", 16))
        self.label.pack(pady=10)

        # Domain Entry
        self.domain_label = tk.Label(self.frame, text="Enter Domain:")
        self.domain_label.pack()
        self.domain_entry = tk.Entry(self.frame, width=50)
        self.domain_entry.pack()

        # Load Subdomain Payload Files Button
        self.load_subdomain_button = tk.Button(self.frame, text="Load Subdomain Payload Files", command=self.load_subdomain_files)
        self.load_subdomain_button.pack(pady=5)

        # Load Vulnerability Payload Files Button
        self.load_vulnerability_button = tk.Button(self.frame, text="Load Vulnerability Payload Files", command=self.load_vulnerability_files)
        self.load_vulnerability_button.pack(pady=5)

        # Custom Payloads Text Area
        self.custom_payload_label = tk.Label(self.frame, text="Custom Payloads:")
        self.custom_payload_label.pack()
        self.custom_payload_text = tk.Text(self.frame, height=5, width=50)
        self.custom_payload_text.pack(pady=5)

        # Fuzz Subdomains Button
        self.fuzz_button = tk.Button(self.frame, text="Fuzz Subdomains", command=self.fuzz_subdomains)
        self.fuzz_button.pack(pady=10)

        # Progress Bar
        self.progress = ttk.Progressbar(self.frame, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=10)

        # Results Text Area
        self.result_text = tk.Text(self.frame, width=70, height=10)
        self.result_text.pack(pady=10)

        # Variables to store files and payloads
        self.subdomain_payloads = []
        self.vulnerability_payloads = []
        self.custom_payloads = []

    def load_subdomain_files(self):
        file_paths = filedialog.askopenfilenames(title="Select Subdomain Payload Files", filetypes=[("Text files", "*.txt")])
        if file_paths:
            self.subdomain_payloads = self._load_payloads(file_paths) + self._get_custom_payloads()
            messagebox.showinfo("Files Loaded", f"Subdomain payload files loaded: {', '.join(file_paths)}")

    def load_vulnerability_files(self):
        file_paths = filedialog.askopenfilenames(title="Select Vulnerability Payload Files", filetypes=[("Text files", "*.txt")])
        if file_paths:
            self.vulnerability_payloads = self._load_payloads(file_paths) + self._get_custom_payloads()
            messagebox.showinfo("Files Loaded", f"Vulnerability payload files loaded: {', '.join(file_paths)}")

    def _load_payloads(self, filenames):
        payloads = []
        for filename in filenames:
            try:
                with open(filename, 'r') as file:
                    payloads.extend(line.strip() for line in file.readlines())
            except FileNotFoundError:
                messagebox.showerror("File Error", f"Payload file '{filename}' not found.")
        return payloads

    def _get_custom_payloads(self):
        custom_payloads = self.custom_payload_text.get("1.0", tk.END).strip().split('\n')
        return [payload.strip() for payload in custom_payloads if payload.strip()]

    def fuzz_subdomains(self):
        domain = self.domain_entry.get().strip()
        if not domain:
            messagebox.showwarning("Input Error", "Please enter a domain")
            return

        if not self.subdomain_payloads and not self.vulnerability_payloads:
            messagebox.showwarning("No Payloads", "No payloads loaded. Please load files or add custom payloads.")
            return

        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.progress["value"] = 0

        threading.Thread(target=self.run_fuzzing, args=(domain, len(self.subdomain_payloads) + len(self.vulnerability_payloads))).start()

    def run_fuzzing(self, domain, total_payloads):
        results = []

        # Check subdomains using loaded files
        if self.subdomain_payloads:
            results.extend(self.check_subdomains(domain, self.subdomain_payloads, self.progress, len(self.subdomain_payloads)))
        
        # Check vulnerabilities using loaded payloads
        if self.vulnerability_payloads:
            results.extend(self.check_vulnerabilities(domain, self.vulnerability_payloads, self.progress, len(self.vulnerability_payloads)))

        self.root.after(0, self.update_result_text, results)

    def update_result_text(self, results):
        self.result_text.config(state=tk.NORMAL)
        if not results:
            self.result_text.insert(tk.END, "No results found.\n")
        else:
            self.result_text.insert(tk.END, "\n".join(results) + "\n")
        self.result_text.config(state=tk.DISABLED)

    def check_subdomains(self, domain, payloads, progress, max_value):
        results = []
        step = 100 / max_value if max_value else 1  # Avoid division by zero

        # First, perform DNS enumeration for known subdomains
        known_subdomains = self.perform_dns_enumeration(domain)
        results.extend(known_subdomains)

        # Then, perform brute forcing for additional subdomains
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(self.resolve_subdomain, payload + "." + domain): payload for payload in payloads}
            for future in concurrent.futures.as_completed(futures):
                payload = futures[future]
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                except Exception as e:
                    results.append(f"Error with payload {payload}: {e}")
                progress['value'] += step
                self.root.update_idletasks()
        return results

    def check_vulnerabilities(self, domain, payloads, progress, max_value):
        results = []
        step = 100 / max_value if max_value else 1  # Avoid division by zero

        # Perform vulnerability testing using payloads
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(self.test_vulnerability, payload, domain): payload for payload in payloads}
            for future in concurrent.futures.as_completed(futures):
                payload = futures[future]
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                except Exception as e:
                    results.append(f"Error with payload {payload}: {e}")
                progress['value'] += step
                self.root.update_idletasks()
        return results

    def perform_dns_enumeration(self, domain):
        results = []
        resolver = dns.resolver.Resolver()
        try:
            answers = resolver.resolve(domain, "A")
            for rdata in answers:
                results.append(f"Detected: {domain} -> {rdata.address}")
        except dns.resolver.NoAnswer:
            results.append(f"No DNS records found for {domain}.")
        except dns.exception.DNSException as e:
            results.append(f"DNS Error: {e}")
        return results

    def resolve_subdomain(self, subdomain):
        try:
            ip = socket.gethostbyname(subdomain)
            return f"Found: {subdomain} -> {ip}"
        except socket.gaierror:
            return None

    def test_vulnerability(self, payload, domain):
        try:
            if "<script>" in payload:
                return f"Potential XSS vulnerability detected with payload: {payload}"
            return None
        except Exception as e:
            return f"Error with payload {payload}: {e}"


class APIFuzzerGUI:
    def __init__(self, root):
        self.root = root

        # Frame for API Fuzzer GUI
        self.frame = tk.Frame(root)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Title Label
        self.label = tk.Label(self.frame, text="API Endpoint Fuzzer", font=("Arial", 16))
        self.label.pack(pady=10)

        # URL Entry
        self.url_label = tk.Label(self.frame, text="Enter API URL:")
        self.url_label.pack()
        self.url_entry = tk.Entry(self.frame, width=50)
        self.url_entry.pack()

        # SQL Payload File Upload
        self.sql_file_button = tk.Button(self.frame, text="Upload SQL Payload File", command=self.load_sql_file)
        self.sql_file_button.pack(pady=5)

        # XSS Payload File Upload
        self.xss_file_button = tk.Button(self.frame, text="Upload XSS Payload File", command=self.load_xss_file)
        self.xss_file_button.pack(pady=5)

        # Manual SQL Payload Entry
        self.manual_sql_label = tk.Label(self.frame, text="Enter Manual SQL Payload:")
        self.manual_sql_label.pack()
        self.manual_sql_entry = tk.Entry(self.frame, width=50)
        self.manual_sql_entry.pack(pady=5)

        # Manual XSS Payload Entry
        self.manual_xss_label = tk.Label(self.frame, text="Enter Manual XSS Payload:")
        self.manual_xss_label.pack()
        self.manual_xss_entry = tk.Entry(self.frame, width=50)
        self.manual_xss_entry.pack(pady=5)

        # Start Button
        self.start_button = tk.Button(self.frame, text="Start Fuzzing", command=self.start_fuzzing)
        self.start_button.pack(pady=10)

        # Progress Bar
        self.progress = ttk.Progressbar(self.frame, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=10)

        # Results
        self.result_box = tk.Text(self.frame, width=70, height=10)
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
        if not url.startswith('https'):
            vulnerabilities.append(("Insecure Data Transmission", "Use HTTPS for secure communication."))



class URLFuzzerGUI:
    def __init__(self, root):
        self.root = root

        # Frame for URL Fuzzer GUI
        self.frame = tk.Frame(root)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Title Label
        self.label = tk.Label(self.frame, text="URL Fuzzer", font=("Arial", 16))
        self.label.pack(pady=10)

        # URL Entry
        self.url_label = tk.Label(self.frame, text="Enter URL:")
        self.url_label.pack()
        self.url_entry = tk.Entry(self.frame, width=50)
        self.url_entry.pack()

        # URL Payload File Upload
        self.url_file_button = tk.Button(self.frame, text="Upload URL Payload File", command=self.load_url_file)
        self.url_file_button.pack(pady=5)

        # Manual URL Payload Entry
        self.manual_url_label = tk.Label(self.frame, text="Enter Manual URL Payload:")
        self.manual_url_label.pack()
        self.manual_url_entry = tk.Entry(self.frame, width=50)
        self.manual_url_entry.pack(pady=5)

        # Start Button
        self.start_button = tk.Button(self.frame, text="Start Fuzzing", command=self.start_fuzzing)
        self.start_button.pack(pady=10)

        # Progress Bar
        self.progress = ttk.Progressbar(self.frame, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=10)

        # Results
        self.result_box = tk.Text(self.frame, width=70, height=10)
        self.result_box.pack(pady=10)

        # Variables to store file paths
        self.url_payloads_file = None

    def load_url_file(self):
        self.url_payloads_file = filedialog.askopenfilename(title="Select URL Payload File", filetypes=(("Text Files", "*.txt"), ("All Files", "*.*")))
        if self.url_payloads_file:
            messagebox.showinfo("File Selected", f"URL payload file selected: {self.url_payloads_file}")

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
                executor.submit(self.test_url_fuzzing, url, vulnerabilities)
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

    def test_url_fuzzing(self, url, vulnerabilities):
        # Get manual payload
        manual_payload = self.manual_url_entry.get()

        # Load from file if present
        url_payloads = []
        if self.url_payloads_file:
            with open(self.url_payloads_file, 'r') as file:
                url_payloads = file.readlines()

        # Add manual payload to the list
        if manual_payload:
            url_payloads.append(manual_payload)

        for payload in url_payloads:
            fuzzed_url = url.rstrip('/') + f"/{payload.strip()}"
            response = requests.get(fuzzed_url)
            if response.status_code == 200:
                vulnerabilities.append((f" {payload.strip()}", "Restrict access to sensitive directories, ensure proper authorization mechanisms."))
                break  # Stop after detecting the first vulnerability to save time

class VirtualHostFuzzerGUI:
    def __init__(self, root):
        self.root = root

        # Frame for Virtual Host Fuzzer GUI
        self.frame = tk.Frame(root)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Title Label
        self.label = tk.Label(self.frame, text="Virtual Host Fuzzer", font=("Arial", 16))
        self.label.pack(pady=10)

        # URL Entry
        self.url_label = tk.Label(self.frame, text="Enter Base URL:")
        self.url_label.pack()
        self.url_entry = tk.Entry(self.frame, width=60)
        self.url_entry.pack()

        # Load Payloads Button
        self.load_payloads_button = tk.Button(self.frame, text="Load Payload Files", command=self.load_payload_files, bg="lightgreen")
        self.load_payloads_button.pack(pady=5)

        # User-Defined Test Cases
        self.custom_test_label = tk.Label(self.frame, text="Custom Test Cases (one per line):")
        self.custom_test_label.pack()
        self.custom_test_cases = tk.Text(self.frame, height=5, width=60)
        self.custom_test_cases.pack(pady=5)

        # Start Button
        self.start_button = tk.Button(self.frame, text="Start Fuzzing", command=self.start_fuzzing, bg="lightblue")
        self.start_button.pack(pady=10)

        # Progress Bar
        self.progress = ttk.Progressbar(self.frame, orient="horizontal", length=600, mode="determinate")
        self.progress.pack(pady=10)

        # Results
        self.result_box = tk.Text(self.frame, width=80, height=15)
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


if __name__ == "__main__":
    root = tk.Tk()
    app = WebAppFuzzer(root)
    root.mainloop()

