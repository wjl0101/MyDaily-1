from os import getenv
import os
import sys
import setenv
from connection import FudanConnection

print(sys.path)

uid = getenv("STD_ID")
psw = getenv("PASSWORD")
send_key = getenv("SENDKEY")

connection = FudanConnection(
    uid, psw, send_key)
connection.login()
connection.get_verify_code()
connection.check_in()
connection.close()
