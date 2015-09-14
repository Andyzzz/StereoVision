# -*- coding:utf-8 -*- 


#
# Qt interface for the disparity module
#


#
# External dependencies
#
import pickle
import sys
import cv2
import numpy as np
import PySide.QtCore as qtcore
import PySide.QtGui as qtgui


#
# Class to export 3D point cloud
#
class PointCloud( object ) :

	#
    # Header for exporting point cloud to PLY file format
    #
    ply_header = (
'''ply
format ascii 1.0
element vertex {vertex_count}
property float x
property float y
property float z
property uchar red
property uchar green
property uchar blue
end_header
''')

	#
	# Initialize the point cloud
	#
    def __init__( self, coordinates, colors ) :
		self.coordinates = coordinates.reshape(-1, 3)
		self.colors = colors.reshape(-1, 3)

	#
	# Export the point cloud to a PLY file
	#
    def WritePly( self, output_file ) :
		mask = self.coordinates[:, 2] > self.coordinates[:, 2].min()
		self.coordinates = self.coordinates[ mask ]
		self.colors = self.colors[ mask ]
		points = np.hstack( [ self.coordinates, self.colors ] )
		with open( output_file, 'w' ) as outfile :
			outfile.write( self.ply_header.format( vertex_count=len(self.coordinates) ) )
			np.savetxt( outfile, points, '%f %f %f %d %d %d' )


#
# Customize the Qt widget to setup the stereo BM
#
class StereoSGBM( qtgui.QWidget ) :

	#
	# Initialisation
	#
	def __init__( self, parent = None ) :
		
		#
		# Initialize the StereoBM
		#
		
		# Load stereo calibration parameter file
		with open( 'stereo-calibration.pkl' , 'rb') as input_file :
			self.calibration = pickle.load( input_file )

		# Read the images
		self.left_image = cv2.imread( 'left.png', cv2.CV_LOAD_IMAGE_GRAYSCALE )
		self.right_image = cv2.imread( 'right.png', cv2.CV_LOAD_IMAGE_GRAYSCALE )

		# Remap the images
		self.left_image = cv2.remap( self.left_image,
			self.calibration['left_map'][0], self.calibration['left_map'][1], cv2.INTER_LINEAR )
		self.right_image = cv2.remap( self.right_image,
			self.calibration['right_map'][0], self.calibration['right_map'][1], cv2.INTER_LINEAR )

		# StereoSGBM parameters
		self.min_disparity = 16
		self.max_disparity = 96
		self.sad_window_size = 3
		self.uniqueness_ratio = 10
		self.speckle_window_size = 100
		self.speckle_range = 2
		self.p1 = 216
		self.p2 = 864
		self.max_difference = 1
		self.full_dp = False


		#
		# Initialize the interface
		#

		# Initialise QWidget
		super( StereoSGBM, self ).__init__( parent )

		# Set the window title
		self.setWindowTitle( 'StereoSGBM disparity controls' )

		# Set the window size
		self.setGeometry( qtcore.QRect(10, 10, 621, 251) )

		# Minimum disparity
		self.label_min_disparity = qtgui.QLabel( self )
		self.label_min_disparity.setText( 'Minimum disparity' )
		self.spinbox_min_disparity = qtgui.QSpinBox( self )
		self.spinbox_min_disparity.setMaximum( 240 )
		self.spinbox_min_disparity.setSingleStep( 16 )
		self.spinbox_min_disparity.setValue( self.min_disparity )

		# Maximum disparity
		self.label_max_disparity = qtgui.QLabel( self )
		self.label_max_disparity.setText( 'Maximum disparity' )
		self.spinbox_max_disparity = qtgui.QSpinBox( self )
		self.spinbox_max_disparity.setMaximum( 240 )
		self.spinbox_max_disparity.setSingleStep( 16 )
		self.spinbox_max_disparity.setValue( self.max_disparity )

		# SAD window size
		self.label_sad_window_size = qtgui.QLabel( self )
		self.label_sad_window_size.setText( 'SAD window size' )
		self.spinbox_sad_window_size = qtgui.QSpinBox( self )
		self.spinbox_sad_window_size.setMinimum( 3 )
		self.spinbox_sad_window_size.setMaximum( 11 )
		self.spinbox_sad_window_size.setSingleStep( 2 )
		self.spinbox_sad_window_size.setValue( self.sad_window_size )

		# Uniqueness ratio
		self.label_uniqueness_ratio = qtgui.QLabel( self )
		self.label_uniqueness_ratio.setText( 'Uniqueness ratio' )
		self.spinbox_uniqueness_ratio = qtgui.QSpinBox( self )
		self.spinbox_uniqueness_ratio.setValue( self.uniqueness_ratio )

		# Speckle window size
		self.label_speckle_window_size = qtgui.QLabel( self )
		self.label_speckle_window_size.setText( 'Speckle window size' )
		self.spinbox_speckle_window_size = qtgui.QSpinBox( self )
		self.spinbox_speckle_window_size.setMaximum( 240 )
		self.spinbox_speckle_window_size.setValue( self.speckle_window_size )

		# Speckle range
		self.label_speckle_range = qtgui.QLabel( self )
		self.label_speckle_range.setText( 'Speckle range' )
		self.spinbox_speckle_range = qtgui.QSpinBox( self )
		self.spinbox_speckle_range.setValue( self.speckle_range )

		# P1
		self.label_p1 = qtgui.QLabel( self )
		self.label_p1.setText( 'P1' )
		self.spinbox_p1 = qtgui.QSpinBox( self )
		self.spinbox_p1.setMaximum( 2000 )
		self.spinbox_p1.setValue( self.p1 )

		# P2
		self.label_p2 = qtgui.QLabel( self )
		self.label_p2.setText( 'P2' )
		self.spinbox_p2 = qtgui.QSpinBox( self )
		self.spinbox_p2.setMaximum( 2000 )
		self.spinbox_p2.setValue( self.p2 )

		# Max difference
		self.label_max_difference = qtgui.QLabel( self )
		self.label_max_difference.setText( 'Max difference' )
		self.spinbox_max_difference = qtgui.QSpinBox( self )
		self.spinbox_max_difference.setValue( self.max_difference )

		# Buttons
		self.button_open = qtgui.QPushButton( 'Open', self )
		self.button_open.clicked.connect( self.LoadImages )
		self.button_apply = qtgui.QPushButton( 'Apply', self )
		self.button_apply.clicked.connect( self.UpdateDisparity )
		self.button_save = qtgui.QPushButton( 'Save', self )
		self.button_save.clicked.connect( self.SavePointCloud )

		# Widget layout
		self.layout_controls = qtgui.QGridLayout()
		self.layout_controls.addWidget( self.label_min_disparity, 0, 0 )
		self.layout_controls.addWidget( self.spinbox_min_disparity, 0, 1 )
		self.layout_controls.addWidget( self.label_max_disparity, 1, 0 )
		self.layout_controls.addWidget( self.spinbox_max_disparity, 1, 1 )
		self.layout_controls.addWidget( self.label_sad_window_size, 2, 0 )
		self.layout_controls.addWidget( self.spinbox_sad_window_size, 2, 1 )
		self.layout_controls.addWidget( self.label_uniqueness_ratio, 3, 0 )
		self.layout_controls.addWidget( self.spinbox_uniqueness_ratio, 3, 1 )
		self.layout_controls.addWidget( self.label_speckle_window_size, 4, 0 )
		self.layout_controls.addWidget( self.spinbox_speckle_window_size, 4, 1 )
		self.layout_controls.addWidget( self.label_speckle_range, 5, 0 )
		self.layout_controls.addWidget( self.spinbox_speckle_range, 5, 1 )
		self.layout_controls.addWidget( self.label_p1, 6, 0 )
		self.layout_controls.addWidget( self.spinbox_p1, 6, 1 )
		self.layout_controls.addWidget( self.label_p2, 7, 0 )
		self.layout_controls.addWidget( self.spinbox_p2, 7, 1 )
		self.layout_controls.addWidget( self.label_max_difference, 8, 0 )
		self.layout_controls.addWidget( self.spinbox_max_difference, 8, 1 )
		self.layout_buttons = qtgui.QHBoxLayout()
		self.layout_buttons.addWidget( self.button_open )
		self.layout_buttons.addWidget( self.button_apply )
		self.layout_buttons.addWidget( self.button_save )
		self.layout_global = qtgui.QVBoxLayout( self )
		self.layout_global.addLayout( self.layout_controls )
		self.layout_global.addLayout( self.layout_buttons )
		
	#
	# Load the images
	#
	def LoadImages( self ) :
		pass

	#
	# Save the resulting point cloud
	#
	def SavePointCloud( self ) :
		print( 'Exporting point cloud...' )
		point_cloud = PointCloud( cv2.reprojectImageTo3D( self.bm_disparity, self.calibration['Q'] ),
			cv2.cvtColor( self.left_image, cv2.COLOR_GRAY2RGB ) )
		point_cloud.WritePly( 'mesh-{}-{}.ply'.format( self.min_disparity, self.sad_window_size ) )
		print( 'Done.' )

	#
	# Compute the stereo correspondence
	#
	def UpdateDisparity( self ) :

		# Get the parameters
		self.min_disparity = self.spinbox_min_disparity.value()
		self.max_disparity = self.spinbox_max_disparity.value()
		self.sad_window_size = self.spinbox_sad_window_size.value()
		self.uniqueness_ratio = self.spinbox_uniqueness_ratio.value()
		self.speckle_window_size = self.spinbox_speckle_window_size.value()
		self.speckle_range = self.spinbox_speckle_range.value()
		self.max_difference = self.spinbox_max_difference.value()
		self.p1 = self.spinbox_p1.value()
		self.p2 = self.spinbox_p2.value()

		# Create the disparity object
		print( "Create SGBM..." )
		self.bm = cv2.StereoSGBM( minDisparity=self.min_disparity,
			numDisparities=self.max_disparity,
			SADWindowSize=self.sad_window_size,
			uniquenessRatio=self.uniqueness_ratio,
			speckleWindowSize=self.speckle_window_size,
			speckleRange=self.speckle_range,
			disp12MaxDiff=self.max_difference,
			P1=self.p1,
			P2=self.p2,
			fullDP=self.full_dp )
		
		# Compute the disparity map
		print( "Compute SGBM..." )
		self.bm_disparity = self.bm.compute( self.left_image, self.right_image )
		
		# Create the disparity image for display
		print( "Create disparity image..." )
		self.bm_disparity_img = self.bm_disparity.astype( np.float32 ) / 16.0
		cv2.normalize( self.bm_disparity_img, self.bm_disparity_img, 0, 255, cv2.NORM_MINMAX )
		self.bm_disparity_img = self.bm_disparity_img.astype( np.uint8 )
		self.bm_disparity_img = cv2.applyColorMap( self.bm_disparity_img, cv2.COLORMAP_JET )
		cv2.imshow( 'Disparity map', cv2.pyrDown( self.bm_disparity_img ) )
		cv2.waitKey( 1 )

