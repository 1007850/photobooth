import booth_camera as cam

c = cam.cam()

c.shoot()
c.lastCapture[-1].show()