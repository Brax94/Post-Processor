import sys
import datetime
import random
import math

class PostProcessor:

	#Make sure robot coincides with the world reference frame
	#Support for reference frame offsets not yet included
	#TODO: Support world reference frame offsets. 

#__________________OPEN AND INIT FILE _____________________________
	def __init__(self, name, folderLocation, robot=None):
		self.name = name
		#TODO: Make dat file when program handles more complexity
		#self.dat = open(folderLocation + name + ".dat", 'w')
		self.src = open(folderLocation + name + '.src', 'w')
		self.src.write(';'+str(datetime.datetime.now()) + '\n')
		self.src.write("DEF " + name.upper() + '()')
		self.src.write(
			'''
EXT BAS (BAS_COMMAND: IN, REAL:IN)
DECL AXIS HOME

BAS (#INITMOV, 0)

HOME = {AXIS: A1 0, A2 -90, A3 90, A4 0, A5 0, A6 0}
PTP HOME\n'''
			)
#____________________READ VISUAL COMPONENTS PROGRAM __________________
	#This method will get all statemnets in the given program, listed in 
	#the sequence of the simulation. Subprograms not called from the given sequence 
	#will not be part of the resulting list
	def getProgramStatements(self, routine):
		statements = routine.Statements
		finalStatements = []

		for statement in statements:
			finalStatements.append(statement)
			if statement.Type == 'Call':
				print "extends"
				print statement.Routine
				finalStatements.extend(self.getProgramStatements(statement.Routine))
		return finalStatements

#___________________ HANDLE ALL STATEMENT CASES ______________________

	#TODO: Fix speed, acc, ects. 
	#TODO: Fix reference point extraction, currently only writes arbitrary VC world positions
	def ptpMotion(self, statement):
		pM = statement.Positions[0].PositionInWorld
		pV = pM.P
		pR = pM.WPR
		x,y,z =  pV.X, pV.Y, pV.Z
		a,b,c = pR.X, pR.Y, pR.Z
		self.src.write('PTP {X %f,Y %f,Z %f,A %f,B %f,C %f} C_DIS\n' % (x,y,z,a,b,c))

	def linMotion(self, statement):
		pM = statement.Positions[0].PositionInWorld
		pV = pM.P
		pR = pM.WPR 
		x,y,z =  pV.X, pV.Y, pV.Z
		a,b,c = pR.X, pR.Y, pR.Z
		self.src.write('LIN {X %f,Y %f,Z %f,A %f,B %f,C %f} C_DIS\n' % (x,y,z,a,b,c))

	#TODO: Implement more statements, ie TOOL, BASE, CALL, PATH, DELAY and so on. 

	#TODO: Paths in VC are sets of linear movements - check if SLIN is best fit when
	#translating. SLP might be just as good or better?
	def path(self, statement):
		self.src.write('SPLINE\n')
		for i in statement.Positions:
			pM = i.Position #position matrix
			pV = pM.P #position vector
			pR = pM.WPR  #rotation vector
			x,y,z =  pV.X, pV.Y, pV.Z
			a,b,c = pR.X, pR.Y, pR.Z
			self.src.write('	SLIN {X %f,Y %f,Z %f,A %f,B %f,C %f}\n' % (x,y,z,a,b,c))
		self.src.write('ENDSPLINE\n')

	def delay(self, statement):
		self.src.write('WAIT SEC %f\n' % statement.Delay )

	def defineBase(self, statement):
		pM = statement.Position
		pV = pM.P #position vector
		pR = pM.WPR  #rotation vector
		x,y,z =  pV.X, pV.Y, pV.Z
		a,b,c = pR.X, pR.Y, pR.Z
		self.src.write('$BASE = {X %f,Y %f,Z %f,A %f,B %f,C %f}\n' % (x,y,z,a,b,c))

	def defineTool(self, statement):
		pM = statement.Position
		pV = pM.P #position vector
		pR = pM.WPR  #rotation vector
		x,y,z =  pV.X, pV.Y, pV.Z
		a,b,c = pR.X, pR.Y, pR.Z
		self.src.write('$TOOL = {X %f,Y %f,Z %f,A %f,B %f,C %f}\n' % (x,y,z,a,b,c))

#__________________ PROCESS ROUTINE __________________________
	def process(self, routine):
		statements = self.getProgramStatements(routine)

		#Following code is used to process different statement
		#types. Support for all statement types should be added here.

		for statement in statements:
			t = statement.Type
			if(t == 'LinMotion' ):
				self.linMotion(statement)
			elif(t == 'PtpMotion'):
				self.ptpMotion(statement)
			elif(t == 'Delay'):
				self.delay(statement)
			elif(t == 'Path'):
				self.path(statement)
			elif(t == 'DefineTool'):
				self.defineTool(statement)
			elif(t == 'DefineBase'):
				self.defineBase(statement)
			else:
				print('Statement Not Yet Supported')

#_________________ON FINISH ____________________________________
	#Close file when finished
	def close(self):
		self.src.close()

