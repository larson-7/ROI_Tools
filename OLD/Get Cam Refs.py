from pypylon import pylon
maxCamerasToUse = 2


cam_list = []
# Get the transport layer factory.
tlFactory = pylon.TlFactory.GetInstance()
# Get all attached devices and exit application if no device is found.
devices = tlFactory.EnumerateDevices()
if len(devices) == 0:
    raise pylon.RuntimeException("No camera present.")

# Create an array of instant cameras for the found devices and avoid exceeding a maximum number of devices.
cameras = pylon.InstantCameraArray(min(len(devices), maxCamerasToUse))
print('device len', len(devices))
print('attributes', devices[0].__dict__)
print([x.DeviceGUIDKey  for x in devices])