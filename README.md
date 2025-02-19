# mobilidade-urbana
Data analysis scripts for Abdala's urban mobility research

## installation

1. Install Git.
2. Install Python (3.11.2 or higher) with Pip (https://www.python.org/).
3. Install VSCode (https://code.visualstudio.com/).
4. Open VSCode.
5. Click on the "Source Control" option or press CTRL+SHIFT+G on your keyboard.
6. Clone this repository. If you prefer to clone using the terminal you can do:
   ```
   # clone to your local "mobilidade-urbana" folder in your current directory
   git clone https://github.com/cpicanco/mobilidade-urbana
   ```
7. Open your cloned folder in VSCode (File -> Open Folder).
8. Open PowerShell within VSCode (View -> Terminal).
9.  Create a new virtual environment:
    ```
    py -m venv .venv
    ```
10. Activate the virtual environment in VSCode when it prompts you, or do it manually in the VSCode PowerShell: .\\.venv\\Scripts\\activate.
11. Install project dependencies:
    ```
    py -m pip install -r .\\analysis\\requirements.txt
    ```
12. Copy raw data to corresponding folders:
    - oliveira-paiva
    - rogaciano-leite
    - virgilio-tavora

## raw data access
Contact us for obtaining the raw data.