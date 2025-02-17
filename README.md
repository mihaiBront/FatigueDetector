# CloudComputing_FinalProject
CloudComputing_FinalProject

## 1. Openning project in VS code

1) Press `F1` to open command palette
2) Have Python 3.12.X installed
3) Search for "*Tasks: Run Build Task*" and click on it
4) Run the "*Environment Setup Task*", which will install all necessary dependencies and get the virtual environment ready
5) Press `F1` again and select interpreter as

## 2. Debugging with flask

1) Go to the debug pane (left bar in visual studio)
2) Find "*RUN AND DEBUG*" on the top of that pane (you will see a Play button and a *drop down* selector)
3) In that *drop-down* selector, chose `Python Debugger: Flask ({Project Name})`
4) Run it. It will launch flask in *debug mode* with *hot reload*.

## 3. Notes on development
- All necessary pip installs must be added to the requirements.txt, since will be used for the container setup aswell
- Changes in settings for this project must be done at "workspace" level so they are updated to all users
