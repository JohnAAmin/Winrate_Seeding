## Python Setup Guide
In order to run the Winrate Seeder, you need a version of python as well as a text editor.

I recommend [Sublime Text 3](https://www.sublimetext.com/3) for the text editor. [Atom](https://atom.io/) is another good editor

#### Setup
1. Install python:
  - Open Command Prompt and type "python".
    - **If you don't have python:** This should open the Microsoft Windows Store to the python app. Download it.
    - **If you have python:** A python terminal should open in the Command Prompt.
1. Install Packages:
  - Open a new command prompt or type "quit()" to exit python terminal
  - Type "pip help" to verify you have pip. This should open a command list
  - Install packages by typing:
      - "pip install **numpy==1.19.1**"
      - "pip install **pandas**"
      - "pip install **graphqlclient**"
      - "pip install **pyyaml**"
1. Install Sublime Text 3
  - Install Sublime 3
  - Go to Tools > Build System and select Python
  - Test python runs through Sublime Text
    - Create a file called "test.py"
    - In the file type "print('hello world')"
    - Press "Ctrl+B" to run test.py
    - A popup at the bottom should show "hello world"

Once these steps are complete you have a working installation of python and text editor on your computer. You can continue to follow the steps of the README.md to run the seed generator.
