import textwrap
import paho.mqtt.client as mqtt
import uuid
import ssl

import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789

# Configuration for CS and DC pins (these are FeatherWing defaults on M0/M4):
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = None

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 64000000

# Setup SPI bus using hardware SPI:
spi = board.SPI()

# Create the ST7789 display:
disp = st7789.ST7789(
    spi,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
    width=135,
    height=240,
    x_offset=53,
    y_offset=40,
)

# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
height = disp.width  # we swap height/width to rotate it to landscape!
width = disp.height
image = Image.new("RGB", (width, height))
rotation = 90

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
disp.image(image, rotation)
# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height - padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0

# Alternatively load a TTF font.  Make sure the .ttf font file is in the
# same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)

# Turn on the backlight
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True

# the # wildcard means we subscribe to all subtopics of IDD
topic = 'IDD/#'

# some other examples
# topic = 'IDD/a/fun/topic'

#this is the callback that gets called once we connect to the broker. 
#we should add our subscribe functions here as well
def on_connect(client, userdata, flags, rc):
	print(f"connected with result code {rc}")
	client.subscribe(topic)
	# you can subsribe to as many topics as you'd like
	# client.subscribe('some/other/topic')

def update_display_with_mqtt_message(message):
    """Updates the display with the received MQTT message."""
    # Clear the image with a black rectangle
    draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
    
    # Wrap the message to fit the display
    wrapped_text = textwrap.fill(message, width=20)  # Adjust width as needed
    
    # Draw the text on the display
    text_size = draw.textsize(wrapped_text, font=font)
    text_x = (width - text_size[0]) // 2
    text_y = (height - text_size[1]) // 2
    draw.text((text_x, text_y), wrapped_text, font=font, fill="#FFFFFF")
    
    # Update the display with the new image
    disp.image(image, rotation)

# this is the callback that gets called each time a message is recived
def on_message(cleint, userdata, msg):
	print(f"topic: {msg.topic} msg: {msg.payload.decode('UTF-8')}")
	# you can filter by topics
	update_display_with_mqtt_message(msg.payload.decode('UTF-8'))
	# if msg.topic == 'IDD/some/other/topic': do thing




# Every client needs a random ID
client = mqtt.Client(str(uuid.uuid1()))
# configure network encryption etc
client.tls_set(cert_reqs=ssl.CERT_NONE)
# this is the username and pw we have setup for the class
client.username_pw_set('idd', 'device@theFarm')

# attach out callbacks to the client
client.on_connect = on_connect
client.on_message = on_message

#connect to the broker
client.connect(
    'farlab.infosci.cornell.edu',
    port=8883)

# this is blocking. to see other ways of dealing with the loop
#  https://www.eclipse.org/paho/index.php?page=clients/python/docs/index.php#network-loop
client.loop_forever()
