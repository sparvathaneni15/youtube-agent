Custom agent that performs actions within your YouTube account

# Directions
- Create virtual environment
```python3 -m venv [name]```
- Activate virtual environment
```source [name]/bin/activate```
- Install required packages for virtual environment
```pip install -r requirements.txt```
- Create a .env file using the template and name the file you will saving the state to
```cp .env .env.example```
- Find the path to your Chrome Profile in your local system (most likely fits a format similar to below)
```/Users/[username]/Library/Application Support/Google/Chrome/Default```
* may need to append ```/Default```
- Save YouTube Account credentials
```python save_state_from_chrome.py```