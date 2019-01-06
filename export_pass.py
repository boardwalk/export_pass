#!/usr/bin/env python3
import argparse
import os
import subprocess
import csv

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('in_dir')
    parser.add_argument('out_file', type=argparse.FileType('w'))
    args = parser.parse_args()

    header = [
        'folder',
        'favorite',
        'type',
        'name',
        'notes',
        'fields',
        'login_uri',
        'login_username',
        'login_password',
        'login_totp'
    ]

    writer = csv.writer(args.out_file)
    writer.writerow(header)

    for dirpath, dirnames, filenames in os.walk(args.in_dir):
        for filename in filenames:
            if not filename.endswith('.gpg'):
                continue

            fullpath = os.path.join(dirpath, filename)
            print('Processing ' + fullpath)

            folder = ''
            favorite = ''
            type = 'login'
            name = ''
            notes = ''
            fields = ''
            login_uri = ''
            login_username = ''
            login_password = ''
            login_totp = ''

            # Fill in values from file path
            assert dirpath.startswith(args.in_dir)
            folder = dirpath[len(args.in_dir):].lstrip('/')
            name = filename[:-len('.gpg')]

            # Fill in values from file contents
            lines = subprocess.check_output(['gpg', '-qd', fullpath]).decode().strip().splitlines()

            login_password = lines[0]

            for line in lines[1:]:
                key, value = line.split(':', maxsplit=1)
                key = key.strip()
                value = value.strip()
                if key == 'URL':
                    login_uri = value
                elif key == 'UserName':
                    login_username = value
                else:
                    print('Putting other key in note: {}: {}'.format(key, value))
                    if notes:
                        notes += '\n'
                    notes += '{}: {}'.format(key, value)

            # Write to CSV
            values = []
            for col in header:
                values.append(locals()[col])

            writer.writerow(values)

if __name__ == '__main__':
    main()
