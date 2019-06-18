"""
============================================
vidgear library code is placed under the MIT license
Copyright (c) 2019 Abhishek Thakur

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
===============================================
"""


# import the necessary packages
from .camgear import CamGear

class VideoGear:
	"""
	This class provides a high level wrapper around VidGear's real-time video stabilizer. 
	This also provide access to any of the vidgear's primary classes(i.e. PiGear and CamGear), 
	separated by ```enablePiCamera``` flag. Furthermore, This Class accepts different attributes 
	and parameters based on which class is being accessed currently. 
	Kindly read `Vidgear Wiki` for more detailed information.

	VideoGear Specific parameters:
	
		:param (boolean) enablePiCamera: set this flag to access PiGear or CamGear class respectively. 
										/ This means the if enablePiCamera flag is `True`, PiGear class will be accessed 
										/ and if `False`, the camGear Class will be accessed. Its default value is False.

		:param (boolean) stabilize: set this flag to enable access to VidGear's Stabilizer Class. This basically enables(if True) or disables(if False) 
										video stabilization in VidGear. Its default value is False.

		:param (dict) **options: can be used in addition, to pass parameter supported by VidGear's stabilizer class.
						/ Supported dict keys are: 
								`SMOOTHING_FACTOR` (int) : to alter averaging window size
								`BORDER_SIZE` (int) : to alter output border cropping				
								`BORDER_TYPE` (string) : to change the border mode
		:param (boolean) logging: set this flag to enable/disable error logging essential for debugging. Its default value is False.
	
	CamGear Specific supported parameters for VideoGear:

		:param source : take the source value for CamGear Class. Its default value is 0. Valid Inputs are:
		    - Index(integer): Valid index of the video device.
		    - YouTube Url(string): Youtube URL as input.
		    - Network_Stream_Address(string): Incoming Stream Valid Network address. 
		    - GStreamer (string) videostream Support
		:param (boolean) y_tube: enables YouTube Mode in CamGear Class, i.e If enabled the class will interpret the given source string as YouTube URL. 
								/ Its default value is False.
		:param (int) backend: set the backend of the video stream (if specified). Its default value is 0.


	PiGear Specific supported parameters for VideoGear:
	
		:param (tuple) resolution: sets the resolution (width,height) in Picamera class. Its default value is (640,480).
		:param (integer) framerate: sets the framerate in Picamera class. Its default value is 25.


	Common parameters for CamGear and PiGear: 
	    :param (dict) **options: sets parameter supported by PiCamera or Camgear (whichever being accessed) Class to the input video stream. 
	    						/ These attribute provides the flexibity to manuplate input raspicam video stream directly. 
	    						/ Parameters can be passed using this **option, allows you to pass keyworded variable length of arguments to given Class.
	    :param (boolean) logging: set this flag to enable/disable error logging essential for debugging. Its default value is False.
	    :param (integer) time_delay: sets time delay(in seconds) before start reading the frames. 
	    					/ This delay is essentially required for camera to warm-up. 
	    					/ Its default value is 0.
	"""

	def __init__(self, enablePiCamera = False, stabilize = False, source=0, y_tube = False, backend = 0, colorspace = None, resolution=(640, 480), framerate=25, logging = False, time_delay = 0, **options):
		
		self.stablization_mode = stabilize

		if self.stablization_mode:
			from .stabilizer import Stabilizer
			self.s_factor, border_size, border_type = (25, 0, 'black')
			if options:
				if "SMOOTHING_FACTOR" in options:
					if isinstance(options["SMOOTHING_FACTOR"],int):
						self.s_factor = options["SMOOTHING_FACTOR"] #assigsn special parameter to global variable
					del options["SMOOTHING_FACTOR"] #clean
				if "BORDER_SIZE" in options:
					if isinstance(options["BORDER_SIZE"],int):
						border_size = options["BORDER_SIZE"] #assigsn special parameter
					del options["BORDER_SIZE"] #clean
				if "BORDER_TYPE" in options:
					if isinstance(options["BORDER_TYPE"],str):
						border_type = options["BORDER_TYPE"] #assigsn special parameter
			self.stabilizer_obj = Stabilizer(smoothing_factor = self.s_factor, border_type = border_type, border_size = border_size, logging = logging)
			#log info
			if logging:
				print('Enabling Stablization Mode for the current video source!')

		if enablePiCamera:
			# only import the pigear module only if required
			from .pigear import PiGear

			# initialize the picamera stream by enabling PiGear Class
			self.stream = PiGear(resolution=resolution, framerate=framerate, colorspace = colorspace, logging = logging, time_delay = time_delay, **options)

		else:
			# otherwise, we are using OpenCV so initialize the webcam
			# stream by activating CamGear Class
			self.stream = CamGear(source=source, y_tube = y_tube, backend = backend, colorspace = colorspace, logging = logging, time_delay = time_delay, **options)

	def start(self):
		# start the threaded video stream
		self.stream.start()
		return self

	def update(self):
		# grab the next frame from the stream
		self.stream.update()

	def read(self):
		# return the current frame
		while self.stablization_mode:
			frame = self.stream.read()
			if frame is None:
				break
			frame_stab = self.stabilizer_obj.stabilize(frame)
			if not(frame_stab is None):
				return frame_stab
		return self.stream.read()

	def stop(self):
		# stop the thread and release any resources
		self.stream.stop()
		self.stabilizer_obj.clean()