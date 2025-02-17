# Find Line Segments Example
#
# This example shows off how to find line segments in the image. For each line object
# found in the image a line object is returned which includes the line's rotation.
# find_line_segments() finds finite length lines (but is slow).
# Use find_line_segments() to find non-infinite lines (and is fast).
enable_lens_corr = False # turn on for straighter lines...
import sensor, image, time, math
from pyb import UART
sensor.reset()
sensor.set_pixformat(sensor.RGB565) # grayscale is faster
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(time = 2000)
sensor.set_auto_gain(False) # must be turned off for color tracking
sensor.set_auto_whitebal(False) # must be turned off for color tracking
clock = time.clock()

uart = UART(3, 115200, timeout_char=1000)                         # init with given baudrate
uart.init(115200, bits=8, parity=None, stop=1, timeout_char=1000) # init with given parameters

threshold_index = 3 # 0 for red, 1 for green, 2 for blue, 3 for 3d printed, 4 for cytron box
# Color Tracking Thresholds (L Min, L Max, A Min, A Max, B Min, B Max)
# The below thresholds track in general red/green/blue things. You may wish to tune them...
thresholds = [(30, 100, 15, 127, 15, 127), # generic_red_thresholds
              (30, 100, -64, -8, -32, 32), # generic_green_thresholds
              (0, 30, 0, 64, -128, 0),
              (31, 53, -128, 37, -128, -35),
              (30, 60, -34, 12, -38, -13)] # generic_blue_thresholds

def find_color_blob():
    ours_x, ours_y, width, height = 0,0,0,0

    for blob in img.find_blobs([thresholds[threshold_index]], pixels_threshold=0, area_threshold=0, merge=True):
        # These values depend on the blob not being circular - otherwise they will be shaky.
        temp_width = blob.rect()[2]
        temp_height = blob.rect()[3]
        if temp_width * temp_height > 60:
            ours_x, ours_y, width, height = blob.rect()
            #img.draw_rectangle(blob.rect(), color = (0,255,0))

        # Note - the blob rotation is unique to 0-180 only.
    return ours_x, ours_y, ours_x + width, ours_y + height, width, height
while(True):
    clock.tick()
    img = sensor.snapshot()
    img.crop(1,1,(30,10,100,100))

    ours_x1, ours_y1, ours_x2, ours_y2, width, height = find_color_blob()
    center_x = int((math.fabs(ours_x2 - ours_x1) / 2) + ours_x1)
    center_y = int((math.fabs(ours_y2 - ours_y1) / 2) + ours_y1)
    #img.draw_cross((center_x, center_y), color = (255, 255, 0))

    arena_x, arena_y, radius = 0, 0, 0
    ### detect arena circle
    for c in img.find_circles(threshold = 2000, x_margin = 10, y_margin = 10, r_margin = 10,
        r_min = 40, r_max = 42, r_step = 2):

        if c.r() > radius:
            arena_x, arena_y, radius = c.x(), c.y(), c.r()

    if enable_lens_corr: img.lens_corr(1.8)

    min_line = 30
    max_line = 70
    edge_x1 = 1000
    edge_x2 = 0
    edge_y1 = 1000
    edge_y2 = 0
    offset = 2

    ### detect enemy robot
    for l in img.find_line_segments(merge_distance = 2, max_theta_diff = 5):
        x1, y1, x2, y2 = l.line()
        if math.sqrt(math.pow(x1-center_x, 2) + math.pow(y1-center_y, 2)) > 17:
            if math.sqrt(math.pow(x1-arena_x, 2) + math.pow(y1-arena_y, 2)) < radius-3:
                edge_x1, edge_y1, edge_x2, edge_y2 = x1, y1, x2, y2
                #img.draw_line(l.line(), color = (255, 0, 0))

    print("%d,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (ours_x1, ours_y1, ours_x2, ours_y2,edge_x1, edge_y1, edge_x2, edge_y2, arena_x, arena_y))

