# PoopTracker RaspberryPi

RaspberryPi to collect and send all needed sensor data to the PoopTracker Backend.


## Project structure

Main.py contains the full application to run the RaspberryPi. The other .py Applications are used by Main.py to define some important classes.

```
PoopTracker_Test/
┣ .gitignore
┣ MCP3008.py
┣ README.md
┣ hx711.py
┣ main.py
┣ mq.py
┗ requirements.txt
```

## Local installation

The project can be installed locally by completing the following checklist.

1. Clone the repository: `git clone https://github.com/pfistdo/PoopTracker_RaspberryPi.git`
2. Create a new venv: `python -m venv venv`
3. Activate the venv: `.\venv\Scripts\activate`
4. Install all dependencies: `pip install -r requirements.txt`
5. Start the server by executing [main.py](main.py)

## Authors

- [@fabioardi](https://github.com/fabioardi)
