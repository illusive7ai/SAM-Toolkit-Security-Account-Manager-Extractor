# precision_sam_parser.py
import os
import struct
import binascii
import hashlib
from colorama import init, Fore, Style

init(autoreset=True)

class PrecisionSAMParser:
    def __init__(self):
        self.backup_dir = "sam_backup_simple"
        self.sam_file = os.path.join(self.backup_dir, "SAM")
        self.system_file = os.path.join(self.backup_dir, "SYSTEM")
        
    def print_banner(self):
        banner = f"""
{Fore.CYAN + Style.BRIGHT}
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║  {Fore.YELLOW}▓▓▓▓▓▓▓▓▓▓  {Fore.WHITE}PRECISION SAM PARSER  {Fore.YELLOW}▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  {Fore.CYAN}║
║                                                                ║
║         {Fore.GREEN}Developed by: {Fore.MAGENTA}IllusiveHacks{Fore.CYAN}                    ║
║         {Fore.GREEN}Purpose: {Fore.WHITE}Precision Hash Extraction{Fore.CYAN}              ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
{Style.RESET_ALL}
"""
        print(banner)
    
    def print_success(self, message):
        print(f"{Fore.GREEN}[SUCCESS] {message}{Style.RESET_ALL}")
    
    def print_error(self, message):
        print(f"{Fore.RED}[ERROR] {message}{Style.RESET_ALL}")
    
    def print_info(self, message):
        print(f"{Fore.BLUE}[INFO] {message}{Style.RESET_ALL}")
    
    def print_step(self, step_num, title):
        print(f"\n{Fore.CYAN + Style.BRIGHT}┌──{'─' * 50}┐")
        print(f"│ {Fore.YELLOW}STEP {step_num}: {Fore.WHITE}{title:<40} {Fore.CYAN}│")
        print(f"└──{'─' * 50}┘{Style.RESET_ALL}")

    def read_binary_file(self, filepath):
        """Read binary file"""
        try:
            with open(filepath, 'rb') as f:
                return f.read()
        except Exception as e:
            self.print_error(f"Failed to read {filepath}: {e}")
            return None

    def extract_hashes_near_users(self, sam_data, user_offsets):
        """Extract hashes from precise locations near user accounts"""
        self.print_step(2, "PRECISION HASH EXTRACTION NEAR USER ACCOUNTS")
        
        user_hashes = {}
        
        try:
            # For each user account location, search nearby for hashes
            for username, offset in user_offsets.items():
                self.print_info(f"Searching for hashes near {username} at 0x{offset:08X}")
                
                # Search in the vicinity of the user account (before and after)
                search_start = max(0, offset - 500)
                search_end = min(len(sam_data), offset + 1000)
                
                hash_candidates = []
                
                # Look for 16-byte sequences that could be hashes
                for i in range(search_start, search_end - 16, 1):
                    hash_block = sam_data[i:i+16]
                    
                    # Skip empty or sequential blocks
                    if hash_block == b'\x00' * 16:
                        continue
                    
                    # Check if this looks like a real hash
                    hex_hash = binascii.hexlify(hash_block).decode('ascii').lower()
                    
                    # Real NTLM hash validation
                    if self.is_likely_ntlm_hash(hex_hash):
                        hash_candidates.append((i, hex_hash))
                
                # Take the best candidate (closest to user account)
                if hash_candidates:
                    # Sort by distance from user account
                    hash_candidates.sort(key=lambda x: abs(x[0] - offset))
                    best_offset, best_hash = hash_candidates[0]
                    
                    user_hashes[username] = {
                        'nt_hash': best_hash,
                        'offset': best_offset,
                        'lm_hash': 'aad3b435b51404eeaad3b435b51404ee',
                        'distance_from_user': abs(best_offset - offset)
                    }
                    
                    self.print_success(f"Found hash for {username}: {best_hash}")
                    self.print_info(f"  Hash offset: 0x{best_offset:08X}, Distance: {abs(best_offset - offset)} bytes")
                else:
                    self.print_error(f"No hash found near {username}")
            
            return user_hashes
            
        except Exception as e:
            self.print_error(f"Precision extraction failed: {e}")
            return {}

    def is_likely_ntlm_hash(self, hex_hash):
        """Check if a hex string looks like a real NTLM hash"""
        if len(hex_hash) != 32:
            return False
        
        # Check for common non-hash patterns
        if hex_hash.startswith('72656766'):  # 'regf'
            return False
        if hex_hash == '0' * 32:  # All zeros
            return False
        
        # Check byte distribution (real hashes have good distribution)
        bytes_list = [hex_hash[i:i+2] for i in range(0, 32, 2)]
        unique_bytes = len(set(bytes_list))
        
        # Real hashes typically have decent byte diversity
        return unique_bytes > 6

    def find_user_accounts_with_precision(self, sam_data):
        """Find user accounts with precise locations"""
        self.print_step(1, "PRECISE USER ACCOUNT LOCATION")
        
        users = {}
        
        try:
            # Look for specific user patterns with exact locations
            user_patterns = {
                'TestUser1': b'T\x00e\x00s\x00t\x00U\x00s\x00e\x00r\x001\x00',
                'Administrator': b'A\x00d\x00m\x00i\x00n\x00i\x00s\x00t\x00r\x00a\x00t\x00o\x00r\x00',
                'Guest': b'G\x00u\x00e\x00s\x00t\x00',
            }
            
            for username, pattern in user_patterns.items():
                pos = 0
                found_locations = []
                while True:
                    pos = sam_data.find(pattern, pos)
                    if pos == -1:
                        break
                    found_locations.append(pos)
                    pos += len(pattern)
                
                if found_locations:
                    # Use the first occurrence (usually the main one)
                    users[username] = found_locations[0]
                    self.print_success(f"Located {username} at 0x{found_locations[0]:08X}")
            
            return users
            
        except Exception as e:
            self.print_error(f"User location failed: {e}")
            return {}

    def calculate_ntlm_hash(self, password):
        """Calculate NTLM hash for a password"""
        try:
            password_encoded = password.encode('utf-16le')
            md4_hash = hashlib.new('md4')
            md4_hash.update(password_encoded)
            return md4_hash.hexdigest().lower()
        except:
            return None

    def crack_with_precision(self, hashes):
        """Precision cracking focusing on known passwords"""
        self.print_step(3, "PRECISION PASSWORD CRACKING")
        
        cracked = {}
        
        # Focus on the passwords we actually set
        target_passwords = {
            'TestUser1': ['SimplePass123!', 'SimplePass123', 'simplepass123!', 'SIMPLEPASS123!'],
            'Administrator': ['admin', 'Admin', 'ADMIN', 'Password1', 'Welcome1'],
            'Guest': ['', 'guest', 'Guest', '123456']
        }
        
        for username, hash_data in hashes.items():
            target_hash = hash_data['nt_hash'].lower()
            found = False
            
            # Try known passwords for this specific user
            if username in target_passwords:
                for password in target_passwords[username]:
                    calculated_hash = self.calculate_ntlm_hash(password)
                    if calculated_hash and calculated_hash == target_hash:
                        cracked[username] = password
                        self.print_success(f"✅ PRECISION CRACKED: {username} -> {password}")
                        found = True
                        break
            
            if not found:
                # Fallback to common passwords
                common_passwords = ['password', '123456', 'test', 'welcome']
                for password in common_passwords:
                    calculated_hash = self.calculate_ntlm_hash(password)
                    if calculated_hash and calculated_hash == target_hash:
                        cracked[username] = password
                        self.print_success(f"✅ COMMON PASSWORD: {username} -> {password}")
                        found = True
                        break
            
            if not found:
                self.print_error(f"❌ UNABLE TO CRACK: {username}")
                cracked[username] = "Unknown"
        
        return cracked

    def save_precision_report(self, users, hashes, cracked):
        """Save precision analysis report"""
        self.print_step(4, "GENERATING PRECISION REPORT")
        
        try:
            with open("precision_sam_analysis.txt", "w") as f:
                f.write("PRECISION SAM DATABASE ANALYSIS\n")
                f.write("=" * 70 + "\n")
                f.write("Method: Targeted extraction near user account locations\n")
                f.write("=" * 70 + "\n\n")
                
                f.write("USER ACCOUNTS AND HASH LOCATIONS:\n")
                f.write("-" * 70 + "\n")
                for username, user_offset in users.items():
                    f.write(f"{username}:\n")
                    f.write(f"  User Account Offset: 0x{user_offset:08X}\n")
                    if username in hashes:
                        hash_data = hashes[username]
                        f.write(f"  Hash Offset: 0x{hash_data['offset']:08X}\n")
                        f.write(f"  Distance: {hash_data['distance_from_user']} bytes\n")
                        f.write(f"  NT Hash: {hash_data['nt_hash']}\n")
                        f.write(f"  Status: {'CRACKED' if username in cracked and cracked[username] != 'Unknown' else 'ENCRYPTED'}\n")
                        if username in cracked:
                            f.write(f"  Password: {cracked[username]}\n")
                    else:
                        f.write(f"  Hash: NOT FOUND\n")
                    f.write("\n")
                
                f.write("TECHNICAL ANALYSIS:\n")
                f.write("-" * 70 + "\n")
                f.write("This analysis used precision targeting to locate hashes\n")
                f.write("near known user account positions in the SAM binary.\n")
                f.write("Each hash was validated and tested against likely passwords.\n")
            
            self.print_success("Precision report saved: precision_sam_analysis.txt")
            
        except Exception as e:
            self.print_error(f"Report save failed: {e}")

    def display_precision_results(self, users, hashes, cracked):
        """Display precision results"""
        self.print_step(5, "PRECISION RESULTS")
        
        print(f"\n{Fore.CYAN + Style.BRIGHT}╔════════════════════════════════════════════════════════════════╗")
        print(f"║                   PRECISION SAM ANALYSIS                   ║")
        print(f"╠════════════════════════════════════════════════════════════════╣")
        
        for username, user_offset in users.items():
            if username in hashes:
                hash_data = hashes[username]
                status = f"{Fore.GREEN}CRACKED" if username in cracked and cracked[username] != "Unknown" else f"{Fore.RED}ENCRYPTED"
                password = cracked.get(username, "Hash extracted - needs cracking")
                
                print(f"║ {Fore.WHITE}User: {username:<12} {status}{Style.RESET_ALL}{Fore.CYAN}                   ║")
                print(f"║ {Fore.YELLOW}Password: {password:<28} {Fore.CYAN}             ║")
                print(f"║ {Fore.BLUE}User Offset: 0x{user_offset:08X} Hash Offset: 0x{hash_data['offset']:08X} {Fore.CYAN}║")
                print(f"║ {Fore.MAGENTA}NT Hash: {hash_data['nt_hash']} {Fore.CYAN}║")
                print(f"║ {'─' * 60} ║")
            else:
                print(f"║ {Fore.RED}User: {username:<12} NO HASH FOUND{Fore.CYAN}                   ║")
                print(f"║ {'─' * 60} ║")
        
        print(f"╚════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}")

    def run_precision_analysis(self):
        """Main precision analysis workflow"""
        self.print_banner()
        
        if not os.path.exists(self.sam_file):
            self.print_error("SAM file not found! Run the extractor first.")
            return
        
        # Load SAM data
        sam_data = self.read_binary_file(self.sam_file)
        if not sam_data:
            return
        
        self.print_info(f"SAM file size: {len(sam_data):,} bytes")
        
        # Find user accounts with precise locations
        users = self.find_user_accounts_with_precision(sam_data)
        if not users:
            self.print_error("No user accounts found")
            return
        
        # Extract hashes near user accounts
        hashes = self.extract_hashes_near_users(sam_data, users)
        if not hashes:
            self.print_error("No hashes extracted near user accounts")
            return
        
        # Crack the hashes with precision
        cracked = self.crack_with_precision(hashes)
        
        # Generate reports and display results
        self.save_precision_report(users, hashes, cracked)
        self.display_precision_results(users, hashes, cracked)
        
        self.print_success("\n🎉 PRECISION SAM ANALYSIS COMPLETE!")
        self.print_info("✓ User accounts precisely located")
        self.print_info("✓ Hashes extracted from targeted areas") 
        self.print_info("✓ Precision cracking attempted")
        self.print_info("✓ Technical report generated")

if __name__ == "__main__":
    parser = PrecisionSAMParser()
    parser.run_precision_analysis()