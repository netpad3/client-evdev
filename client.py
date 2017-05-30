import sys, socket
from evdev import InputDevice, ecodes as ec

if len(sys.argv) < 3:
    print("Usage: "+sys.argv[0]+" /dev/input/event* ip [port]")
    exit(1)

PORT = 6723
if len(sys.argv) > 3:
    PORT = int(sys.argv[3])

ADDRESS = (sys.argv[2], PORT)

ABS_MIN = -32767
ABS_MAX = 32767

dev = InputDevice(sys.argv[1])

print("Device: "+dev.name)

def mapthing(value, info):
    return (value - info.min) * (ABS_MAX - ABS_MIN) / (info.max - info.min) + ABS_MIN

caps = dev.capabilities()
keys = caps[ec.EV_KEY]
axes = ()
try:
    axes = caps[ec.EV_ABS]
except:
    pass
axesout = []
axismap = {}
for a in axes:
    axismap[a[0]] = len(axesout)
    info = a[1]
    axesout.append(mapthing(info.value, info))

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def sendMsg():
    global dev, keys, axesout
    active = dev.active_keys()
    buttons = 1
    for i in range(len(keys)-1, -1, -1):
        buttons <<= 1
        if keys[i] in active:
            buttons += 1
    print(axesout)
    print("{0:b}".format(buttons))
    msg = ",".join(str(int(x)) for x in axesout)+";"+("%x" % buttons)
    print(msg)
    sock.sendto(msg.encode('utf-8'), ADDRESS)

for event in dev.read_loop():
    print(event)
    if event.type == ec.EV_ABS:
        i = axismap[event.code]
        info = axes[i][1]
        axesout[i] = mapthing(event.value, info)
    sendMsg()
