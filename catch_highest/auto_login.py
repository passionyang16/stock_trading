# coding: utf-8

import pywinauto
import pyautogui
import time

print(pywinauto.__version__)

PATH = 'c:\\Users\\passi\\Desktop'

with open(PATH + '\\programming\\stair_to_heaven\\catch_highest\\config\\pw.txt') as f:
    itms = list(f.readlines())
    pw = itms[0].strip()
    cert = itms[1].strip()

app = pywinauto.Application(backend='win32')
app.start(r'C:\CREON\STARTER\coStarter.exe /prj:cp')
print('cp load done')

# wait
time.sleep(1)

procs = pywinauto.findwindows.find_elements()
for proc in procs:
    if proc.name == 'CREON Starter':
        break

app.connect(process=proc.process_id)
print('connected')

app.window(title="CREON")
app.window().TypeKeys(pw)


# # 다이얼로그
# def ret_wind():
#     return app.window(title='CREON Starter')
# dlg = pywinauto.timings.WaitUntilPasses(20, 0.5, ret_wind)
# print('done dlg')

# pass edit
# pass_edit = app.Edit2
# pass_edit.SetFocus()
# pass_edit.TypeKeys(pw)
# print('done pw')

# # cert edit
# cert_edit = app.Edit3
# cert_edit.SetFocus()
# cert_edit.TypeKeys(cert)
# print('done cert')

# # login
# btn = app.Button
# btn.Click()
# print('done login click')