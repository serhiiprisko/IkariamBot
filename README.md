### To build ui into py

pyuic6 -o botdialog_ui.py ui/botdialog.ui<br/>
pyuic6 -o botitem_ui.py ui/botitem.ui<br/>
pyuic6 -o widget_ui.py ui/widget.ui

### To build python into exe

pyinstaller --onefile --windowed main.py
