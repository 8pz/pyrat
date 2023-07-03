import win32service
import win32serviceutil
import win32security

def check_service_privileges(service_name):
    # Open the Service Control Manager
    scm_handle = win32service.OpenSCManager(None, None, win32service.SC_MANAGER_CONNECT)

    try:
        # Open the service
        service_handle = win32service.OpenService(scm_handle, service_name, win32service.SERVICE_QUERY_CONFIG)

        try:
            # Query the service configuration
            service_info = win32service.QueryServiceConfig(service_handle)
            
            # Check if the service has elevated privileges
            if service_info[2] & win32service.SERVICE_CONFIG_REQUIRED_PRIVILEGES_INFO:
                return True
            else:
                return False
        finally:
            # Close the service handle
            win32service.CloseServiceHandle(service_handle)
    finally:
        # Close the Service Control Manager handle
        win32service.CloseServiceHandle(scm_handle)

# Example usage
service_name = "WebClient"
has_privileges = check_service_privileges(service_name)
if has_privileges:
    print(f"The service '{service_name}' has elevated privileges.")
else:
    print(f"The service '{service_name}' does not have elevated privileges.")
