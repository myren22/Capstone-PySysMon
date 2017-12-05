# Created on Oct 3, 2017
#
# @author: KyleWin10
#-------------------------------------------------------------------------------------
# Outline:
#
#  Main code (part 1)
#  class PySysMonitor_gui
#      __init__(self, par
#      create_widgets(self)
#      open_optionsWindow(self)
#          applyOptions()
#          restoreDefaults()
#      open_singleProcProp (self)
#      columnSort(self,  *posArgs)
#      onlyDrawExistingPIDS(self):
#      clearData(self):
#
#      create_procListViewFrameGUI (self, parent)   return plvTree, plvFrame
#         acceptAndGraphPID()
#      periodicUpdateProcIDList(self)
#
#      create_timeGraphContentsGUI(self, parent)  
#      periodicUpdateOfGraph(self)
#
#      toggleUpdate(self, aBool)
#      raiseFrame(self, frameRaised)
#      printScreen(self)
#    end class
#  Main code (part 2)
#     on_closing()
#
#-------------------------------------------------------------------------------------
# Revision History:
#  2017-11-13   Added comments.  
#               Added filter to prevent logging of this command repeatedly to the PID. 
#               Added PID to process ID, to be used later in the graphing.
#               Added CLEAR button to top of form, and wipe out the list and start from
#                  scratch. 
#  2017-11-14   Made start page wider and higher
#  2017-11-15   Added ability to save data to Queue.
#               Added ability to draw graph for PID
#
# ------------------------------------------------------------------------------------
# Ideas:   Process Page:  Detect a click on a row, and use the  PID in that row
#                          to kick off the Graphical draw. 
#                         Ability to click on several PIDs.  Have software graph 
#                          the selected pids on same graph.
#
# ------------------------------------------------------------------------------------

#imports
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
# implement the default mpl key bindings
from matplotlib.backend_bases import key_press_handler
import matplotlib.pyplot as plt

from pprint import pprint
import tkinter as tk
import tkinter.font as tkFont
import tkinter.ttk as ttk
import numpy as np
import time
# from tkinter import *
# from tkinter.ttk import *
# import re
# import subprocess
# import sys
# import os
from subprocess import Popen, PIPE

# from PIL import Image, ImageTk#still buggy, needed for screenprinting only tk wind
# import pyscreenshot as ImageGrab # For Linux

#---#

#---- MAIN -------------------------------------------
print('start')



# boolTakeInData=True

pidDict={}
# pidList=[[7,7,7,7,7,7],[7,7,7,7,7,7]]#2d
# dictFrames={}

#time->pid->process traits
timeTick=0

#-----------------------------------------------
class PySysMonitor_gui(tk.Frame):
#-----------------------------------------------
# Purpose: PySysMonitor_gui provides ..
#
#-----------------------------------------------

    #-----------------------------------------------
    def __init__(self, parent):
    #-----------------------------------------------
    # Purpose:  To be the contructor/initialize variables in the class
    #-----------------------------------------------
        tk.Frame.__init__(self, parent) # embeds this frame class in a parent

        self['relief']='raised'
        self['borderwidth']=4
        self.pack(fill='both', expand=1) # now it will be visible

        # setup window setting
        # name, size, exit button,

        # init class variables
        self.timeTick=0
        self.dictFrames={}
        self.pidDict={}
        self.boolTakeInData=True
        self.updateIntervalMS= 3000
        self.timeTrackDurat=60
        self.printSaveDir=r'/home/kyle/Software Downloads/Capstone/Screenshots'
        self.strPSatrFound=None
        self.desigCol='CPU%'
        self.desigDescend=1
        self.plvTree=None
        self.visColumns=['PID', 'CPU%', 'RAM%', 'User', 'Process Name']
        self.PID_GuiScratchpad       = -1   # User enters one by one each a sequence of data
        self.PID_ReqToBeGraphed_i    = -1   # User presses ACCEPT and if its a valid PID_GuiScratchpad it is here
        self.ActivePIDbeingGraphed_i = -1   # Current graphics are being drawn for this.

        #  matplot variables
        self.canvas = None
        self.axCPU = None
        self.axMem = None

        self.Q_size      = int(300)    # Queue Size.  Elements in the Queue
        self.head_oldest = int(  1)    # front of Queue. If other data is added, this is the oldest data.
        self.tail_newest = int(  1)    # end of Queue.  Items get in line here.  Has the newest data.

        # ---- New pidQinfo (start)----------------------
        self.firstRun=True
        self.psCompleteDict={} #dict of all ps's, keyword pid
        self.MaxPids2Graph = 5
        self.pidQinfo = np.zeros(self.MaxPids2Graph,
                         dtype={'names': ['active', 'pid', 'Qhead', 'Qtail'],
                                'formats': ['i8', 'i8', 'i8', 'i8']})
        self.pidQinfo[0]["active"] = 0  # 0 = not being tracked,  1=being tracked
        self.pidQinfo[0]["Qhead"] = int(1)
        # ---- New pidQinfo (end) ----------------------

        # ----- new  pids2graph (start) -------------
        self.pids2graph={}
        self.lbSelected=None
        # ----- new  pids2graph (end) -------------


        # self.timeQueue = [None] * self.Q_size;dd

        #self.timeQueue = np.dtype(('str', (300,5) ))
        self.timeQueue = np.zeros ( self.Q_size,
                           dtype = { 'names'   :['timestamp','pid','pcpu','pmem','str40'],
                                     'formats' :[       'f8', 'f8',  'f8',  'f8',  'a40'] } )
        # ---- New timeQueue for multiple pids (start) ----------------------


        self.timeQueue2 = np.zeros((self.MaxPids2Graph,
                               self.Q_size),
                                dtype={'names'  : ['timestamp', 'pid', 'pcpu', 'pmem', 'str40'],
                                       'formats': ['f8', 'f8', 'f8', 'f8', 'a40'] } )
        self.timeQueue2[0, 0]["timestamp"] = int(2)
        # ---- New timeQueue for multiple pids (end) ----------------------

        # run create gui methods
        self.create_widgets() #

    #----------------------------------------------------------------------------
    def create_widgets(self):
        #----------------------------------------------------------------------------
        # Purpose:  To create the GUI widgets the user will see.   This consists of:
        # Row
        # ---
        #      topBarFrame
        # 1:  buttons: PROCESS_LIST, TIME_GRAPH, PROC_PROP, OPTIONS, PRINT, RESUME, PAUSE
        #             |----------------------|  |--------------------------------------|
        #                      LEFT_BAR                          RIGHT_BAR
        #    +-------------------------------------------------------------------------+
        # 2: |  Title                                                                  |
        #    |                                                                         |
        #    |                                                                         |
        # 3: |    Muti Frame Overlay (For ProcessListView      and TimeGraph)          |
        #    |                                                                         |
        #    |                                                                         |
        #    +-------------------------------------------------------------------------+
        # 4:
        # 5:
        # 6:
        #
        #----------------------------------------------------------------------------

        self.grid_rowconfigure(    2, weight=12)
        self.grid_columnconfigure( 1, weight= 1)

        # region topBarFrame
        topBarFrame = tk.Frame(self)#relief='raised', borderwidth=2, bg='teal'
        topBarFrame.grid(row=1,column=1, sticky='new')
        # ===============================================================================
        # Create the buttons for the Top Bar
        # Row:
        # 0:  topBarFrame
        #     buttons: PROCESS_LIST, TIME_GRAPH, PROC_PROP, OPTIONS, PRINT, RESUME, PAUSE
        #              |----------------------|  |--------------------------------------|
        #                 LEFT_BAR                          RIGHT_BAR
        #
        # ===============================================================================

        topBarFrame.grid_columnconfigure(1,minsize=40, weight=1)
        topBarFrame.grid_columnconfigure(3, minsize=80, weight=1)

        # TOP_BAR: LEFT_FRAME: will have buttons PROCESS_LISTS and TIME_GRAPH
        leftButFrame = tk.Frame(topBarFrame)
        leftButFrame.grid(row=1,column=1,sticky='w')#grid(row=0, column=0)

        # button: PROCESS_LIST
        procListBut = tk.Button(leftButFrame, text= 'Process List')
        procListBut.grid(row=1, column=0)
        procListBut['command'] = lambda name='procList': self.raiseFrame(name)     #self.raiseFrame('procList')
        # Note:  python keyword "lambda" means don't execute the method, but instead just pass the method as a value

        # button: TIME_GRAPH
        timeGraphBut = tk.Button(leftButFrame, text= 'Time Graph')
        timeGraphBut.grid(row=1, column=1)
        timeGraphBut['command'] = lambda name='timeGraph': self.raiseFrame(name)

        # button: CLEAR
        CLEARBut = tk.Button(leftButFrame, text= 'CLEAR')
        CLEARBut.grid(row=1, column=2)
        CLEARBut['command'] = self.clearData    # call method clearData

        # TOP_BAR:  RIGHT_FRAME: will have PROC_PROP, OPTIONS, PRINT, RESUME, PAUSE
        rightButFrame = tk.Frame(topBarFrame)

        # button: PROC_PROP
        # procPropBut = tk.Button(rightButFrame, text='Proc. Prop')  # ,padx=0.5,pady=0.5
        # procPropBut.grid(row=1, column=1)
        # procPropBut['command'] = self.open_singleProcProp

        # button: OPTIONS
        optionsBut = tk.Button(rightButFrame, text='Options')#,padx=0.5,pady=0.5
        optionsBut.grid(row=1, column=2)
        optionsBut['command'] = self.open_optionsWindow #openOptionsWindow()
        rightButFrame.grid(row=1, column=3, sticky='e')

        # button: PRINT
        # prin
        # But['command'] = self.printScreen()

        # button: RESUME
        resumeBut = tk.Button(rightButFrame, text= 'Resume')
        resumeBut.grid(row=1, column=4)
        resumeBut['command'] = lambda aBool=True: self.toggleUpdate(aBool)

        # button: PAUSE
        pauseBut = tk.Button(rightButFrame, text= 'Pause')
        pauseBut.grid(row=1, column=5)
        pauseBut['command']=  lambda aBool=False: self.toggleUpdate(aBool)
        # endregion topBarFrame


        # ===============================================================================
        # Create the multi frame (overlays) for the middle of the screen
        # Row:
        #    +----------------------------------------------------------------------+
        # 2: |Title                                                                 |
        #    |                                                                      |
        #    |                                                                      |
        # 3: |Muti Frame Overlay (For ProcessListView      and TimeGraph)           |
        #    |  plvAndTgFrame         proclistFrame            timeGraphFrame       |
        #    |                        +-proclistTableFrame     +-timeGraphTableFrame|
        #    |                                                                      |
        #    +----------------------------------------------------------------------+
        # ===============================================================================
        ###begin everything in multi frame###
        plvANDtgFrame = tk.Frame(self)
        plvANDtgFrame.grid(row=2, column=1, sticky='nsew')

        # self.grid_columnconfigure(1, weight=1)
        # self.grid_rowconfigure(2, weight=1)
        plvANDtgFrame.grid_columnconfigure(1, weight=1)
        plvANDtgFrame.grid_rowconfigure(2, weight=1)

        # Overlay #1:    ProcessListView
        proclistFrame = tk.Frame(plvANDtgFrame, relief='sunken', borderwidth=2, width=450)
        proclistFrame.grid(row=2, column=1, sticky='nsew')  # pack(side='left', )
        proclistFrame.grid_columnconfigure(2, weight=1)
        proclistFrame.grid_rowconfigure(2, weight=1)
        self.dictFrames['procList'] = proclistFrame

        ttk.Label(proclistFrame, text='Process List View').grid(row=0,column=2, sticky='nwe')

        procListTableFrame = tk.Frame(proclistFrame, relief='sunken', borderwidth=2)
        procListTableFrame.grid(row=2,column=2, sticky='nsew')
        self.create_procListViewFrameGUI(procListTableFrame)

        # Overlay #2:   TimeGraphFrame
        timeGraphFrame = tk.Frame(plvANDtgFrame, relief='sunken', borderwidth=2)
        timeGraphFrame.grid(row=2, column=1, sticky='nsew')
        timeGraphFrame.grid_columnconfigure(2, weight=1)
        timeGraphFrame.grid_rowconfigure(2, weight=1)
        self.dictFrames['timeGraph'] = timeGraphFrame

        ttk.Label(timeGraphFrame, text='Process Time Graph').grid(row=0, column=2, sticky='nwe')
        timeGraphTableFrame = tk.Frame(timeGraphFrame, relief='raised', borderwidth=2)
        self.create_timeGraphContentsGUI(timeGraphTableFrame)
        timeGraphTableFrame.grid(row=2,column=2,sticky='nsew')



        self.raiseFrame('procList')
        #end create_widgets
		  
    #----------------------------------------------------------------------------
    def open_optionsWindow(self):
        #----------------------------------------------------------------------------
        # Purpose: To bring up the popup OPTIONS display.
        #    When the user clicks on the OPTIONS button, the popup window will appear
        #    where the user can custimize his options.
        #  The window contains some entry fields the user can enter data in such as:
        #   the FREQUENCY, the SAVE directory, the LENGTH OF TIME tracked, etc.
        #  There are three buttons at the bottom:  ACCEPT, CANCEL, DEFAULTS
        #----------------------------------------------------------------------------
        optionsWindow = tk.Toplevel()
        optionsWindow.title('PySysMonitor - Options')  # yep
        # width,height, xPos, yPos = [450,150,150,120]
        # optionsWindow.geometry('%dx%d+%d+%d' % (width,height, xPos, yPos))

        # ===============================================================================
        # Create some Option fields where the user can enter data.
        # ===============================================================================
        titleLabel=tk.Label(optionsWindow, text= 'Configuration Options')
        titleLabel.grid(column=1, row=1 ,columnspan=2,rowspan=1,sticky='')
        updateLabel=tk.Label(optionsWindow, text='Update Frequency(ms)')
        updateLabel.grid(row=2,column=1)
        updateEntry = tk.Entry(optionsWindow)
        updateEntry.grid(row=2, column=2, sticky='EW')

        tk.Label(optionsWindow, text='Print Save Dir.').grid(row=3, column=1)
        printSaveDirEntry = tk.Entry(optionsWindow)
        printSaveDirEntry.grid(row=3, column=2, sticky='EW')

        tk.Label(optionsWindow, text='Length Time Tracked(s)').grid(row=4, column=1)
        timeTrackEntry = tk.Entry(optionsWindow)
        timeTrackEntry.grid(row=4, column=2, sticky='EW')

        tk.Label(optionsWindow, text='Columns Displayed').grid(row=5, column=1)
        checkButFrame = tk.Frame(optionsWindow)
        checkButFrame.grid(row=5, column=2)
        pidCheckButVar = tk.IntVar()
        pidCheckBut = tk.Checkbutton(checkButFrame, text='PID', variable=pidCheckButVar).pack(side='left')
        pcpuCheckButVar = tk.IntVar()
        pcpuCheckBut = tk.Checkbutton(checkButFrame, text='%CPU', variable=pcpuCheckButVar).pack(side='left')
        pramCheckButVar = tk.IntVar()
        pramCheckBut = tk.Checkbutton(checkButFrame, text='%RAM', variable=pramCheckButVar).pack(side='left')
        userCheckButVar = tk.IntVar()
        userCheckBut = tk.Checkbutton(checkButFrame, text='User', variable=userCheckButVar).pack(side='left')
        commCheckButVar = tk.IntVar()
        commCheckBut = tk.Checkbutton(checkButFrame, text='Process Name', variable=commCheckButVar).pack(side='left')


        #Accept, Cancel, Default
        def applyOptions():
        #--------------------------------------------------------
        # Purpose: The ACCEPT button has been pressed by the user
        #   and this method then saves the values the user has changed.
        #--------------------------------------------------------

            self.updateIntervalMS = int(updateEntry.get())
            self.timeTrackDurat   = int(timeTrackEntry.get())
            self.printSaveDir     = printSaveDirEntry.get()
            #checkbuttons
                #['PID', 'CPU%', 'RAM%', 'User', 'Comm']
                #if checked
                    #add to displayList
                #... repeat for all columns/checkbuttons
                #run plvTree show with current list
            listPLVheaderShown=[]
            if (pidCheckButVar.get() == 1):
                listPLVheaderShown.append('PID')
            if (pcpuCheckButVar.get() == 1):
                listPLVheaderShown.append('CPU%')
            if (pramCheckButVar.get() == 1):
                listPLVheaderShown.append('RAM%')
            if (userCheckButVar.get() == 1):
                listPLVheaderShown.append('User')
            if (commCheckButVar.get() == 1):
                listPLVheaderShown.append('Process Name')
            self.plvTree['displaycolumns']=listPLVheaderShown
				
        #--------------------------------------------------------
        def restoreDefaults():
        #--------------------------------------------------------
        # Purpose: The DEFAULTS button has been pressed by the user
        #   and this method restores the values of the defaults. 
        #--------------------------------------------------------
            updateEntry.delete(0,tk.END)
            updateEntry.insert(tk.END, str(self.updateIntervalMS))
            printSaveDirEntry.delete(0,tk.END)
            printSaveDirEntry.insert(tk.END, self.printSaveDir)
            timeTrackEntry.delete(0,tk.END)
            timeTrackEntry.insert(tk.END, self.timeTrackDurat)
            if('PID' in self.visColumns):
                pidCheckButVar.set(1)
            else:
                pidCheckButVar.set(0)
            if ('CPU%' in self.visColumns):
                pcpuCheckButVar.set(1)
            else:
                pcpuCheckButVar.set(0)
            if ('RAM%' in self.visColumns):
                pramCheckButVar.set(1)
            else:
                pramCheckButVar.set(0)
            if ('User' in self.visColumns):
                userCheckButVar.set(1)
            else:
                userCheckButVar.set(0)
            if ('Process Name' in self.visColumns):
                commCheckButVar.set(1)
            else:
                commCheckButVar.set(0)
        restoreDefaults()
        # ===============================================================================
        # Create the buttons for the Bottom Bar:
        #       ACCEPT,             CANCEL,            DEFAULTS
        #       +--applyOptions                        +--restoreDefaults
        #
        # ===============================================================================
           # start off by loading the GUI fields with the default values

        botButFrame = tk.Frame(optionsWindow)
        botButFrame.grid(column=1, row=6 ,columnspan=2,rowspan=1,sticky='')

        acceptBut   = tk.Button(botButFrame,text='Accept',command=applyOptions)
        acceptBut.grid(row=1, column=2)

        cancelBut   = tk.Button(botButFrame,text='Cancel', command= lambda:optionsWindow.destroy())
        cancelBut.grid(row=1, column=3)

        defaultsBut = tk.Button(botButFrame,text='Defaults', command=restoreDefaults)
        defaultsBut.grid(row=1, column=4)
        #end of open_optionsWindow

    #----------------------------------------------------------------------------
    def open_singleProcProp(self, pidVal):
        #----------------------------------------------------------------------------
        # Purpose: To bring up the popup PROCESS PROPERTIES display.
        #    When the user clicks on the PROC_PROP button, the popup window will appear
        #    where the user can custimize some options.
        #  There is a CANCEL button at the bottom.
        #----------------------------------------------------------------------------
        procPropWind = tk.Toplevel()
        procPropWind.title('PySysMonitor - Process Properties')  # yep
        # width,height, xPos, yPos = [450,150,150,120]
        # procPropWind.geometry('%dx%d+%d+%d' % (width,height, xPos, yPos))

        # ===============================================================================
        # Create some Option fields where the user can enter data.
        # ===============================================================================
        # titleLabel = tk.Label(procPropWind, text='Process Properties')
        # titleLabel.grid(column=1, row=1 ,columnspan=2,rowspan=1,sticky='')
        #
        # lab1Des  = tk.Label(procPropWind, text='').grid(row=2, column=1)
        # lab1Data = tk.Label(procPropWind).grid(row=2, column=2)

        tk.Label(procPropWind, text='Fixed Properties').grid(row=0, column=1, columnspan=2)
        fixedList=['pid', 'name', 'ppid', 'parentName', 'uid', 'user name', 'start time', 'args']
        # fixedList = ['pid', 'name', 'uid', 'user']
        for i in range(0,len(fixedList)):
            tk.Label(procPropWind, text=fixedList[i]).grid(row=i+1, column=1,sticky='E')
            # strData = self.psCompleteDict[pidVal][fixedList[i]]
            tk.Label(procPropWind, text='--IN Progress--').grid(row=i+1, column=2,sticky='E')

        tk.Label(procPropWind, text='Variable Properties').grid(row=15, column=1,columnspan=2)
        fixedList = ['SystemTime','UserTime','Priority','ActiveStatus', ]
        # fixedList = ['pid', 'name', 'uid', 'user']
        for i in range(0, len(fixedList)):
            tk.Label(procPropWind, text=fixedList[i]).grid(row=i+20, column=1,sticky='E')
            # strData = self.psCompleteDict[pidVal][fixedList[i]]
            tk.Label(procPropWind, text='--IN Progress--').grid(row=i+20, column=2,sticky='E')





        # ===============================================================================
        # Create the buttons for the Bottom Bar:
        #                    CANCEL
        #
        # ===============================================================================
        cancelBut = tk.Button(procPropWind, text='Cancel', command=lambda: procPropWind.destroy())
        cancelBut.grid(row=100, column=1, columnspan=2)
        #end single_proc_prop

    def selectedProcBox(self, parent):

        listscrolFrame = tk.Frame(parent, borderwidth=2)
        listscrolFrame.pack(side=tk.TOP, fill=tk.BOTH)

        aLabel = tk.Label(listscrolFrame, text='Selected PIDs', )
        aLabel.pack(side=tk.TOP, fill=tk.X)

        # aButton = tk.Button(listscrolFrame, text='but1')
        # aButton.pack(side=tk.BOTTOM, fill=tk.X)

        # aLabel2 = tk.Label(listscrolFrame)
        # aLabel2.pack(side=tk.BOTTOM, fill=tk.X)

        togVisibBut = tk.Button(listscrolFrame, text='Toggle Visible')
        togVisibBut.pack(side=tk.BOTTOM, fill=tk.X)

        remTrakBut = tk.Button(listscrolFrame, text='Remove Track')
        remTrakBut.pack(side=tk.BOTTOM, fill=tk.X)

        # entryStrVar = tk.StringVar()
        # entryStrVar.set('a')
        # aEntry = tk.Entry(parent, textvariable=entryStrVar)
        # aEntry.pack(side=tk.TOP, fill=tk.X)

        scrollbar = tk.Scrollbar(listscrolFrame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.lbSelected = tk.Listbox(listscrolFrame, height=200)
        self.lbSelected.pack(side=tk.TOP, fill=tk.BOTH)

        for i in range(100):
            self.lbSelected.insert(tk.END, 'a' + str(i) + 'c')

        def togVis():
            # get entry value
            # find item in listbox matching entry value
            # for itemInd in range(0, self.lbSelected.size()):
                # a1 = entryStrVar.get()  # str
                # a2 = self.lbSelected.get(itemInd)  # matches whatever value was stored inside, str or int
                # if entryStrVar.get() == str(self.lbSelected.get(itemInd)):
                #     self.lbSelected.delete(itemInd)
                #     aButton['activeforeground'] = 'white'
                #     print('found')
                #     return
            # item not found in listBox
            # aButton['activeforeground'] = 'red'
            print('tog vis')

        def remove():
            self.lbSelected.delete(tk.ANCHOR)

        #
        def singClikLsbx(event):
            a0 = self.lbSelected.curselection()  # this gets changed between click and release events #tuple of selection
            a3 = self.lbSelected.get(tk.ANCHOR)  # same as above. val is that is box clicked. #init state is ''
            a1 = self.lbSelected.get(
                tk.ACTIVE)  # this gets changed after release events #val of active #init state is first listbox

            aLabel2['text'] = str()
            a2 = 2

        def doubClikLsbx(event):
            self.lbSelected.delete(tk.ANCHOR)
            print('dub click')

        togVisibBut['command'] = togVis
        remTrakBut['command'] =  remove
        self.lbSelected.bind("<Double-Button-1>", doubClikLsbx)
        self.lbSelected.bind("<ButtonRelease-1>", singClikLsbx)

        # attach listbox to scrollbar
        self.lbSelected.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.lbSelected.yview)

    #----------------------------------------------------------------
    def columnSort(self,  *posArgs): #tree, col, descending,
    #----------------------------------------------------------------
    # Purpose:  To take the passed in tree (1st parameter)
    #    and for the given column          (2nd parameter)
    #    sort the tree                     (3rd parameter)
    # The tree is then returned.
    #----------------------------------------------------------------
        tree,col,descending=None,None,None
        if(len(posArgs) ==3):
            self.desigCol=posArgs[1]
            self.desigDescend = posArgs[2]

        tree=posArgs[0]
        col=self.desigCol
        descending=self.desigDescend

        # """sort tree contents when a column header is clicked on"""
        # grab values to sort
        data = [[tree.set(child, col), child] \
                for child in tree.get_children()]

        # this make it so that the columns with the given names get treated as purely filled with floats
        # as opposed to filled with strings.
        floatsOnlyCols='CPU% RAM% PID'
        if col in floatsOnlyCols:
            for i in data:
                i[0] = float(i[0])

        data.sort(reverse=descending)

        for ix, item in enumerate(data):
            tree.move(item[1], '', ix)
        # switch the heading so it will sort in the opposite direction
        tree.heading(col, command=lambda col=col: self.columnSort(tree, col, int(not descending)))

    #-----------------------------------------------
    def onlyDrawExistingPIDS(self):
    #-----------------------------------------------
    # Purpose:  to only draw the PIDS (not query the latest info)
    #           Used to draw the cleared list allowing the user to
    #           see the list was actually clear.
    #-----------------------------------------------

        self.plvTree.delete(*self.plvTree.get_children())

        for i in range(0,8):
            pass
        for dictKey in self.pidDict.keys():
            # loop thru list of pids  (e.g. pidDict) and load the plvTree

            listEntries = self.pidDict[ dictKey ]

            self.plvTree.insert('','end',iid=dictKey, text=dictKey,values=(listEntries))


            result = self.plvTree.identify_row(i)
            childr = self.plvTree.get_children()

    #-----------------------------------------------
    def clearData(self):
    #-----------------------------------------------
    # Toggle pause resume method
    #-----------------------------------------------
        # print(' ################# clearData  ==> clearing self.pidDict and self.dictFrames')
        self.pidDict={}
        self.onlyDrawExistingPIDS()
	  
    #----------------------------------------------------------------
    def create_procListViewFrameGUI(self, parent):
        #----------------------------------------------------------------
        # Purpose:  Called once to initialize the table with minimal default values.
        #           parameter 1: "self"   used to see some class variables.
        #           parameter 2: "parent" used to attach new frame to parent.
        # returns  New
        #----------------------------------------------------------------

        # #--------------------------------------------------------
        # def acceptAndGraphPID():
        #     #--------------------------------------------------------
        #     # User has pressed the ACCEPT button and desires to have
        #     #   the  PID he has entered to be graphed.
        #     #--------------------------------------------------------
        #     PIDid = self.PID_GuiScratchpad.get()     # PID user has entered at the GUI
        #     # print ('------------------------------------------------------------------')
        #     # print ('>>>>>>>>>>>> create_procListViewFrameGUI:  ACCEPT(ProcessLIST):   Verifying PIDid', PIDid)
        #     # print ('------------------------------------------------------------------')
        #     PIDstr = str(PIDid)
        #
        #     if PIDstr in self.psCompleteDict:
        #
        #
        #
        #     # if (len(rowDataForPID) < 3):
        #     #    print('   NO Data for what appears to be a VALID PID: Will not graph')
        #     # else:
        #     #    # Yay! PIDid is valid (there is valid data for it in the list).
        #     #    # Go graph it.
        #     #    self.PID_ReqToBeGraphed_i = int(PIDid)          # Send this new PID to the graphics
        #     #    print('   Sending   PID_ReqToBeGraphed_i:  ', self.PID_ReqToBeGraphed_i)
        #     #    print('   VALID PID ===> self.raiseFrame( timeGraph)')
        #     #    self.raiseFrame('timeGraph')
        # # end acceptAndGraphPID --------------------------------

        enabledColumns = ['PID', 'CPU%', 'RAM%', 'User', 'Process Name']  # Column Titles displayed at Top of Table.
        plvFrame = ttk.Frame(parent)
        plvFrame.pack(fill='both', expand=True)

        plvTree = ttk.Treeview(plvFrame, columns=enabledColumns, show='headings', displaycolumns=enabledColumns)  # Display Column headings

        vsb = ttk.Scrollbar(plvFrame, orient='vertical',  command='self.tree.yview')
        hsb = ttk.Scrollbar(plvFrame, orient='horizontal',command='self.tree.xview')

        plvTree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        plvTree.grid(column=0, row=0, sticky='nsew', in_=plvFrame)

        vsb.grid(column=1, row=0, sticky='ns', in_=plvFrame)
        hsb.grid(column=0, row=1, sticky='ew', in_=plvFrame)

        plvFrame.grid_columnconfigure(0, weight=1)
        plvFrame.grid_rowconfigure(   0, weight=1)


        # # -------------- Bottom Right -----------------------------------
        # # 4:                 PID ID         :  ____####_____
        # # 5:                 ACCEPT_BUTTON
        # # ---------------------------------------------------------------
        # pidEntryFrame = tk.Frame(plvFrame)
        # pidEntryFrame.grid(column=0, row=4,columnspan=2, sticky='N')
        # PIDLabel  =  tk.Label(pidEntryFrame, text='PID to Graph:')
        # PIDLabel.grid(row=1,column=1)  # right justify (e)
        # self.PID_GuiScratchpad  = tk.Entry(pidEntryFrame)
        # self.PID_GuiScratchpad.grid(row=1,column=2)
        #
        # # # When ACCEPT button pressed call --> acceptAndGraphPID
        # # acceptPIDBut   = tk.Button(pidEntryFrame,text='Accept',command=acceptAndGraphPID)
        # # acceptPIDBut.grid(row=1, column=3)



        #build tree
        for col in enabledColumns:
            plvTree.heading(col, text=col, command=lambda c=col: self.columnSort(plvTree, c, 0))
            # adjust the column's width to the header string
            plvTree.column(col, width=tkFont.Font().measure(col.title()), anchor='e')


        def eventClick(event):
           print('plvTree:  item click')
           # get focus/selected value
           val = plvTree.focus()
           print(val)#tree item id
           print('itemText',plvTree.item(val)['text'])
           # self.PID_GuiScratchpad.delete(0, tk.END)
           # self.PID_GuiScratchpad.insert(tk.END, plvTree.item(val)['text'])

        #------ Right Click -----------
        def myRightClickEvent(event):
            print("============ plvTree:  RC event =========================")
            if plvTree.focus() !='':
                iidOfTree = plvTree.focus()  # get row
                dictOfRow = plvTree.item(iidOfTree)
                pidRow = dictOfRow['values']
                self.open_singleProcProp(pidRow)
                print(iidOfTree)
                print(self.psCompleteDict[iidOfTree])



        plvTree.bind("<Button-3>", myRightClickEvent)

        # ------ Double Left Click -----------
        def myEventDoubleClick(event):
            print ("============plvTree: Double Left click event =========================")
            #toggle tag,
            # self.plvTree.tag_configure("selected", background='green')
            # if in tree, remove it.  If not in tree, add it


            iidOfTree = plvTree.focus()  # get row
            dictOfRow = plvTree.item(iidOfTree)
            pidRow = dictOfRow['values'][0]
            tagState = self.psCompleteDict[iidOfTree]['ourState']

            if self.psCompleteDict[iidOfTree]['tracked']=='tracked':
                #  remove
                self.psCompleteDict[iidOfTree]['tracked']='notTracked'
                # del self.pids2graph[pidRow]
                plvTree.item(iidOfTree, tag=[tagState,'notTracked'])
            else:
                #  add (but make sure not passed max)
                self.psCompleteDict[iidOfTree]['tracked'] = 'tracked'
                # self.pids2graph[pidRow]=pidRow
                self.lbSelected.insert(tk.END, pidRow)
                plvTree.item(iidOfTree, tag=[tagState,'tracked'])

            pid_count = len(self.pids2graph)
            print ("new PID count = ", pid_count)


            # self.PID_GuiScratchpad.delete(0, tk.END)
            # self.PID_GuiScratchpad.insert(tk.END, pidRow)


        plvTree.bind("<Double-Button-1>", myEventDoubleClick)
        plvTree.tag_configure('tracked', foreground='red')
        colorList=['#165BFF','#53AFFF','#BADFFF','#FFFFFF','#FFD6D0','#FFA8D0','#CD000D']
        for i in range(-3,4):
            tag='state-'+str(i)
            plvTree.tag_configure(tag, background=colorList[i+3])
        plvTree.bind("<<TreeviewSelect>>", eventClick)

        self.plvTree=plvTree
        self.after(1000, self.periodicUpdateProcIDList)  # ----> periodic update

        # return plvTree, plvFrame       # new Tree,  new Frame that the new Tree is in.

    #-----------------------------------------------------------------------------
    def periodicUpdateProcIDList(self):
    #-----------------------------------------------------------------------------
    # Purpose:  This method is called periodically.  It does a Linux command
    #        and processes the linux output, filtering and organizing the data.
    #        and displaying filtered results in a table.
    #-----------------------------------------------------------------------------

        # 'ps', '-Ao', 'user,uid,comm,pid,pcpu,tty', '--sort=-pcpu', '|', 'head', '-n', '6' 
        #head causes issues

        if(self.boolTakeInData): #for some reason this ins't getting the memo when pause is pressed.


            traitsList = ['cpu%', 'mem%', 'time', 'ourState', 'tracked', 'pid', 'name', \
                          'args', 'ppid', 'args','startTime','uid']
            self.strPSatrFound='pid,comm,pcpu,pmem,user,uid'
            # 'pid,pcpu,pmem,uid'
            # 'comm,user'
            #  where:    -Ao = All processes. 
            #           pid  = Process ID(float)
            #           pcpu = Percentage CPU utilization(float)
            #           pmem = Percentage Memory utilization(float)
            #           user = User Name(str)
            #           comm = Command being executed(str)
            # "--sort=-pcpu" = Sort data based on percentage CPU utilization 
            #

            process = Popen(['ps', '-Ao', 'pid,pcpu,pmem,user,comm', '--sort=-pcpu'], stdout=PIPE, stderr=PIPE)
            stdout,_= process.communicate()
            print('time:', time.time())
            # print('gmtime',time.gmtime(time.time()), ', localtime:',time.localtime(time.time()))
            # columns of numbers are right aligned
            # columns of text are left aligned

            timestamp = time.time()

            i=-1
            self.pidList=[]
            listNewProcs=[]
            #update all existing process states as older, until found
            for key in self.psCompleteDict.keys():
                #age goes from new=-3, active=0, old=3+
                self.psCompleteDict[key]['ourState']=self.psCompleteDict[key]['ourState']+1


            # go through returned list of lines, and select lines to process. 
            for line in stdout.splitlines():
                #region terminalDecode
                i = i + 1
                if (i == 0):
                    continue    # ---> skip this line

                ##### print ('line(', i, ')', line)   ## Debug: line read in.
                type(line)
                decodeLine = line.decode('ascii', 'ignore')
                    #'ignore'  is used to not fail on unicode names (like web items from firefox)
                # print ('line(', i, ')', line)   ## Debug print: line read in.

                wordList=decodeLine.split()        # wordList has a list created from the items in the line
                commStrJoin=''

                # FILTER out our own command.   Look at all the fields specifically field 7.  If it 
                # has our own command which can be identified by our "pid,pcpu,pmem" then don't use it (skip it)
                if (len(wordList)> 8):
                    SeventhField = wordList[7]
                    if ( "pid,pcpu,pmem" in SeventhField):
                       continue     #------> skip this line (as it's our own command line)


                # Add the PID to our list (pidDict)
                if(len(wordList)>5):
                    for aStr in wordList[4:]:
                        commStrJoin=commStrJoin+aStr
                else:
                    commStrJoin=wordList[4]
                # if(i<10):
                    # print(wordList)
                floatList=wordList[0:4]
                floatList.append(commStrJoin)
                #all data extracted and formatted in a list cleanly now
                #endregion terminalDecode
                #check if pid in master ps dict
                # keyPIDcomm=wordList[0]+'_--_'+wordList[-1]#potential combinationKey with name
                keyPIDcomm=wordList[0]
                if keyPIDcomm not in self.psCompleteDict:
                    #initialize a dict with pidName combo, add to new ps list
                    self.psCompleteDict[keyPIDcomm]={}
                    self.psCompleteDict[keyPIDcomm]['pid'] = wordList[0]
                    self.psCompleteDict[keyPIDcomm]['name'] = wordList[-1]
                    if(self.firstRun): self.psCompleteDict[keyPIDcomm]['ourState'] = int(-1)
                    else: self.psCompleteDict[keyPIDcomm]['ourState'] = int(-3) #3 cycles till we mark it as normal
                    self.psCompleteDict[keyPIDcomm]['tracked'] ='notTracked'
                    self.psCompleteDict[keyPIDcomm]['cpu%list']=[]
                    self.psCompleteDict[keyPIDcomm]['mem%list']=[]
                    self.psCompleteDict[keyPIDcomm]['timelist']=[]
                    listNewProcs.append(keyPIDcomm)
                else:
                    if(self.psCompleteDict[keyPIDcomm]['ourState']>0):
                        self.psCompleteDict[keyPIDcomm]['ourState']=self.psCompleteDict[keyPIDcomm]['ourState']-1

                #update value
                self.psCompleteDict[keyPIDcomm]['cpu%'] = wordList[1]
                self.psCompleteDict[keyPIDcomm]['mem%'] = wordList[2]
                self.psCompleteDict[keyPIDcomm]['user'] = wordList[3]
                if self.psCompleteDict[keyPIDcomm]['tracked']=='tracked':
                    self.psCompleteDict[keyPIDcomm]['cpu%list'].append(wordList[1])
                    self.psCompleteDict[keyPIDcomm]['mem%list'].append(wordList[2])
                    self.psCompleteDict[keyPIDcomm]['timelist'].append(timestamp)
                self.psCompleteDict[keyPIDcomm]['time'] = ''
                self.psCompleteDict[keyPIDcomm]['plvValues']=wordList
                self.pidDict[  str(wordList[0])  ]  =  floatList  #((wordList[0:4]),(commStrJoin))

                #for first runs of periodicUpdateProcIDList save the top 10.
                if self.firstRun and i<11:
                    self.psCompleteDict[keyPIDcomm]['tracked']='tracked'


            for key in self.psCompleteDict.keys():
                # check if key, and therefore entry exists in tree
                # insert if not
                if self.plvTree.exists(key):
                    if self.psCompleteDict[key]['ourState']>3 and self.psCompleteDict[key]['tracked'] !='tracked':
                        #remove old ps from tree and dict
                        self.plvTree.delete(key)
                        # del self.psCompleteDict[key]
                        continue
                    #update values if proc still alive
                    self.plvTree.item(key, values=self.psCompleteDict[key]['plvValues'])
                    #or set?
                else:
                    self.plvTree.insert('',tk.END,iid=key, values=self.psCompleteDict[key]['plvValues'])

                #set tags
                stateTag='state-' + str(self.psCompleteDict[key]['ourState'])
                trackTag=self.psCompleteDict[key]['tracked']
                self.plvTree.item(key, tags=[stateTag, trackTag])

                #age goes from new=-3, active=0, old=3+



            # #   Using our list of PIDS 2 be Graphed, Tag the pertinent PIDS in the PidDict
            #
            #
            # # Redraw our GUI table.
            # # delete current GUI contents
            # self.plvTree.delete(*self.plvTree.get_children())
            # # create a new GUI table
            #
            # for dictKey in self.pidDict.keys():
            #     # self.plvTree.delete('')
            #     listEntries = self.pidDict[dictKey]
            #     # listEntries = str(dictEntry).split()
            #     self.plvTree.insert('','end',iid=dictKey, text=dictKey,values=(listEntries))
            #     #                    1    2    ========== keywords =============================
            #     # 1 - parent   ('' means no parent)
            #     # 2 - position in parent ('end' means last position)
            #     # KEYWORDS:
            #     #    iid       item identifies
            #     #    text      item text
            #     #    values    values to put into table
            #     #    tags
            #     #### Later can use      self.plvTree.tag_configure("selected", background='green')
            #
            #     # ---- TEST BELOW ----
            #     ###self.plvTree.item()
            #     ###self.plvTree.item( self.plvTree.identify_row(), tags=("bold", 'red'))   #<---------------------- !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1
            #     # ---- TEST ABOVE  ----
            #     # self.pidDict[str(wordList[0])])
            #     # result = self.plvTree.identify_row(i)
            #     # childr = self.plvTree.get_children()
            # # print('plvTree children:',self.plvTree.get_children)
            #
            # # for each PID to be graphed....add tag "2bGraphed" in the plvTree
            # for graphPID in self.pids2graph.keys():
            #
            #     if graphPID in self.pidDict.keys():
            #         self.plvTree.item(graphPID, tag='2bGraphed')
            #     # end if
            # # end loop
            #
            # # Highlight in green each process to be graphed.
            # self.plvTree.tag_configure('2bGraphed', background='green')
            #
            # # pidCo
            # # for rowEntry in self.plvTree['PID']:
            # #     pass
            #
            #
            # #ky--
            # #for all pids in pid column, update the other columns.
            #     #if column pid found in procList, update value. reset any highlights
            #         #remove pid from procList
            #     #if pid in column not found in current procList, highlight it
            # #for all pids remaining in procList
            #     #insert value on column and highlight
            # # for treeEntryPID in self.plvTree:
            # #     pass
            #
            # #run column sort
            self.columnSort(self.plvTree)
            # if(self.desigCol is None):
            #     self.columnSort(self.plvTree, 'RAM%', 1)
            # else:
            #     self.columnSort(self.plvTree)

            if (wordList[0] == '4139'):
                a1 = self.psCompleteDict[keyPIDcomm]
                print('firefox')

        else:
            print('not updating data')

        # print('bool is:'+str(self.boolTakeInData))

        self.firstRun=False
        self.periodicUpdateOfGraphNEW()
        self.after (self.updateIntervalMS, self.periodicUpdateProcIDList)        # -------> periodic update


###########

    #-----------------------------------------------------------------------------
    def create_timeGraphContentsGUI(self, parent):
    #-----------------------------------------------------------------------------
    # Purpose:  Called one time to create the Time Graph GUI.
    #-----------------------------------------------------------------------------
        #  #frame - processes time graph
        # timeGraphFrame=tk.Frame()
        cpuFrame = tk.Frame(parent)
        memFrame = tk.Frame(parent)

        selectFrame=tk.Frame(parent)

        cpuFrame.grid( row=2, column=2,sticky='nsew')
        memFrame.grid( row=4, column=2,sticky='nsew')
        selectFrame.grid(row=2,column=4, sticky='ns',rowspan=2)

        parent.grid_columnconfigure(2, weight=2)
        # # parent.grid_rowconfigure(1, weight=1)#for test matplot
        parent.grid_rowconfigure( 2, weight=2)
        # parent.grid_rowconfigure( 4, weight=2)
        # # parent.grid_rowconfigure( 3, weight=1)
        # parent.grid_rowconfigure( 6, weight=2)

        # tk.Button(cpuFrame, text='cpu').pack(fill='both',expand=1,)
        # tk.Button(memFrame, text='mem').pack(fill='both',expand=1)
        # tk.Button(idkFrame, text='other').pack(fill='both',expand=1)

        self.selectedProcBox(selectFrame)

        # region matplotlib          ------------------------------------

            #container frame for all matplotGUI
        matplotFrame = tk.Frame(cpuFrame, relief='sunken',bg='blue')
        matplotFrame.pack(side='left', fill='both', expand=1)

            # Format plt-fig-axes layout
        fig,(axCPU,axMem) = plt.subplots(2, sharex='all', sharey='all')#3,sharex='col',sharey='row'
        #axArr=(axCPU,axMem) #column

        plt.subplots_adjust(left=0.07, bottom=0.15, right=0.98, top=0.88, wspace=None, hspace=None)



        # -- done setting up plt-fig-ax layouts --

        # x=np.arange(0,6.74,0.01)                         # X range.  (From (Starting At), To(ending at), By Increment size)
        #
        #                                                  # Python Note:   X is ALWAYS the first item set.
        # t = np.arange(0.0, 3.0, 0.01)                    # First Item  (X)  Go from 0.0 to 3.0 by size 0.1
        # s = np.sin(2 * np.pi * t)                        # Second Item (Y)  What to plot
        # axCPU.plot(t, s)                                    # Plot the X (t)  and Y (s) values


        # Embed the matplotlib gui in a tkFrame
        # a tk.DrawingArea
        self.canvas = FigureCanvasTkAgg(fig, master=matplotFrame)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side='top', fill='both', expand=1)

        toolbar = NavigationToolbar2TkAgg(self.canvas, matplotFrame)
        toolbar.update()
        self.canvas._tkcanvas.pack(side='top', fill='both', expand=1)

        def on_key_event(event):
            print('you pressed %s' % event.key)
            key_press_handler(event, self.canvas, toolbar)
        def object_pick_event(event):
            aStr=event.artist.get_label()
            splitStr = aStr.split('-')
            if(len(splitStr[0])>1):
                self.psCompleteDict[splitStr[0]]['tracked']='notTracked'
                event.artist.set_visible(False)
            print(splitStr)
            # self.psCompleteDict[]
            #event.artist.get_label
            #if object picked is legend line

            #if object picked is drawn line
            print(event.artist.get_label())
            pass

        self.canvas.mpl_connect('pick_event', object_pick_event)
        self.canvas.mpl_connect('key_press_event', on_key_event)
        # make any variables class values if needed
        self.axCPU=axCPU
        self.axMem=axMem
        # endregion matplotlib         --------------------------------------

        print('Scheduling periodic update of:  ', self.updateIntervalMS)
        # self.after(self.updateIntervalMS, self.periodicUpdateOfGraph)    # ----> periodic update

        self.ActivePIDbeingGraphed_i = -1

        #end create_timeGraphContentsGUI

    # -----------------------------------------------------------------------------
    def periodicUpdateOfGraphNEW(self):


        # axCPU
        self.axCPU.clear()
        self.axCPU.set_title('CPU Usage')  # Title of Graph.  Centered.  Above Graph.
        self.axCPU.set_ylabel('CPU Usage(%)')  # Title of Left   (Y)
        # axCPU.set_xlabel('Time(s)')                         # Title of Bottom (X)

        # axMem
        self.axMem.clear()
        self.axMem.set_title('Memory Usage')  # Title of Graph.  Centered.  Above Graph.
        self.axMem.set_ylabel('Mem Usage(%)')  # Title of Left   (Y)
        self.axMem.set_xlabel('Time(s)')

        self.axCPU.set_autoscale_on(False)
        self.axMem.set_autoscale_on(False)
        curTime = time.time()
        self.axCPU.set_xbound(curTime-self.timeTrackDurat,curTime+1)
        self.axCPU.set_ybound(0, 100)

        self.axCPU.set_xticks(np.arange(curTime-self.timeTrackDurat,curTime+1,5))
        lablLis = []
        for i in np.arange(0, self.timeTrackDurat+1, 5):
            lablLis.append(str(i))
        self.axCPU.set_xticklabels(lablLis)

        for key in self.psCompleteDict.keys():
            if self.psCompleteDict[key]['tracked']=='tracked':
                linelabel = self.psCompleteDict[key]['pid'] + '-' + self.psCompleteDict[key]['name']
                # i=0
                # for aLine in self.axCPU.get_lines():
                #     if linelabel == aLine.get_label():
                #         i=1
                #         break
                # if i==1: continue
                # for aLine in self.axCPU.get_lines():
                #     if aLine.get_label() ==linelabel:
                #         pass

                xTime = self.psCompleteDict[key]['timelist']
                yCpuPer = self.psCompleteDict[key]['cpu%list']
                yMemPer = self.psCompleteDict[key]['mem%list']


                self.axCPU.plot(xTime,yCpuPer,'-o',label=linelabel,picker='5')
                self.axMem.plot(xTime, yMemPer,'-o', label=linelabel)

        handles, labels = self.axCPU.get_legend_handles_labels()
        self.axCPU.legend(handles, labels)
        self.canvas.show()

    # -----------------------------------------------------------------------------



    # #-----------------------------------------------------------------------------
    # def periodicUpdateOfGraph(self):
    # #-----------------------------------------------------------------------------
    # # Purpose:  This method is called periodically.  It does a Linux command
    # #        and processes the linux output, filtering and organizing the data.
    # #        and displaying filtered results in a table.
    # #-----------------------------------------------------------------------------
    #     # print('Graph update')
    #     if(self.boolTakeInData): #for some reason this isn't getting the memo when pause is pressed.
    #
    #
    #
    #
    #         # 1) New different PID: See if user requested us to change the PID we are recording, and switch if necessary.
    #         reqPID = str(self.PID_ReqToBeGraphed_i)     # PID user has entered at the GUI
    #
    #         if ( reqPID >= str(0) ):        # str() vs int
    #             # Yes, this is a new new requested PID
    #             print ('(((((((((( GRAPH:Verifying reqPID', reqPID, ' )))))))))))))))))'  )
    #             reqPIDstr = str(reqPID)
    #
    #             rowDataForPID = {}
    #             # verify the PID actually exists
    #             try:
    #               rowDataFor_reqPID = self.pidDict[reqPIDstr]
    #             except:
    #                 print(    'NOT VALID reqPIDstr:', reqPIDstr)
    #
    #             if (len(rowDataFor_reqPID) < 3):
    #                 print('   NO Data for what appears to be a VALID PID: Will not graph')
    #             else:
    #                 # Yay! PIDid is valid (there is valid data for it in the list).
    #                 # We will switch over the GRAPH mode and graph it.
    #                 self.ActivePIDbeingGraphed_i = int(reqPIDstr)    # New PID to be graphed.
    #                 self.PID_ReqToBeGraphed_i    = int(-1)           # clear request
    #
    #                 # use new Requested PID. and clear old data (by setting the queues head = tail)
    #                 print("----------------- CLEARING QUEUES --------------------------------")
    #                 print("----------------- CLEARING QUEUES --------------------------------")
    #                 print("----------------- CLEARING QUEUES --------------------------------")
    #                 self.ActivePIDbeingGraphed_i = int(reqPID)
    #                 self.head_oldest = self.tail_newest
    #
    #
    #                 # switch over the GRAPH mode (if we are not in GRAPH mode)
    #                 print("   VALID PID ===> Switching to graph mode:  self.raiseFrame( timeGraph)")
    #                 self.raiseFrame('timeGraph')   # ----> exit
    #
    #         # Normal processing:
    #         #   Gather data on any valid process requested.   We gather data whether or not we are in
    #         #   graphics mode.    That way when the user switches to graphics mode we already have data.
    #
    #         # ---------- For Reference when using the queues ------------------------------------
    #         # self.Q_size      = 300
    #         # self.head_oldest =   1    # front of Queue. If other data is added, this is the oldest data.
    #         # self.tail_newest =   1    # end of Queue.  Items get in line here.  Has the newest data.
    #
    #         # Save Newest data to Queue
    #         timestamp   = time.time()
    #         timestamp_f = float(timestamp)
    #         timestamp_str = str(timestamp)
    #         timestamp2  = time.gmtime(time.time() )
    #         print('Gtime:  time (',  timestamp,  ')  timestamp2(' , timestamp2, ')' )
    #
    #         print('a > b :  a = ', self.ActivePIDbeingGraphed_i, ' b = ', str(0) )
    #
    #         # 3) make sure PID is valid
    #         #if (self.ActivePIDbeingGraphed_i >= 0 ):
    #         pid_count = len(self.pids2graph)
    #         if pid_count > 0:
    #             # We can gather data for this ID
    #             print ("Gather data for activeID:", self.ActivePIDbeingGraphed_i)
    #             pid_count = len(self.pids2graph)
    #             if pid_count > 0:
    #                 secondParam_str = '-q'
    #                 pid_count = len(self.pids2graph)
    #                 isFirst = bool(1)
    #                 # loop through keys
    #                 for graphPID in self.pids2graph.keys():
    #                     if isFirst:
    #                         secondParam_str += str(graphPID)     # -q2
    #                         isFirst = bool(0)
    #                     else:
    #                         secondParam_str += "," + str(graphPID)    # -q2,4
    #                 # end loop
    #             # end if
    #
    #             #secondParam_str = '-q' + str(self.ActivePIDbeingGraphed_i)
    #
    #             print ('secondParam:(', secondParam_str, ')' )
    #             #  command: "ps -q2,4,6 -o pid,pcpu,pmem,user,comm,cmd"
    #             #  where:     q# = query for given process it
    #             #           pid  = Process ID
    #             #           pcpu = Percentage CPU utilization
    #             #           pmem = Percentage Memory utilization
    #             #           user = User Name
    #             #           comm = Command being executed
    #             #           cmd  = full long version of command
    #             # "--sort=-pcpu" = Sort data based on percentage CPU utilization
    #             #
    #             #                "ps    -Ao    pid,pcpu,pmem,user,comm,cmd    --sort=-pcpu"
    #
    #             process = Popen(['ps', secondParam_str, '-o', 'pid,pcpu,pmem,user,comm,cmd'], stdout=PIPE, stderr=PIPE)
    #             stdout,_= process.communicate()
    #
    #             i = -1
    #
    #             # 4) SAVE latest data to Queue.
    #             #    Parse through linux returned list of lines, and extract and save pertent items.
    #             for line in stdout.splitlines():
    #                 i = i + 1
    #                 print ('Gline(', i, ')', line)   ## Debug: line read in.
    #                 if (i == 0):
    #                    continue    # ---> skip the first line (it is a title line)
    #
    #                 type(line)
    #                 decodeLine = line.decode('ascii', 'ignore')
    #                 #                                  ^^^^^^
    #                 #                                  ignore is used to not fail on unicode names (like web items from firefox)
    #
    #                 wordList = decodeLine.split()        # wordList has a list created from the items in the line
    #                 print('spliting word list', wordList)
    #
    #                 # ------------------- sample result ---------------------------------------------
    #                 #   Gline( 0 ) b'  PID %CPU %MEM USER     COMMAND         CMD'
    #                 #   Gline( 1 ) b' 4716 19.7  2.1 kmyren   python3         python3 ks.py'
    #                 #                   0    1    2   3         4               5
    #                 #   spliting word list ['4716', '19.7', '2.1', 'kmyren', 'python3', 'python3', 'ks.py']
    #                 # ------------------- sample result ---------------------------------------------
    #
    #                 # ------------------ what we want to load into our record -----------------
    #                 # self.timeQueue[x].
    #                 #                   [0] timestamp
    #                 #                   [1] pid
    #                 #                   [2] pcpu
    #                 #                   [3] pmem
    #                 # ------------------ what we want to load into our record -----------------
    #
    #                 # 5) VALID data: then SAVE latest data to Queue.
    #                 if( len(wordList) >= 4 ):
    #                     # load Record
    #                     #timeRec [0] = timestamp_str # 0 timestamp
    #                     #timeRec [1] = wordList[1]   # 1 pid
    #                     #timeRec [2] = wordList[2]   # 2 pcpu
    #                     #timeRec [3] = wordList[3]   # 3 pmem
    #
    #                     # ---------------- Queue format -----------------------------------
    #                     #  self.Q_size      = 300
    #                     #  self.head_oldest =   1    # front of Queue. If other data is added, this is the oldest data.
    #                     #  self.tail_newest =   1    # end of Queue.  Items get in line here.  Has the newest data.
    #                     # -----------------------------------------------------------------
    #                     self.tail_newest = (self.tail_newest + 1) % self.Q_size       # where % = modulo function
    #                     if ( self.tail_newest == self.head_oldest):
    #                         # bumped into itself.  Increment head (with the oldest stuff up one)
    #                         self.head_oldest = (self.head_oldest + 1) % self.Q_size   # where % = modulo function
    #
    #                     # print ('Queue:  head_oldest=', self.head_oldest, '  tail_newest=', self.tail_newest)  # Debug Queu Head and Tail
    #                     print ("=====> SAVING ', ,' to NEW TO TAIL (", self.tail_newest, ")         Note: Head is (", self.head_oldest, ")" )
    #                     # load the timeQueue record
    #                     #self.timeQueue[ self.tail_newest ] [0:3] =  timeRec[0:3]
    #                     print ("wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww")
    #                     print("   wordList array: ", wordList)
    #                     print ("wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww")
    #
    #                     # SAVE Latest times to our Queue record ===> save
    #                     self.timeQueue[ self.tail_newest ] ['timestamp'] = float(timestamp)
    #                     self.timeQueue[ self.tail_newest ] [      'pid'] = float(wordList[0] )  # 1 pid
    #                     self.timeQueue[ self.tail_newest ] [     'pcpu'] = float(wordList[1] )  # 2 pcpu
    #                     self.timeQueue[ self.tail_newest ] [     'pmem'] = float(wordList[2] )  # 3 pmem
    #
    #                     # -------------- record struct ----------------------------------------------------------
    #                     #   self.timeQueue = np.zeros ( self.Q_size,
    #                     #                      dtype = { 'names'   :['timestamp','pid','pcpu','pmem','str40'],
    #                     #                                'formats' :[       'f8', 'f8',  'f8',  'f8',  'a40'] } )
    #                     # -------------- record struct ----------------------------------------------------------
    #                 # end if
    #
    #
    #
    #                 # 6) GRAPHICS: Set up the Title, and X,Y Lables
    #
    #                 self.axCPU.clear()    # clear previous lines from GUI
    #
    #                 self.axCPU.set_title('PID = ' + str(self.ActivePIDbeingGraphed_i) )  # Title of Graph.  Centered.  Above Graph.
    #                 self.axCPU.set_ylabel('percent CPU -Ylabel')             # Title of Left   (Y)
    #                 self.axCPU.set_xlabel('Elapsed Time(s)')                 # Title of Bottom (X)
    #
    #
    #                 # 7) Create an array of X values (to plot the time in elapsed seconds)
    #                 #    Initialize zeroed  Y values (which we will fill in further below)
    #
    #                                                   # Python Note:   X is ALWAYS the first item set.
    #                 x1 = np.arange (0, 300, 1)         # First Item  (X)  (From 0 to 300 by 1)
    #                 y1 = np.zeros  (300)               # Second Item (Y)  array of 300 with values zeroed out
    #
    #                 # 8) Fill in the Y values with data that we do have.
    #                 #    loop thru queue, and plot backwards in time.  Start at TAIL (latest data) and walk down
    #                 #       until reaching the HEAD.   So we load the plot backwards:  299, 298, 297, ...
    #                 GRAPH_index = self.Q_size -1     # 299
    #
    #                 HEAD_i   = int(self.head_oldest)
    #                 TAIL_i   = int(self.tail_newest)
    #                 i        = int(self.tail_newest)   # <--- Start at the TAIL (latest data) and plot left until reaching TAIL
    #                 CurVal_f = float(0)
    #                 CurNumOfEntries = 0
    #                 MaxVal_f = float(0)
    #                 for r in range (0, self.Q_size-1):
    #                     # The above loop is simply to prevent runaway code.  We should get to the end before loop runs out
    #                     # We will start with the latest (the tail) and plot BACKWARDS (going left) <------
    #                     if ( i == HEAD_i):
    #                         # started at TAIL and reached HEAD. exit
    #                         print('Loop: Reached END. HEAD(', HEAD_i, ') == i(', i, 'Leaving loop with MAX(', MaxVal_f,
    #                            ')  NumOfEntries(', CurNumOfEntries, ')  ----->')
    #                         break     #  ----> exit loop
    #
    #                         # Get value from queue
    #                         CurVal_f = self.timeQueue [ i ]['pcpu']
    #                         print( i, ": ", self.timeQueue[i] )
    #
    #                         # Y GRAPH:  Load value into Graph list
    #                         y1 [ GRAPH_index ] = CurVal_f
    #                         print ( "GraphI: ", GRAPH_index, " = ", y1[ GRAPH_index] )
    #
    #                         if (CurVal_f > MaxVal_f):
    #                             MaxVal_f = CurVal_f    # new Max Val
    #
    #                             CurNumOfEntries += 1
    #                             # bump down to next item in queue.
    #                             GRAPH_index = GRAPH_index -1
    #                         if (i == 0):
    #                             i=self.Q_size -1              # reached queue bottom, so wrap around to the top
    #                         else:
    #                             i = (i - 1)
    #                 # end loop
    #
    #                 # 9) Calculate the Y SCALE to use, based on the "MaxVal" calculated above
    #                 YfinalScale_f = 1.0
    #                 Yincrements_f = 0.1
    #                 if (MaxVal_f > 10):
    #                     # if the Max value is above 5, set the Y value to an increments of 5.
    #                     intDivideBy5 = int ( MaxVal_f / 5.0)            # 6  becomes (6/5) = 1
    #                     intRoundedDownBy5   = int ( intDivideBy5 * 5)   #    1*5  become 5
    #                     YfinalScale_f   = intRoundedDownBy5 + 5         #    5+5 => 10 is the scale
    #                     Yincrements_f   = 5.0
    #                 elif (MaxVal_f > 2):
    #                     # if the Max value is above 2, set the Y value to an increments of 2.
    #                     intDivideBy2 = int ( MaxVal_f / 2.0)            # 7  becomes (7/2) = 3
    #                     intRoundedDownBy2   = int ( intDivideBy2 * 2)   #    3*2  become 6
    #                     YfinalScale_f   = intRoundedDownBy2 + 2         #    6+2 => 8 is the scale
    #                     Yincrements_f   = 1.0
    #                 elif (MaxVal_f > 0.3):
    #                     # if the Max value is above 0.3 set the Y value to an increments of 0.1
    #                     intDivideByTenths      = int ( MaxVal_f / 0.1)              # 0.5 becomes (0.5/ 0.1) = 5
    #                     intRoundedDownByTenths_f = float ( intDivideByTenths * 0.1) #    5*0.1 become 0.5
    #                     YfinalScale_f   = intRoundedDownByTenths_f + 0.1          #    0.5 + 0.1 => 10 is the scale
    #                     Yincrements_f   = 0.1
    #                 else:
    #                     YfinalScale_f   = MaxVal_f
    #                     Yincrements_f   = 0.1
    #                 # end if.  The scale is now in "YfinalScale".
    #
    #                 print("         +++++ Y SCALE:  ", YfinalScale_f, "  ++++++++++++" )
    #
    #                 # 10) GRAPHICS:  Send X,Y data out to be graphed.
    #                 print ("Go DRAWa ====================")
    #
    #                 ########self.canvas.delete("plot")
    #                 # Python Note:   X is ALWAYS the first item set.
    #                 # self.ax.xlim(0.0, YfinalScale)       # <== invalid. if not used, self scaling is automatically used.
    #                 # self.axCPU.plot(x1, y1)                   # Plot the X (t)  and Y (s) values
    #                 #
    #                 # # TEST ======================
    #                 # y2 = np.zeros(300)  # Second Item (Y)  array of 300 with values zeroed out
    #                 # y2[200:250] = y1[250:300]
    #                 # self.axCPU.plot(x1, y2)  # Plot the X (t)  and Y (s) values
    #                 #
    #                 # y3 = np.zeros(300)  # Second Item (Y)  array of 300 with values zeroed out
    #                 # y3[150:200] = y1[250:300]
    #                 # self.axCPU.plot(x1, y3)  # Plot the X (t)  and Y (s) values
    #                 #
    #                 # y4 = np.zeros(300)  # Second Item (Y)  array of 300 with values zeroed out
    #                 # y4[100:150] = y1[250:300]
    #                 # self.axCPU.plot(x1, y4)  # Plot the X (t)  and Y (s) values
    #
    #                 # TEST ======================
    #
    #                 self.canvas.show()
    #                 print ("Go DRAWb ====================")
    #
    #     # self.after  (self.updateIntervalMS, self.periodicUpdateOfGraph)        # -------> periodic update
    # ## end periodicUpdateOfGraph(self):

    #-----------------------------------------------
    def toggleUpdate(self, aBool):
        #-----------------------------------------------
        # Toggle pause resume method
        #-----------------------------------------------
        self.boolTakeInData = aBool
        # print('Update Data is:'+str(aBool))
    
    #-----------------------------------------------
    def raiseFrame(self, frameRaised):
        #-----------------------------------------------
        # Bring proc or time graph to top
        #-----------------------------------------------
        frame = self.dictFrames[frameRaised]
        frame.tkraise()

    #-----------------------------------------------
    def printScreen(self):
        #-----------------------------------------------
        # save a screenshot of each window
        # save location is configurable in options window
        #-----------------------------------------------
        pass


# ----------------------- MAIN ---------------------------------------------------
##MAIN##
if __name__ == '__main__':
    #this runs if this is the first/start program in execution
    print(__name__)
    print('Main case start')
    
    root = tk.Tk()
        # define all the window preferences
    root.title('PySysMonitor')
    width,height, xPos, yPos = [1000,700,70,70]
    root.geometry('%dx%d+%d+%d' % (width,height, xPos, yPos))
    #root.minsize(400, 300)#wont let user shrink below this

    # change X close behavior to better terminate program
    def on_closing():
        root.quit()
    root.protocol("WM_DELETE_WINDOW", on_closing)

    #fill root window with pySysMonitor frame
    PySysMonitor_gui(root)
    root.mainloop()
    print('program ending')
    
if __name__ != '__main__':
    #this runs if the .py file is called during a different classes execution
    print(__name__)
    print('NOT main case')
    
print('end of file')

