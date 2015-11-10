# -*- coding:utf-8 -*-


#
# Module to display live images from a camera
#


#
# External dependencies
#
import numpy as np
from PySide import QtCore
from PySide import QtGui


#
# Qt Widget to display the images from a camera
#
class CameraWidget( QtGui.QLabel ) :

	#
	# Signal sent to update the image in the widget
	#
	update_image = QtCore.Signal( np.ndarray )

	#
	# Initialization
	#
	def __init__( self, parent = None ) :

		# Initialize QLabel
		super( CameraWidget, self ).__init__( parent )

		# Connect the signal to update the image
		self.update_image.connect( self.UpdateImage )

	#
	# Update the image in the widget
	#
	def UpdateImage( self, image ) :

		# Create a Qt image
		qimage = QtGui.QImage( image, image.shape[1], image.shape[0], QtGui.QImage.Format_RGB888 )

		# Set the image to the Qt widget
		self.setPixmap( QtGui.QPixmap.fromImage( qimage ) )

		# Update the widget
		self.update()
