import subprocess
import os

def generate_executable():
    # Define the path to the client script
    client_script = 'client.py'
    
    # Check if the client script exists
    if not os.path.exists(client_script):
        print(f"Error: {client_script} does not exist.")
        return
    
    # Define the command to run PyInstaller
    command = [
        'pyinstaller',
        '--onefile',
        '--noconfirm',
        '--clean',
        client_script
    ]
    
    # Execute the command
    print("Generating executable using PyInstaller...")
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # Check if the build was successful
    if result.returncode == 0:
        print("Build completed successfully.")
        print("Executable can be found in the 'dist' directory.")
        print("Move the client.exe file to the target machine for execution.")

    else:
        print("Build failed with errors:")
        print(result.stdout)
        print(result.stderr)

if __name__ == "__main__":
    generate_executable()
