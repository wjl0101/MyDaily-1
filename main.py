from os import getenv
import os
import sys
import setenv
from connection import FudanConnection



uid = getenv("STD_ID")
psw = getenv("PASSWORD")
send_key = getenv("SENDKEY")

print(uid,psw,send_key)

connection = FudanConnection(
    uid, psw, send_key)
connection.login()
connection.get_verify_code()
connection.check_in()
connection.close()
