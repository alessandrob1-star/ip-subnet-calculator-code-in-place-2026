"""
IP Subnet Calculator
====================

Final Project for Code in Place (Stanford University)

Author: Alessandro Benevelli
Date: Jun 2026
Version: 1.2

Description:
    A professional IPv4 Subnet Calculator with graphical interface.
    Features:
    - Calculate subnet information
    - Subnetting (divide network into multiple subnets)
    - Automatic prefix detection
"""

import ipaddress
import json
import os
import re
import threading
import tkinter as tk
from itertools import islice
from tkinter import ttk, messagebox, scrolledtext
import urllib.error
import urllib.request
import webbrowser


MAX_SUBNETS_TO_DISPLAY = 1024
PRIVATE_IPV4_NETWORKS = tuple(
    ipaddress.ip_network(cidr)
    for cidr in ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16")
)
SHARED_IPV4_NETWORK = ipaddress.ip_network("100.64.0.0/10")
DOCUMENTATION_IPV4_NETWORKS = tuple(
    ipaddress.ip_network(cidr)
    for cidr in ("192.0.2.0/24", "198.51.100.0/24", "203.0.113.0/24")
)


def get_default_prefix(ip_str: str) -> int:
    """Calculate CIDR prefix based on trailing zero octets."""
    try:
        # Split the IP address into four decimal octets.
        octets = [int(x) for x in ip_str.split('.') if x.strip().isdigit()]
        if len(octets) != 4:
            return 24

        # Count how many octets at the end are zero.
        # This lets the program make a reasonable default CIDR guess.
        trailing_zeros = 0
        for octet in reversed(octets):
            if octet == 0:
                trailing_zeros += 1
            else:
                break

        # Examples:
        # 10.0.0.0      -> /8
        # 172.16.0.0   -> /16
        # 192.168.1.0  -> /24
        if trailing_zeros == 3:
            return 8
        elif trailing_zeros == 2:
            return 16
        elif trailing_zeros == 1:
            return 24
        else:
            return 32
    except:
        return 24


def get_ip_class(ip_str: str) -> str:
    """Return the IP Class (A, B, C, D, E)."""
    try:
        # Traditional IPv4 classes are based on the first octet.
        first = int(ip_str.split('.')[0])
        if first == 127:
            return "A (Loopback)"
        elif 1 <= first <= 126:
            return "A"
        elif 128 <= first <= 191:
            return "B"
        elif 192 <= first <= 223:
            return "C"
        elif 224 <= first <= 239:
            return "D (Multicast)"
        elif 240 <= first <= 255:
            return "E"
        return "?"
    except:
        return "?"


def get_network_scope(network: ipaddress.IPv4Network) -> str:
    """Describe the routing scope of an IPv4 network."""
    if any(network.subnet_of(private) for private in PRIVATE_IPV4_NETWORKS):
        return "Private (RFC 1918)"
    if network.subnet_of(SHARED_IPV4_NETWORK):
        return "Shared Address Space (CGNAT)"
    if any(network.subnet_of(test_net) for test_net in DOCUMENTATION_IPV4_NETWORKS):
        return "Documentation (TEST-NET)"
    if network.is_loopback:
        return "Loopback"
    if network.is_link_local:
        return "Link-local"
    if network.is_multicast:
        return "Multicast"
    if network.is_unspecified:
        return "Unspecified"
    if network.is_reserved:
        return "Reserved"
    if network.is_global:
        return "Public (globally routable)"
    return "Special-use / Non-global"


def ip_to_binary(ip_address) -> str:
    """Convert IP address to binary format."""
    # Each IPv4 octet is shown as 8 bits, because IPv4 addresses are 32 bits total.
    return '.'.join(f'{int(octet):08b}' for octet in str(ip_address).split('.'))


def is_power_of_two(value: int) -> bool:
    """Return True when value is a positive power of two."""
    return value > 0 and (value & (value - 1)) == 0


class SubnetCalculatorGUI:
    def __init__(self):
        # Create the main Tkinter window.
        self.root = tk.Tk()
        self.root.title("IP Subnet Calculator")
        self.root.geometry("1150x880")
        self.create_widgets()

    def create_widgets(self):
        # Title
        title = tk.Label(self.root, text="IP Subnet Calculator",
                        font=("Arial", 24, "bold"), fg="#1e40af")
        title.pack(pady=15)

        # The Notebook widget creates the tabbed interface.
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=20, pady=5)

        # Tab 1: calculate information about one IPv4 network.
        self.tab1 = ttk.Frame(notebook)
        notebook.add(self.tab1, text="Calculate Subnet")
        self.create_calculate_tab()

        # Tab 2: divide one network into smaller subnets.
        self.tab2 = ttk.Frame(notebook)
        notebook.add(self.tab2, text="Subnetting")
        self.create_subnetting_tab()

        # Tab 3: subnetting chatbot / AI tutor.
        self.tab3 = ttk.Frame(notebook)
        notebook.add(self.tab3, text="AI Chatbot")
        self.create_chatbot_tab()

        # Footer with links
        footer = tk.Frame(self.root)
        footer.pack(fill="x", pady=10)

        tk.Label(footer, text="Project developed by Alessandro Benevelli",
                font=("Arial", 9), fg="gray").pack()

        link_frame = tk.Frame(footer)
        link_frame.pack(pady=5)

        linkedin = tk.Label(link_frame, text="LinkedIn", fg="#0077b5",
                           cursor="hand2", font=("Arial", 10, "underline"))
        linkedin.pack(side="left", padx=15)
        linkedin.bind("<Button-1>", lambda e: webbrowser.open("https://www.linkedin.com/in/alessandrobenevelliopit/"))

        github = tk.Label(link_frame, text="GitHub", fg="#333333",
                         cursor="hand2", font=("Arial", 10, "underline"))
        github.pack(side="left", padx=15)
        github.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/alessandrob1-star"))

    def create_calculate_tab(self):
        # Build the user interface for the first tab.
        frame = ttk.Frame(self.tab1, padding=15)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Enter IP Address or Network:", font=("Arial", 11, "bold")).pack(anchor="w")
        self.entry_ip = ttk.Entry(frame, width=50, font=("Arial", 11))
        self.entry_ip.pack(pady=8)
        self.entry_ip.insert(0, "192.168.1.0")

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=12)
        ttk.Button(btn_frame, text="Calculate", command=self.calculate).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Clear", command=lambda: self.result_text1.delete(1.0, tk.END)).pack(side="left", padx=5)

        self.result_text1 = scrolledtext.ScrolledText(frame, height=27, font=("Consolas", 10))
        self.result_text1.pack(fill="both", expand=True, pady=10)

    def create_subnetting_tab(self):
        # Build the user interface for the subnetting tab.
        frame = ttk.Frame(self.tab2, padding=15)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Network to Subnet:", font=("Arial", 11, "bold")).pack(anchor="w")
        self.entry_network = ttk.Entry(frame, width=50, font=("Arial", 11))
        self.entry_network.pack(pady=8)
        self.entry_network.insert(0, "192.168.0.0")

        ttk.Label(frame, text="Number of Subnets:", font=("Arial", 11, "bold")).pack(anchor="w", pady=(10,0))
        self.entry_subnets = ttk.Entry(frame, width=25, font=("Arial", 11))
        self.entry_subnets.pack(pady=5)
        self.entry_subnets.insert(0, "8")

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=12)
        ttk.Button(btn_frame, text="Perform Subnetting", command=self.do_subnetting).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Clear", command=lambda: self.result_text2.delete(1.0, tk.END)).pack(side="left", padx=5)

        self.result_text2 = scrolledtext.ScrolledText(frame, height=27, font=("Consolas", 10))
        self.result_text2.pack(fill="both", expand=True, pady=10)

    def create_chatbot_tab(self):
        # Build the user interface for the chatbot tab.
        frame = ttk.Frame(self.tab3, padding=15)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Ask the AI Tutor about IP addresses and subnetting:",
                  font=("Arial", 11, "bold")).pack(anchor="w")

        self.chat_text = scrolledtext.ScrolledText(frame, height=27, font=("Arial", 10), wrap=tk.WORD)
        self.chat_text.pack(fill="both", expand=True, pady=10)
        self.chat_text.insert(tk.END, "AI Tutor: Hi! Ask me about CIDR, subnet masks, network IDs, broadcast addresses, or host ranges.\n\n")
        # The chat history is read-only so the user cannot accidentally edit old messages.
        self.chat_text.configure(state="disabled")

        input_frame = ttk.Frame(frame)
        input_frame.pack(fill="x", pady=5)

        self.chat_entry = ttk.Entry(input_frame, font=("Arial", 11))
        self.chat_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.chat_entry.bind("<Return>", lambda event: self.send_chat_message())

        ttk.Button(input_frame, text="Ask", command=self.send_chat_message).pack(side="left", padx=4)
        ttk.Button(input_frame, text="Clear", command=self.clear_chat).pack(side="left", padx=4)

        ttk.Label(frame, text="Works offline with a built-in subnetting tutor. Set OPENAI_API_KEY to enable online AI answers.",
                  font=("Arial", 9), foreground="gray").pack(anchor="w", pady=(5, 0))

    def calculate(self):
        # Clear previous results before showing a new calculation.
        self.result_text1.delete(1.0, tk.END)
        ip_input = self.entry_ip.get().strip()

        try:
            # Accept small user input mistakes, such as spaces or commas instead of dots.
            ip_input = ip_input.replace(" ", "").replace(",", ".")

            # If the user does not type a CIDR prefix, choose a default one.
            if '/' not in ip_input:
                prefix = get_default_prefix(ip_input)
                ip_input += f"/{prefix}"
                detected = f" (Auto-detected prefix: /{prefix})"
            else:
                detected = ""

            # strict=False allows host addresses such as 192.168.1.25/24.
            # Python converts them to the correct network: 192.168.1.0/24.
            network = ipaddress.ip_network(ip_input, strict=False)
            ip_class = get_ip_class(str(network.network_address))

            # Build the output text step by step.
            result = f"Results for → {network}{detected}\n"
            result += "="*85 + "\n\n"
            result += f"Network Address:     {network.network_address}\n"
            result += f"Broadcast Address:   {network.broadcast_address}\n"
            result += f"Subnet Mask:         {network.netmask}  (/{network.prefixlen})\n"
            result += f"                     {ip_to_binary(network.netmask)}\n"
            result += f"IP Class:            Class {ip_class}\n"
            result += f"Total IP Addresses:  {network.num_addresses:,}\n"
            result += f"Usable Hosts:        {max(0, network.num_addresses - 2):,}   (Total - 2)\n"

            if network.num_addresses > 2:
                result += f"Host Range:          {network.network_address + 1} — {network.broadcast_address - 1}\n"

            result += f"Address Scope:       {get_network_scope(network)}\n"

            self.result_text1.insert(tk.END, result)

        except Exception as e:
            messagebox.showerror("Error", f"Invalid input:\n\n{ip_input}\n\nError: {str(e)}")

    def do_subnetting(self):
        # Clear previous subnetting results.
        self.result_text2.delete(1.0, tk.END)
        ip_input = self.entry_network.get().strip()

        try:
            # The number of subnets must be an integer.
            num_subnets = int(self.entry_subnets.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number of subnets!")
            return

        try:
            # Normalize the network input before calculating.
            ip_input = ip_input.replace(" ", "").replace(",", ".")
            if '/' not in ip_input:
                prefix = get_default_prefix(ip_input)
                ip_input += f"/{prefix}"

            network = ipaddress.ip_network(ip_input, strict=False)
            ip_class = get_ip_class(str(network.network_address))

            # Very small networks do not have enough room for useful subnetting.
            if network.prefixlen >= 30:
                messagebox.showerror("Error", "Network too small for subnetting.")
                return
            if num_subnets < 2:
                messagebox.showerror("Error", "You must enter at least 2 subnets.")
                return
            if not is_power_of_two(num_subnets):
                messagebox.showerror(
                    "Error",
                    "For equal-size subnetting, the number of subnets must be a power of 2 "
                    "(for example: 2, 4, 8, or 16)."
                )
                return
            if num_subnets > MAX_SUBNETS_TO_DISPLAY:
                messagebox.showerror(
                    "Error",
                    f"This app can display at most {MAX_SUBNETS_TO_DISPLAY:,} subnets at once. "
                    "Choose fewer subnets to keep the interface responsive."
                )
                return

            # Calculate how many extra bits are needed for the requested subnets.
            # Example: 8 subnets need 3 bits, because 2^3 = 8.
            bits_needed = (num_subnets - 1).bit_length()
            new_prefix = network.prefixlen + bits_needed

            if new_prefix > 32:
                messagebox.showerror("Error", f"Cannot create {num_subnets} subnets.")
                return

            result = f"Dividing into {num_subnets} subnets with mask /{new_prefix}\n"
            result += f"Original IP Class: Class {ip_class}\n"
            result += "="*90 + "\n\n"

            # Iterate lazily so subnet objects are not all stored in memory at once.
            subnets = network.subnets(new_prefix=new_prefix)

            for i, subnet in enumerate(subnets, 1):
                # In normal IPv4 subnetting, network and broadcast are not usable hosts.
                usable = max(0, subnet.num_addresses - 2)
                result += f"Subnet {i}\n"
                result += f"   Network:           {subnet.network_address}/{subnet.prefixlen}\n"
                result += f"   Broadcast:         {subnet.broadcast_address}\n"
                result += f"   Subnet Mask:       {subnet.netmask}\n"
                result += f"                      {ip_to_binary(subnet.netmask)}\n"
                result += f"   Total IPs:         {subnet.num_addresses:,}\n"
                result += f"   Usable Hosts:      {usable:,}   (Total - 2)\n"
                result += f"   Host Range:        {subnet.network_address + 1} — {subnet.broadcast_address - 1}\n"
                result += "-"*90 + "\n\n"

            self.result_text2.insert(tk.END, result)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def send_chat_message(self):
        # Read the question from the input box.
        question = self.chat_entry.get().strip()
        if not question:
            return

        # Show the user's message immediately.
        self.chat_entry.delete(0, tk.END)
        self.add_chat_message("You", question)
        self.add_chat_message("AI Tutor", "Thinking...")

        # Run the chatbot answer in a background thread.
        # This prevents the Tkinter window from freezing while waiting.
        thread = threading.Thread(target=self.answer_chat_question, args=(question,), daemon=True)
        thread.start()

    def answer_chat_question(self, question):
        # First try the online AI API.
        answer = self.get_online_ai_response(question)
        if not answer:
            # If there is no API key, no internet, or an API error, use the offline tutor.
            answer = self.get_local_ai_response(question)
        # Tkinter widgets must be updated from the main GUI thread.
        self.root.after(0, lambda: self.replace_last_chat_message("AI Tutor", answer))

    def add_chat_message(self, speaker, message):
        # Temporarily enable the chat box so the program can insert text.
        self.chat_text.configure(state="normal")
        self.chat_text.insert(tk.END, f"{speaker}: {message}\n\n")
        self.chat_text.see(tk.END)
        self.chat_text.configure(state="disabled")

    def replace_last_chat_message(self, speaker, message):
        self.chat_text.configure(state="normal")
        content = self.chat_text.get("1.0", tk.END)
        placeholder = f"{speaker}: Thinking...\n\n"
        index = content.rfind(placeholder)
        if index != -1:
            # Replace the temporary "Thinking..." message with the real answer.
            start = f"1.0+{index}c"
            end = f"1.0+{index + len(placeholder)}c"
            self.chat_text.delete(start, end)
            self.chat_text.insert(start, f"{speaker}: {message}\n\n")
        else:
            self.chat_text.insert(tk.END, f"{speaker}: {message}\n\n")
        self.chat_text.see(tk.END)
        self.chat_text.configure(state="disabled")

    def clear_chat(self):
        # Reset the chatbot conversation area.
        self.chat_text.configure(state="normal")
        self.chat_text.delete(1.0, tk.END)
        self.chat_text.insert(tk.END, "AI Tutor: Hi! Ask me about CIDR, subnet masks, network IDs, broadcast addresses, or host ranges.\n\n")
        self.chat_text.configure(state="disabled")

    def get_online_ai_response(self, question):
        # The API key is read from an environment variable for safety.
        # This avoids saving a private key directly inside the code.
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None

        # Message sent to the online AI model.
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a friendly networking tutor inside an IPv4 subnet calculator. "
                        "Answer clearly and briefly. Focus on subnetting, CIDR, masks, network IDs, "
                        "broadcast addresses, host ranges, and IPv4 basics."
                    )
                },
                {"role": "user", "content": question}
            ],
            "temperature": 0.3,
            "max_tokens": 350
        }

        # Build a normal HTTP POST request using Python's standard library.
        request = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            },
            method="POST"
        )

        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                data = json.loads(response.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"].strip()
        except (urllib.error.URLError, urllib.error.HTTPError, KeyError, IndexError, json.JSONDecodeError):
            # Return None so the program can safely use the offline fallback.
            return None

    def get_local_ai_response(self, question):
        # Offline chatbot logic.
        # It does not use a real AI model, but it recognizes common subnetting questions.
        text = question.lower()
        network = self.extract_network_from_text(question)

        # Extract useful information from the question, if present.
        subnet_count = self.extract_subnet_count(text)
        prefix = self.extract_prefix_from_text(text)
        wants_subnetting = self.has_any(text, ["subnetting", "subnet", "subnets", "sottoreti", "dividi", "divide", "split"])

        # Example: "Divide 192.168.0.0/24 into 4 subnets"
        if network and subnet_count and wants_subnetting:
            return self.explain_subnet_split(network, subnet_count)

        # Example: "What is the network ID of 192.168.1.25/24?"
        if network:
            usable_hosts = max(0, network.num_addresses - 2)
            host_range = "No usable host range for this very small subnet."
            if network.num_addresses > 2:
                host_range = f"The usable host range is {network.network_address + 1} to {network.broadcast_address - 1}."

            return (
                f"For {network}, the network ID is {network.network_address}, "
                f"the broadcast address is {network.broadcast_address}, and the subnet mask is {network.netmask}. "
                f"It contains {network.num_addresses:,} total addresses and {usable_hosts:,} usable hosts. "
                f"{host_range}"
            )

        # Example: "How many hosts are in /26?"
        if prefix is not None and self.has_any(text, ["host", "usable", "utilizzabili", "dispositivi", "indirizzi"]):
            total_addresses = 2 ** (32 - prefix)
            usable_hosts = max(0, total_addresses - 2)
            return (
                f"A /{prefix} network has {32 - prefix} host bits. "
                f"That gives 2^{32 - prefix} = {total_addresses:,} total addresses and "
                f"{usable_hosts:,} usable hosts in normal IPv4 subnetting."
            )

        # Example: "What subnet mask is /27?"
        if prefix is not None and self.has_any(text, ["mask", "maschera"]):
            mask = ipaddress.ip_network(f"0.0.0.0/{prefix}").netmask
            return f"The subnet mask for /{prefix} is {mask}."

        if self.has_any(text, ["cidr", "prefix", "prefisso", "slash", "/"]):
            return (
                "CIDR is the slash notation after an IP address, like /24. "
                "It tells how many bits belong to the network part. For example, /24 means the first 24 bits "
                "identify the network, leaving 8 bits for hosts. More network bits means smaller subnets."
            )

        if self.has_any(text, ["mask", "subnet mask", "maschera"]):
            return (
                "A subnet mask separates the network part from the host part of an IPv4 address. "
                "For example, /24 is the same as 255.255.255.0. Bits set to 1 are network bits; "
                "bits set to 0 are host bits."
            )

        if self.has_any(text, ["network id", "network address", "id network", "indirizzo di rete", "rete"]):
            return (
                "The network ID is the first address of a subnet. It identifies the subnet itself, "
                "so it is not normally assigned to a device. Example: in 192.168.1.25/24, "
                "the network ID is 192.168.1.0."
            )

        if self.has_any(text, ["broadcast", "ultimo indirizzo"]):
            return (
                "The broadcast address is the last address of a subnet. It is used to reach every host "
                "inside that subnet, so it is not normally assigned to a device. Example: "
                "192.168.1.0/24 has broadcast address 192.168.1.255."
            )

        if self.has_any(text, ["host", "usable", "utilizzabili", "dispositivi"]):
            return (
                "Usable hosts are usually total addresses minus 2: one address for the network ID and one "
                "for broadcast. Formula: 2^(32 - prefix) - 2. For example, a /24 has "
                "2^8 = 256 total addresses and 254 usable hosts."
            )

        if self.has_any(text, ["private", "public", "privato", "pubblico"]):
            return (
                "Private IPv4 ranges are 10.0.0.0/8, 172.16.0.0/12, and 192.168.0.0/16. "
                "They are used inside local networks. Public IP addresses are routable on the internet."
            )

        if wants_subnetting:
            return (
                "Subnetting means dividing a larger network into smaller networks. "
                "You borrow bits from the host part to create more subnet IDs. "
                "More subnet bits means more subnets, but fewer hosts per subnet. Example: "
                "to split a /24 into 4 subnets, borrow 2 bits and use /26."
            )

        if self.has_any(text, ["class", "classe", "classi"]):
            return (
                "IPv4 classes are the old way to group addresses. Class A is 1-126, Class B is 128-191, "
                "Class C is 192-223, Class D is multicast, and Class E is reserved. Today, CIDR is used "
                "more often than classful addressing."
            )

        if self.has_any(text, ["binary", "binario", "bits", "bit"]):
            return (
                "IPv4 addresses are 32 bits long. They are shown as four decimal octets, but subnetting "
                "works on the binary bits. A /24 means 24 network bits and 8 host bits."
            )

        return (
            "Ask me a specific subnetting question and include an IP with CIDR when possible. "
            "Examples: 'What is the network ID of 192.168.1.25/24?', "
            "'How many hosts are in a /26?', or 'Divide 192.168.0.0/24 into 4 subnets.'"
        )

    def extract_network_from_text(self, question):
        # Find IPv4 CIDR patterns inside a sentence, such as 192.168.1.25/24.
        matches = re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}/\d{1,2}\b", question)
        for match in matches:
            try:
                # strict=False converts host addresses to their network address.
                return ipaddress.ip_network(match, strict=False)
            except ValueError:
                continue
        return None

    def extract_prefix_from_text(self, text):
        # Find a CIDR prefix written by itself, such as /26.
        match = re.search(r"/(\d{1,2})\b", text)
        if not match:
            return None
        prefix = int(match.group(1))
        if 0 <= prefix <= 32:
            return prefix
        return None

    def extract_subnet_count(self, text):
        # Look for phrases that ask for a specific number of subnets.
        patterns = [
            r"\binto\s+(\d+)\s+subnets\b",
            r"\bin\s+(\d+)\s+sottoreti\b",
            r"\b(\d+)\s+subnets\b",
            r"\b(\d+)\s+sottoreti\b",
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    return int(match.group(1))
                except ValueError:
                    return None
        return None

    def explain_subnet_split(self, network, subnet_count):
        # Explain subnetting step by step for chatbot answers.
        if subnet_count < 2:
            return "To subnet a network, choose at least 2 subnets."
        if not is_power_of_two(subnet_count):
            return (
                "Equal-size IPv4 subnetting requires a power-of-two subnet count. "
                "Choose 2, 4, 8, 16, or another power of two."
            )
        if network.prefixlen >= 30:
            return "This network is too small to divide into useful IPv4 subnets."

        # The number of borrowed bits decides the new CIDR prefix.
        bits_needed = (subnet_count - 1).bit_length()
        new_prefix = network.prefixlen + bits_needed
        if new_prefix > 32:
            return f"{network} cannot be divided into {subnet_count} IPv4 subnets."

        # The tutor shows at most four examples, so generate only those subnet objects.
        subnets = list(islice(network.subnets(new_prefix=new_prefix), 4))
        first_lines = []
        for index, subnet in enumerate(subnets, 1):
            usable = max(0, subnet.num_addresses - 2)
            first_lines.append(
                f"{index}. {subnet} | hosts: {usable:,} | range: {subnet.network_address} - {subnet.broadcast_address}"
            )

        extra = ""
        if subnet_count > 4:
            extra = f"\nI showed the first 4 subnets; the calculator tab can list all {subnet_count}."

        return (
            f"To divide {network} into {subnet_count} subnets, you need {bits_needed} extra subnet bits. "
            f"The new prefix is /{new_prefix}, so each subnet has {subnets[0].num_addresses:,} total addresses.\n"
            + "\n".join(first_lines)
            + extra
        )

    def has_any(self, text, keywords):
        # Small helper used by the offline chatbot keyword checks.
        return any(keyword in text for keyword in keywords)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = SubnetCalculatorGUI()
    app.run()
