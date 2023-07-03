import os
import string

drives = ['%s:' % d for d in string.ascii_uppercase if os.path.exists('%s:' % d)]

for drive in drives:
    users_folder = os.path.join(drive, 'Users')
    if os.path.exists(users_folder):
        user_folders = [folder for folder in os.listdir(users_folder)
                        if os.path.isdir(os.path.join(users_folder, folder)) and
                        folder.lower() != 'default' and folder.lower() != 'public' and folder.lower() != 'all users' and folder.lower() != 'default user']

        if user_folders:
            for folder in user_folders:
                user_profile = os.path.join(users_folder, folder)
