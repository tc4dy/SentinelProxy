#This tool is developed by @tc4dy and is provided completely for FREE.
#Unauthorized selling of this software is prohibited.

import requests
from bs4 import BeautifulSoup
import threading
import queue
import time
import os
from colorama import Fore, Style, init

init(autoreset=True)

class SentinelProxy:
    def __init__(self):
        self.proxies_to_check = queue.Queue()
        self.valid_proxies = []
        self.lock = threading.Lock()
        self.language = "EN"
        self.timeout = 5
        self.sources = [
            "https://free-proxy-list.net/",
            "https://www.us-proxy.org/",
            "https://www.socks-proxy.net/",
            "https://www.sslproxies.org/"
        ]
        
        self.banner = f"""
{Fore.CYAN}    ███████╗███████╗███╗   ██╗████████╗██╗███╗   ██╗███████╗██╗     
    ██╔════╝██╔════╝████╗  ██║╚══██╔══╝██║████╗  ██║██╔════╝██║     
    ███████╗█████╗  ██╔██╗ ██║   ██║   ██║██╔██╗ ██║█████╗  ██║     
    ╚════██║██╔══╝  ██║╚██╗██║   ██║   ██║██║╚██╗██║██╔══╝  ██║     
    ███████║███████╗██║ ╚████║   ██║   ██║██║ ╚████║███████╗███████╗
    ╚══════╝╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚═╝╚═╝  ╚═══╝╚══════╝╚══════╝
{Fore.RED}    [#] Advanced Proxy Scraper & Checker
    [#] Created by Tc4dy - Tuğra | 2026
        """

    def set_language(self):
        print(self.banner)
        print(f"{Fore.YELLOW}1- English\n2- Türkçe")
        choice = input(f"{Fore.WHITE}Choose Language / Dil Seçin: ")
        if choice == "2":
            self.language = "TR"
            print(f"{Fore.GREEN}[+] Dil Türkçe olarak ayarlandı.\n")
        else:
            print(f"{Fore.GREEN}[+] Language set to English.\n")

    def msg(self, en, tr):
        return tr if self.language == "TR" else en

    def scrape_proxies(self):
        print(f"{Fore.BLUE}[*] {self.msg('Scraping proxies from multiple sources...', 'Birden fazla kaynaktan proxy toplanıyor...')}")
        
        found_count = 0
        for url in self.sources:
            try:
                response = requests.get(url, timeout=10)
                soup = BeautifulSoup(response.text, "html.parser")
                table = soup.find("table")
                if table:
                    for row in table.find_all("tr")[1:]:
                        tds = row.find_all("td")
                        if len(tds) >= 2:
                            ip = tds[0].text.strip()
                            port = tds[1].text.strip()
                            proxy = f"{ip}:{port}"
                            self.proxies_to_check.put(proxy)
                            found_count += 1
            except Exception as e:
                continue
        
        print(f"{Fore.GREEN}[+] {self.msg(f'Found {found_count} proxies.', f'{found_count} adet proxy bulundu.')}")

    def check_proxy_worker(self):
        while not self.proxies_to_check.empty():
            proxy = self.proxies_to_check.get()
            url = "https://httpbin.org/ip"
            try:
                proxy_dict = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
                start_time = time.time()
                r = requests.get(url, proxies=proxy_dict, timeout=self.timeout)
                latency = round((time.time() - start_time) * 1000)
                
                if r.status_code == 200:
                    with self.lock:
                        print(f"{Fore.GREEN}[+] {self.msg('Valid', 'Aktif')}: {proxy} | {latency}ms")
                        self.valid_proxies.append(proxy)

                        with open("valid_proxies.txt", "a") as f:
                            f.write(f"{proxy}\n")
            except:
                pass
            finally:
                self.proxies_to_check.task_done()

    def run(self):
        self.set_language()
        
        if os.path.exists("valid_proxies.txt"):
            os.remove("valid_proxies.txt")
            
        self.scrape_proxies()
        
        thread_count = 50
        print(f"{Fore.BLUE}[*] {self.msg(f'Starting {thread_count} threads for verification...', f'Doğrulama için {thread_count} thread başlatılıyor...')}")
        
        threads = []
        for _ in range(thread_count):
            t = threading.Thread(target=self.check_proxy_worker, daemon=True)
            t.start()
            threads.append(t)
        
        self.proxies_to_check.join()
        
        print(f"\n{Fore.YELLOW}{'='*50}")
        print(f"{Fore.CYAN}[!] {self.msg('Scan Completed!', 'Tarama Tamamlandı!')}")
        print(f"{Fore.GREEN}[+] {self.msg(f'Total Valid Proxies: {len(self.valid_proxies)}', f'Toplam Aktif Proxy: {len(self.valid_proxies)}')}")
        print(f"{Fore.GREEN}[+] {self.msg('Results saved to valid_proxies.txt', 'Sonuçlar valid_proxies.txt dosyasına kaydedildi.')}")
        print(f"{Fore.YELLOW}{'='*50}")

if __name__ == "__main__":
    app = SentinelProxy()
    app.run()