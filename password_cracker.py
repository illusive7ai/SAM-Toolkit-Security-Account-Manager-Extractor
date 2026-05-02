# password_cracker_advanced.py
import os
import sys
import hashlib
import itertools
import string
import json
import random
import time
from colorama import init, Fore, Back, Style
from datetime import datetime

# Initialize colorama for Windows color support
init(autoreset=True)

class AdvancedPasswordCracker:
    def __init__(self):
        self.found_passwords = {}
        self.attempts = 0
        self.start_time = None
        self.wordlist_file = "custom_wordlist.txt"
        self.results_file = "cracking_results.json"
        
    def print_banner(self):
        """Print a professional banner with colors"""
        banner = f"""
{Fore.CYAN + Style.BRIGHT}
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║  {Fore.YELLOW}▓▓▓▓▓▓▓▓▓▓  {Fore.WHITE}ADVANCED PASSWORD CRACKER v3.0  {Fore.YELLOW}▓▓▓▓▓▓  {Fore.CYAN}
║                                                                ║
║         {Fore.GREEN}Developed by: {Fore.MAGENTA}IllusiveHacks{Fore.CYAN}                    
║         {Fore.GREEN}Purpose: {Fore.WHITE}Windows Security Research{Fore.CYAN}              
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
{Style.RESET_ALL}
"""
        print(banner)
    
    def print_success(self, message):
        """Print success messages in green"""
        print(f"{Fore.GREEN}[SUCCESS] {message}{Style.RESET_ALL}")
    
    def print_error(self, message):
        """Print error messages in red"""
        print(f"{Fore.RED}[ERROR] {message}{Style.RESET_ALL}")
    
    def print_warning(self, message):
        """Print warning messages in yellow"""
        print(f"{Fore.YELLOW}[WARNING] {message}{Style.RESET_ALL}")
    
    def print_info(self, message):
        """Print info messages in blue"""
        print(f"{Fore.BLUE}[INFO] {message}{Style.RESET_ALL}")
    
    def print_step(self, step_num, title):
        """Print step headers with colors"""
        print(f"\n{Fore.CYAN + Style.BRIGHT}┌──{'─' * 50}┐")
        print(f"│ {Fore.YELLOW}STEP {step_num}: {Fore.WHITE}{title:<40} {Fore.CYAN}│")
        print(f"└──{'─' * 50}┘{Style.RESET_ALL}")

    def calculate_ntlm_hash(self, password):
        """Calculate NTLM hash for a given password"""
        try:
            password_encoded = password.encode('utf-16le')
            md4_hash = hashlib.new('md4')
            md4_hash.update(password_encoded)
            return md4_hash.hexdigest().upper()
        except Exception as e:
            self.print_error(f"Hash calculation failed: {e}")
            return None

    def hash_to_password(self, target_hash, method="manual"):
        """Convert hash to password using specified method"""
        self.print_step(2, f"CRACKING HASH: {target_hash}")
        
        self.attempts = 0
        self.start_time = datetime.now()
        
        if method == "manual":
            return self.manual_mode_attack(target_hash)
        elif method == "ai_auto":
            return self.ai_automated_mode(target_hash)
        else:
            self.print_error("Invalid method selected")
            return None

    def manual_mode_attack(self, target_hash):
        """Manual mode with interactive wordlist management"""
        self.print_step(3, "MANUAL MODE - WORDLIST MANAGEMENT")
        
        # Load existing wordlist or create new
        wordlist = self.load_wordlist()
        
        while True:
            print(f"\n{Fore.CYAN}Current wordlist has {len(wordlist)} passwords")
            print(f"{Fore.YELLOW}Options:")
            print(f"  1. Add password to wordlist")
            print(f"  2. View current wordlist")
            print(f"  3. Clear wordlist")
            print(f"  4. Start cracking with current wordlist")
            print(f"  5. Exit manual mode")
            
            choice = input(f"\n{Fore.WHITE}Enter your choice (1-5): ").strip()
            
            if choice == "1":
                self.add_password_manual(wordlist)
            elif choice == "2":
                self.view_wordlist(wordlist)
            elif choice == "3":
                wordlist = self.clear_wordlist()
            elif choice == "4":
                password = self.crack_with_wordlist(target_hash, wordlist)
                if password:
                    return password
                else:
                    self.print_warning("Password not found in current wordlist")
            elif choice == "5":
                self.print_info("Exiting manual mode")
                return None
            else:
                self.print_error("Invalid choice")

    def add_password_manual(self, wordlist):
        """Add passwords manually through terminal"""
        self.print_info("Enter passwords one by one. Type 'done' to finish.")
        
        while True:
            password = input(f"{Fore.WHITE}Enter password (or 'done' to finish): ").strip()
            
            if password.lower() == 'done':
                break
            elif password:
                if password not in wordlist:
                    wordlist.append(password)
                    self.print_success(f"Added: {password}")
                else:
                    self.print_warning(f"Password already in wordlist: {password}")
            else:
                self.print_error("Password cannot be empty")
        
        self.save_wordlist(wordlist)

    def view_wordlist(self, wordlist):
        """Display current wordlist"""
        if not wordlist:
            self.print_warning("Wordlist is empty")
            return
        
        print(f"\n{Fore.CYAN}Current Wordlist ({len(wordlist)} passwords):")
        print("-" * 40)
        for i, password in enumerate(wordlist, 1):
            print(f"{Fore.WHITE}{i:3d}. {password}")

    def clear_wordlist(self):
        """Clear the current wordlist"""
        confirm = input(f"{Fore.YELLOW}Are you sure you want to clear the wordlist? (y/n): ").strip().lower()
        if confirm == 'y':
            self.save_wordlist([])
            self.print_success("Wordlist cleared")
            return []
        else:
            self.print_info("Wordlist clearance cancelled")
            return self.load_wordlist()

    def load_wordlist(self):
        """Load wordlist from file"""
        try:
            if os.path.exists(self.wordlist_file):
                with open(self.wordlist_file, 'r') as f:
                    return [line.strip() for line in f if line.strip()]
            return []
        except Exception as e:
            self.print_error(f"Failed to load wordlist: {e}")
            return []

    def save_wordlist(self, wordlist):
        """Save wordlist to file"""
        try:
            with open(self.wordlist_file, 'w') as f:
                for password in wordlist:
                    f.write(password + '\n')
            self.print_success(f"Wordlist saved to {self.wordlist_file}")
        except Exception as e:
            self.print_error(f"Failed to save wordlist: {e}")

    def crack_with_wordlist(self, target_hash, wordlist):
        """Crack password using provided wordlist"""
        self.print_info(f"Testing {len(wordlist)} passwords...")
        
        for i, password in enumerate(wordlist, 1):
            self.attempts += 1
            calculated_hash = self.calculate_ntlm_hash(password)
            
            if calculated_hash == target_hash:
                self.print_success(f"Password found: {password}")
                return password
            
            if i % 100 == 0:
                print(f"{Fore.CYAN}[PROGRESS] Tested {i}/{len(wordlist)} passwords...{Style.RESET_ALL}")
        
        return None

    def ai_automated_mode(self, target_hash):
        """AI Automated mode with smart password generation"""
        self.print_step(3, "AI AUTOMATED MODE - SMART PASSWORD GENERATION")
        
        # Generate passwords using different criteria
        generated_passwords = self.generate_smart_passwords()
        
        self.print_info(f"Generated {len(generated_passwords)} smart passwords")
        self.print_info("Testing against target hash...")
        
        for i, password in enumerate(generated_passwords, 1):
            self.attempts += 1
            calculated_hash = self.calculate_ntlm_hash(password)
            
            if calculated_hash == target_hash:
                self.print_success(f"Password cracked with AI: {password}")
                return password
            
            # Show progress
            if i % 5 == 0:
                print(f"{Fore.CYAN}[AI PROGRESS] Tested {i}/10 passwords...{Style.RESET_ALL}")
        
        self.print_warning("AI mode failed to crack the password")
        return None

    def generate_smart_passwords(self):
        """Generate 10 smart passwords using different criteria"""
        passwords = []
        
        # Criteria 1: Common patterns with special chars
        common_base = ["password", "admin", "user", "test", "welcome"]
        for base in common_base[:3]:
            passwords.extend([
                base + "123!",
                base.capitalize() + "123!",
                base + "!@#",
            ])
        
        # Criteria 2: Mixed case with numbers
        words = ["pass", "admin", "secure", "access", "login"]
        for word in words[:2]:
            passwords.extend([
                word + "2024!",
                word.upper() + "123",
                word.capitalize() + str(random.randint(100, 999))
            ])
        
        # Criteria 3: Special character patterns
        special_patterns = [
            "P@ssw0rd",
            "Admin@123",
            "Welcome1!",
            "Test@2024",
            "Secure#123"
        ]
        passwords.extend(special_patterns)
        
        # Ensure we have exactly 10 unique passwords
        passwords = list(set(passwords))[:10]
        
        self.print_info("AI Generated Passwords:")
        for i, pwd in enumerate(passwords, 1):
            print(f"  {Fore.WHITE}{i:2d}. {pwd}")
        
        return passwords

    def hash_cracking_menu(self):
        """Main menu for hash cracking"""
        self.print_step(1, "HASH CRACKING MODE SELECTION")
        
        print(f"\n{Fore.YELLOW}Available Modes:")
        print(f"  {Fore.CYAN}1. Manual Mode")
        print(f"    {Fore.WHITE}- Add passwords via terminal")
        print(f"    {Fore.WHITE}- Manage custom wordlist")
        print(f"    {Fore.WHITE}- Full control over password selection")
        
        print(f"  {Fore.CYAN}2. AI Automated Mode")
        print(f"    {Fore.WHITE}- AI generates 10 smart passwords")
        print(f"    {Fore.WHITE}- Different complexity criteria")
        print(f"    {Fore.WHITE}- Automated testing")
        
        print(f"  {Fore.CYAN}3. Exit")
        
        while True:
            choice = input(f"\n{Fore.WHITE}Select mode (1-3): ").strip()
            
            if choice == "1":
                return "manual"
            elif choice == "2":
                return "ai_auto"
            elif choice == "3":
                return "exit"
            else:
                self.print_error("Invalid selection")

    def get_target_hash(self):
        """Get target hash from user"""
        self.print_step(1, "TARGET HASH INPUT")
        
        print(f"\n{Fore.YELLOW}Options:")
        print(f"  1. Enter hash manually")
        print(f"  2. Use demo hash (SimplePass123!)")
        print(f"  3. Load from file")
        
        choice = input(f"\n{Fore.WHITE}Select option (1-3): ").strip()
        
        if choice == "1":
            hash_input = input(f"{Fore.WHITE}Enter the NTLM hash: ").strip().upper()
            if len(hash_input) == 32 and all(c in string.hexdigits for c in hash_input):
                return hash_input
            else:
                self.print_error("Invalid hash format. Must be 32-character hexadecimal.")
                return None
        elif choice == "2":
            demo_hash = self.calculate_ntlm_hash("SimplePass123!")
            self.print_info(f"Using demo hash: {demo_hash}")
            return demo_hash
        elif choice == "3":
            return self.load_hash_from_file()
        else:
            self.print_error("Invalid selection")
            return None

    def load_hash_from_file(self):
        """Load hash from file"""
        filename = input(f"{Fore.WHITE}Enter filename: ").strip()
        try:
            with open(filename, 'r') as f:
                hash_content = f.read().strip()
                if len(hash_content) == 32 and all(c in string.hexdigits for c in hash_content):
                    return hash_content.upper()
                else:
                    self.print_error("Invalid hash in file")
                    return None
        except Exception as e:
            self.print_error(f"Failed to load hash: {e}")
            return None

    def save_to_json(self, target_hash, password, method, attempts, time_taken):
        """Save results to JSON file"""
        result = {
            "target_hash": target_hash,
            "cracked_password": password,
            "method_used": method,
            "attempts_made": attempts,
            "time_taken": time_taken,
            "timestamp": datetime.now().isoformat(),
            "status": "SUCCESS" if password else "FAILED",
            "tool": "IllusiveHacks Advanced Password Cracker v3.0"
        }
        
        # Load existing results
        existing_results = []
        if os.path.exists(self.results_file):
            try:
                with open(self.results_file, 'r') as f:
                    existing_results = json.load(f)
            except:
                existing_results = []
        
        # Add new result
        existing_results.append(result)
        
        # Save back to file
        try:
            with open(self.results_file, 'w') as f:
                json.dump(existing_results, f, indent=2)
            self.print_success(f"Results saved to {self.results_file}")
        except Exception as e:
            self.print_error(f"Failed to save JSON results: {e}")

    def display_final_result(self, target_hash, password, method, attempts, time_taken):
        """Display final cracking result"""
        self.print_step(5, "CRACKING RESULT")
        
        if password:
            print(f"\n{Fore.GREEN + Style.BRIGHT}╔════════════════════════════════════════════════════════════════╗")
            print(f"║                      PASSWORD CRACKED!                       ║")
            print(f"╠════════════════════════════════════════════════════════════════╣")
            print(f"║ {Fore.WHITE}Hash:    {target_hash} {Fore.GREEN}║")
            print(f"║ {Fore.YELLOW}Password: {password:<30} {Fore.GREEN}                   ║")
            print(f"║ {Fore.CYAN}Method:  {method:<12} Attempts: {attempts:<8} {Fore.GREEN}          ║")
            print(f"║ {Fore.BLUE}Time:    {time_taken:<20} {Fore.GREEN}                   ║")
            print(f"╚════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.RED + Style.BRIGHT}╔════════════════════════════════════════════════════════════════╗")
            print(f"║                   CRACKING FAILED!                        ║")
            print(f"╠════════════════════════════════════════════════════════════════╣")
            print(f"║ {Fore.WHITE}Hash:    {target_hash} {Fore.RED}║")
            print(f"║ {Fore.YELLOW}Attempts: {attempts:<8} Time: {time_taken:<10} {Fore.RED}               ║")
            print(f"║ {Fore.CYAN}The password could not be cracked with current methods {Fore.RED}║")
            print(f"╚════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}")

    def run_advanced_cracker(self):
        """Main cracking workflow"""
        self.print_banner()
        
        # Get target hash
        target_hash = self.get_target_hash()
        if not target_hash:
            return
        
        # Select cracking mode
        mode = self.hash_cracking_menu()
        if mode == "exit":
            return
        
        # Start cracking
        start_time = datetime.now()
        password = self.hash_to_password(target_hash, mode)
        end_time = datetime.now()
        time_taken = str(end_time - start_time).split('.')[0]
        
        # Display and save results
        self.display_final_result(target_hash, password, mode, self.attempts, time_taken)
        self.save_to_json(target_hash, password, mode, self.attempts, time_taken)
        
        # Show completion banner
        self.print_completion_banner()

    def print_completion_banner(self):
        """Print completion banner"""
        completion_banner = f"""
{Fore.GREEN + Style.BRIGHT}
╔════════════════════════════════════════════════════════════════╗
║                    OPERATION COMPLETE!                         ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║  {Fore.CYAN}Results saved: {Fore.WHITE}{self.results_file}{Fore.GREEN}                     
║  {Fore.CYAN}Wordlist:      {Fore.WHITE}{self.wordlist_file}{Fore.GREEN}                    
║                                                                ║
║  {Fore.YELLOW}Advanced password cracking completed!{Fore.GREEN}                
║  {Fore.YELLOW}Check JSON file for detailed results{Fore.GREEN}                 
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
{Style.RESET_ALL}
"""
        print(completion_banner)

if __name__ == "__main__":
    try:
        cracker = AdvancedPasswordCracker()
        cracker.run_advanced_cracker()
        
        print(f"\n{Fore.GREEN + Style.BRIGHT}[SUCCESS] Advanced password cracking completed!{Style.RESET_ALL}")
        print(f"{Fore.CYAN}[INFO] Check '{cracker.results_file}' for JSON results.{Style.RESET_ALL}")
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[WARNING] Operation cancelled by user.{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}[ERROR] Cracking failed: {e}{Style.RESET_ALL}")