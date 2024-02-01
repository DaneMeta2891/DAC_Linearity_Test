from scope_com import scopeConnectionUtil
import subprocess

VALID_IDS = ["MSO-X 4054A"]

def get_dynamic_ips():
    dynamic_lines = list()
    for line in subprocess.run(["arp", "-a"], capture_output=True).stdout.decode().split("\r\n"):
        if (line.find("dynamic") != -1):
            dynamic_lines.append([val for val in line.split(" ") if val != ''])
    return dynamic_lines

def check_id(scope:scopeConnectionUtil):
    idn = scope.send_recv("*IDN?")
    return True if idn.split(",")[1] in VALID_IDS else False

def check_ips():
    with scopeConnectionUtil() as scope:
        for val in get_dynamic_ips():
            print(val[0])
            if (scope.connect(val[0]) and check_id(scope)):
                return True

check_ips()