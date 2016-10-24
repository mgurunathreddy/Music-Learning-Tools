# GUI frame for the dftModel_function.py

from Tkinter import *
import tkFileDialog, tkMessageBox
import sys, os
import subprocess
sys.path.insert(0, '/home/ksrao/gurunath/MS_work/zff_melody/melody_extract/singing_range_identification/src/')
import festivalSpeak as speak
import pygame
from scipy.io.wavfile import read
import mainSARGAMPractice_V6 as mainSARGAM
import singerF0TanpuraSyn_V2 as TanpurSynth
class DftModel_frame:
  
	def __init__(self, parent):  
		 
		self.parent = parent        
		self.initUI()
		pygame.init()

	def initUI(self):

		choose_label = "Please select a SARGAM music wave file:"
		Label(self.parent, text=choose_label).grid(row=0, column=0, sticky=W, padx=5, pady=(10,2))
 
		#TEXTBOX TO PRINT PATH OF THE SOUND FILE
		self.filelocation = Entry(self.parent)
		self.filelocation.focus_set()
		self.filelocation["width"] = 35
		self.filelocation.grid(row=1,column=0, sticky=W, padx=15)
		self.filelocation.delete(0, END)
		self.filelocation.insert(0, '../../SARGAMS/sargam.wav')

		#BUTTON TO BROWSE SOUND FILE
		self.open_file = Button(self.parent, text="Browse...", command=self.browse_file) #see: def browse_file(self)
		self.open_file.grid(row=1, column=0, sticky=W, padx=(315, 8)) #put it beside the filelocation textbox
 
		#BUTTON TO PREVIEW SOUND FILE
		self.preview = Button(self.parent, text=">", command=self.preview_sound, bg="gray30", fg="white")
		self.preview.grid(row=1, column=0, sticky=W, padx=(400,6))

		## DFT MODEL
          #BUTTON TO Tanpura tuning
		self.compute = Button(self.parent, text="Tanpura Tuning", command=self.Tanpura_Tuning, bg="dark red", fg="white")
		self.compute.grid(row=2, column=0, padx=(315, 8), pady=(10,15), sticky=W)
     
          #BUTTON TO Record
		self.compute = Button(self.parent, text="SARGAM Record", command=self.record_sargam, bg="dark red", fg="white")
		self.compute.grid(row=3, column=0, padx=(315, 8), pady=(10,15), sticky=W)

          #BUTTON TO Analyze
		self.compute = Button(self.parent, text="SARGAM Analyze", command=self.analyze_sargam, bg="dark red", fg="white")
		self.compute.grid(row=4, column=0, padx=(315, 8), pady=(10,15), sticky=W)

          #BUTTON TO Correct SARGAM
		self.compute = Button(self.parent, text="SARGAM Correct", command=self.correct_sargam, bg="dark red", fg="white")
		self.compute.grid(row=5, column=0, padx=(315, 8), pady=(10,15), sticky=W)

		#ANALYSIS WINDOW TYPE
		wtype_label = "Developed by"
		Label(self.parent, text=wtype_label).grid(row=2, column=0, sticky=W, padx=5, pady=(10,2))
		self.w_type = StringVar()
		#self.w_type.set("blackman") # initial value
		#window_option = OptionMenu(self.parent, self.w_type, "rectangular", "hanning", "hamming", "blackman", "blackmanharris")
		#window_option.grid(row=2, column=0, sticky=W, padx=(95,5), pady=(10,2))

		#WINDOW SIZE
		M_label = "Audio Speech and Music Signal Processing Group"
		Label(self.parent, text=M_label).grid(row=3, column=0, sticky=W, padx=5, pady=(10,2))
		#self.M = Entry(self.parent, justify=CENTER)
		#self.M["width"] = 5
		#self.M.grid(row=3,column=0, sticky=W, padx=(115,5), pady=(10,2))
		#self.M.delete(0, END)
		#self.M.insert(0, "511")

		#FFT SIZE
		N_label = "Indian Institute of Technology, Kharagpur"
		Label(self.parent, text=N_label).grid(row=4, column=0, sticky=W, padx=5, pady=(10,2))
		#self.N = Entry(self.parent, justify=CENTER)
		#self.N["width"] = 5
		#self.N.grid(row=4,column=0, sticky=W, padx=(270,5), pady=(10,2))
		#self.N.delete(0, END)
		#self.N.insert(0, "1024")

		#TIME TO START ANALYSIS
		#time_label = "Time in sound (in seconds):"
		#Label(self.parent, text=time_label).grid(row=5, column=0, sticky=W, padx=5, pady=(10,2))
		#self.time = Entry(self.parent, justify=CENTER)
		#self.time["width"] = 5
		#self.time.grid(row=5, column=0, sticky=W, padx=(180,5), pady=(10,2))
		#self.time.delete(0, END)
		#self.time.insert(0, ".2")

#==============================================================================
# 		#BUTTON TO COMPUTE EVERYTHING
# 		self.compute = Button(self.parent, text="Compute", command=self.compute_model, bg="dark red", fg="white")
# 		self.compute.grid(row=6, column=0, padx=5, pady=(10,15), sticky=W)
#==============================================================================

		# define options for opening file
		self.file_opt = options = {}
		options['defaultextension'] = '.wav'
		options['filetypes'] = [('All files', '.*'), ('Wav files', '.wav')]
		options['initialdir'] = '../../sounds/'
		options['title'] = 'Open a mono audio file .wav with sample frequency 44100 Hz'

	def preview_sound(self):
		
		filename = self.filelocation.get()

		if filename[-4:] == '.wav':
			fs, x = read(filename)
		else:
			tkMessageBox.showerror("Wav file", "The audio file must be a .wav")
			return

		if len(x.shape) > 1 :
			tkMessageBox.showerror("Stereo file", "Audio file must be Mono not Stereo")
		#elif fs != 44100:
		#	tkMessageBox.showerror("Sample Frequency", "Sample frequency must be 44100 Hz")
		else:
			sound = pygame.mixer.Sound(filename)
			sound.play()
 
	def browse_file(self):
		
		self.filename = tkFileDialog.askopenfilename(**self.file_opt)
 
		#set the text of the self.filelocation
		self.filelocation.delete(0, END)
		self.filelocation.insert(0,self.filename)

	def Tanpura_Tuning(self):
		
		try:
			#inputFile = self.filelocation.get()
			#window = self.w_type.get()
			#M = int(self.M.get())
			#N = int(self.N.get())
			#time = float(self.time.get())
			#melody_main.main(inputFile)
			TanpurSynth.tuneTanpura()
			#mainSARGAM.analysisSARGAM()   

		except ValueError as errorMessage:
			tkMessageBox.showerror("Input values error",errorMessage)

	def record_sargam(self):
		
		try:
			#inputFile = self.filelocation.get()
			#window = self.w_type.get()
			#M = int(self.M.get())
			#N = int(self.N.get())
			#time = float(self.time.get())
			#melody_main.main(inputFile)
			#mainSARGAM.recordSARGAM()   
			recordFileName = '../../record/test.wav'
			text = "Get ready to record your SARGAM for thirty seconds after start command"
			speak.speak(text)
			speak.speak('Start')
			subprocess.call(['arecord',  '-r', '44100', '-d', '30', recordFileName])        # Recording will be done for 30 sec at 44.1 KHz
			text = "This is what you have recorded"
			speak.speak(text)
			subprocess.call(['aplay', recordFileName])

		except ValueError as errorMessage:
			tkMessageBox.showerror("Input values error",errorMessage)
   
	def analyze_sargam(self):
		
		try:
			inputFile = self.filelocation.get()
			#window = self.w_type.get()
			#M = int(self.M.get())
			#N = int(self.N.get())
			#time = float(self.time.get())
			#melody_main.main(inputFile)
			mainSARGAM.analysisSARGAM(inputFile)   

		except ValueError as errorMessage:
			tkMessageBox.showerror("Input values error",errorMessage)
   
	def correct_sargam(self):
		
		try:
			#inputFile = self.filelocation.get()
			#window = self.w_type.get()
			#M = int(self.M.get())
			#N = int(self.N.get())
			#time = float(self.time.get())
			#melody_main.main(inputFile)
			mainSARGAM.correctSARGAM()   

		except ValueError as errorMessage:
			tkMessageBox.showerror("Input values error",errorMessage)
			
