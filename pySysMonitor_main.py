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
import matplotlib as mpl
mpl.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
# implement the default mpl key bindings
from matplotlib.backend_bases import key_press_handler
import matplotlib.pyplot as plt
import matplotlib.animation as mplAnimat

from pprint import pprint
import tkinter as tk
import tkinter.font as tkFont
import tkinter.ttk as ttk
import numpy as np
import time
# from tkinter import *
# from tkinter.ttk import *
import re
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
    def open_singleProcProp(self, pidStr):
        #----------------------------------------------------------------------------
        # Purpose: To bring up the popup PROCESS PROPERTIES display.
        #    When the user clicks on the PROC_PROP button, the popup window will appear
        #    where the user can custimize some options.
        #  There is a CANCEL button at the bottom.
        #----------------------------------------------------------------------------
        procPropWind = tk.Toplevel()
        procPropWind.title('PySysMonitor - Process Properties')
        # ===============================================================================

        #'parentName'
        listLabels=[]
        tk.Label(procPropWind, text='Fixed Properties').grid(row=0, column=1, columnspan=2)
        fixedList=['PID', 'Name', 'PPID', 'UID', 'User name', 'Start time', 'args']
        # fixedList = ['pid', 'name', 'uid', 'user']
        for i in range(0,len(fixedList)):
            tk.Label(procPropWind, text=fixedList[i]).grid(row=i+1, column=1,sticky='E')
            # strData = self.psCompleteDict[pidVal][fixedList[i]]
            aLabel =tk.Label(procPropWind, text='--IN Progress--')
            aLabel.grid(row=i+1, column=2,sticky='E')
            listLabels.append(aLabel)

        tk.Label(procPropWind, text='Variable Properties').grid(row=15, column=1,columnspan=2)
        fixedList = ['CPU Time','Priority','Active Status','Virtual Mem']
        # 'UserTime',
        # fixedList = ['pid', 'name', 'uid', 'user']
        for i in range(0, len(fixedList)):
            tk.Label(procPropWind, text=fixedList[i]).grid(row=i+20, column=1,sticky='E')
            # strData = self.psCompleteDict[pidVal][fixedList[i]]
            aLabel = tk.Label(procPropWind, text='--IN Progress--')
            aLabel.grid(row=i+20, column=2,sticky='E')
            listLabels.append(aLabel)


        listArgs=['pid','comm','ppid','uid','user','start_time','args',
                  'cputime','s', 'pri','sz']
        listWords=[]
        for arg in listArgs:
            process = Popen(['ps', '-p', pidStr, '-o', arg+'='], stdout=PIPE, stderr=PIPE)
            stdout, _ = process.communicate()
            strAsc = stdout.decode('ascii', 'ignore')
            strAsc=strAsc.rstrip()
            strAsc=re.sub("(.{48})", "\\1\n", strAsc, 0, re.DOTALL)
            listWords.append(strAsc)
            print(arg,'  - ',strAsc)
        # ==  Set Labels to display info ========
        listLabels[0]['text'] =   listWords[0]
        listLabels[1]['text'] =   listWords[1]
        listLabels[2]['text'] =   listWords[2]
        listLabels[3]['text'] =   listWords[3]
        listLabels[4]['text'] =   listWords[4]
        listLabels[5]['text'] =   listWords[5]
        listLabels[6]['text'] =   listWords[6]
        listLabels[7]['text'] =   listWords[7]
        listLabels[8]['text'] =   listWords[8]
        listLabels[9]['text'] =   listWords[9]
        listLabels[10]['text'] =  listWords[10]
        # listLabels[11]['text'] =  listWords[11]
        # listLabels[12]['text'] =  listWords[12]
        # listLabels[13]['text'] =  listWords[13]
        # listLabels[14] =          listWords[0]



        # ===============================================================================
        # Create the buttons for the Bottom Bar:
        #                    CANCEL        #
        # ===============================================================================
        cancelBut = tk.Button(procPropWind, text='Cancel', command=lambda: procPropWind.destroy())
        cancelBut.grid(row=100, column=1, columnspan=2)

        # region matplotlib          ------------------------------------

        # container frame for all matplotGUI
        matplotFrame = tk.Frame(procPropWind, relief='sunken', bg='blue')
        matplotFrame.grid(row=1,column=3,rowspan=90,sticky='NSEW')

        # Format plt-fig-axes layout
        fig, ax = plt.subplots()
        ax.set_title('CPU Usage')  # Title of Graph.  Centered.  Above Graph.
        ax.set_ylabel('Percent')  # Title of Left   (Y)
        ax.set_xlabel('Time(s)')
        # -- done setting up plt-fig-ax layouts -
        ax.set_autoscale_on(False)
        ax.set_ybound(0, 100)
        lablLis = []
        for i in np.arange(0, self.timeTrackDurat + 1, 5):
            lablLis.append(str(i))
        lablLis.reverse()
        ax.set_xticklabels(lablLis)
        # --#--#
        x_data = [0,1,2,3]+self.psCompleteDict[pidStr]['timelist']#[0, 1, 2, 3, 4, 5, 6]
        y_data = [0,1,2,3]+self.psCompleteDict[pidStr]['cpu%list']#[0, 0, 0, 1, 2, 3, 4]
        lnAnim, = ax.plot(x_data, y_data, 'ro-', animated=True)

        # curTime = time.time()
        # .set_xbound(curTime - self.timeTrackDurat, curTime + 1)

        figCanvas = FigureCanvasTkAgg(fig, master=matplotFrame)
        figCanvas.get_tk_widget().pack(side='top', fill='both', expand=1)

        toolbar = NavigationToolbar2TkAgg(figCanvas, matplotFrame)
        toolbar.update()
        figCanvas._tkcanvas.pack(side='top', fill='both', expand=1)

        def updateMethod(updateCounter):
            print('-updateCount=', updateCounter)
            curTime = time.time()
            ax.set_xticks(np.arange(curTime - self.timeTrackDurat, curTime + 1, 5))
            ax.set_xbound(curTime - self.timeTrackDurat, curTime + 1)
            x_data=self.psCompleteDict[pidStr]['timelist']
            y_data=self.psCompleteDict[pidStr]['cpu%list']
            print(x_data,y_data)
            lnAnim.set_data(x_data,y_data)
            figCanvas.show()
            return lnAnim,

        ani = mpl.animation.FuncAnimation(fig, updateMethod,interval=1000,blit=True)
        #--#--#
        print('-after updatr set-',lnAnim)

        # Embed the matplotlib gui in a tkFrame
        figCanvas.show()

        # def on_key_event(event):
        #     print('you pressed %s' % event.key)
        #     key_press_handler(event, figCanvas, toolbar)
        #
        # def object_pick_event(event):
        #     aStr = event.artist.get_label()
        #     splitStr = aStr.split('-')
        #     if (len(splitStr[0]) > 1):
        #         self.psCompleteDict[splitStr[0]]['tracked'] = 'notTracked'
        #         event.artist.set_visible(False)
        #     print(splitStr)
        #     # self.psCompleteDict[]
        #     # event.artist.get_label
        #     # if object picked is legend line
        #
        #     # if object picked is drawn line
        #     print(event.artist.get_label())
        #     pass
        # figCanvas.mpl_connect('pick_event', object_pick_event)
        # figCanvas.mpl_connect('key_press_event', on_key_event)

        # make any variables class values if needed
        # endregion matplotlib         --------------------------------------
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

        # togVisibBut = tk.Button(listscrolFrame, text='Toggle Visible')
        # togVisibBut.pack(side=tk.BOTTOM, fill=tk.X)

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

        # for i in range(100):
        #     self.lbSelected.insert(tk.END, 'a' + str(i) + 'c')

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
            curVal=self.lbSelected.get(tk.ANCHOR)
            if curVal != '':
                self.togTrackedPID(curVal)


        #
        def singClikLsbx(event):
            #idk what my plan for this guy is
            pass
            # a0 = self.lbSelected.curselection()  # this gets changed between click and release events #tuple of selection
            # a3 = self.lbSelected.get(tk.ANCHOR)  # same as above. val is that is box clicked. #init state is ''
            # a1 = self.lbSelected.get(tk.ACTIVE)  # this gets changed after release events #val of active #init state is first listbox

            # aLabel2['text'] = str()

        def doubClikLsbx(event):
            print('dub click')

        def singRighClik(event):
            curVal=self.lbSelected.get(tk.ANCHOR)
            print('right click. pidStr=',curVal)
            if(curVal != ''):
                self.open_singleProcProp(curVal)


        # togVisibBut['command'] = togVis
        remTrakBut['command'] =  remove
        self.lbSelected.bind("<Double-Button-1>", doubClikLsbx)
        self.lbSelected.bind("<ButtonRelease-1>", singClikLsbx)
        self.lbSelected.bind("<ButtonRelease-3>", singRighClik)
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

        #------ Right Click -----------
        def myRightClickEvent(event):
            print("============ plvTree:  RC event =========================")
            if plvTree.focus() !='':
                iidOfTree = plvTree.focus()  # get row
                dictOfRow = plvTree.item(iidOfTree)
                self.open_singleProcProp(str(iidOfTree))
                print(iidOfTree)
                print(self.psCompleteDict[iidOfTree])

        plvTree.bind("<Button-3>", myRightClickEvent)

        # ------ Double Left Click -----------
        def myEventDoubleClick(event):
            print ("============plvTree: Double Left click event =========================")
            #toggle tag,
            # if in tree, remove it.  If not in tree, add it
            iidOfTree = plvTree.focus()  #getRow, is str pidVal
            dictOfRow = plvTree.item(iidOfTree)
            pidRow = dictOfRow['values'][0]     #  int pidVal

            pidStr=iidOfTree
            pidInt=pidRow

            self.togTrackedPID(pidInt)




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
                if self.firstRun and i<6:
                    self.psCompleteDict[keyPIDcomm]['tracked']='tracked'
                    self.lbSelected.insert(tk.END,wordList[0])

            toDelete=[]
            for key in self.psCompleteDict.keys():
                # check if key, and therefore entry exists in tree
                # insert if not
                if self.plvTree.exists(key):
                    if self.psCompleteDict[key]['ourState']>3 and self.psCompleteDict[key]['tracked'] !='tracked':
                        #remove old ps from tree and dict
                        self.plvTree.delete(key)
                        toDelete.append(key)

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

            for key in toDelete:
                del self.psCompleteDict[key]


            self.columnSort(self.plvTree)

            if (wordList[0] == '4139'):
                a1 = self.psCompleteDict[keyPIDcomm]
                print('firefox')

        else:
            print('not updating data')

        # print('bool is:'+str(self.boolTakeInData))

        self.firstRun=False
        self.periodicUpdateOfGraph()
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

        plt.subplots_adjust(left=0.07, bottom=0.10, right=0.98, top=0.92, wspace=None, hspace=0.24)

        # -- done setting up plt-fig-ax layouts --

        # Embed the matplotlib gui in a tkFrame
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
                self.open_singleProcProp(splitStr[0])
                # self.psCompleteDict[splitStr[0]]['tracked']='notTracked'
                # event.artist.set_visible(False)
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
    def periodicUpdateOfGraph(self):



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


                aline, = self.axCPU.plot(xTime,yCpuPer,'-o',label=linelabel,picker='5')
                self.axMem.plot(xTime, yMemPer,'-o', label=linelabel,color=aline.get_color())


        handles, labels = self.axCPU.get_legend_handles_labels()

        for aHandle in handles:
            aColor=aHandle.get_color()

            aLabel=aHandle.get_label()
            intPid = int(re.search(r'\d+', aLabel).group())

            index = self.lbSelected.get(0, "end").index(str(intPid))
            hexVal=mpl.colors.to_hex(aColor)
            self.lbSelected.itemconfig(index,background=hexVal)

        # self.axCPU.legend(handles, labels)
        self.canvas.show()


    #-----------------------------------------------
    def toggleUpdate(self, aBool):
        #-----------------------------------------------
        # Toggle pause resume method
        #-----------------------------------------------
        self.boolTakeInData = aBool
    
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

    # -----------------------------------------------
    def togTrackedPID(self, pidInt):
        # -----------------------------------------------
        # change all GUIs that relate to this PID
        #
        # -----------------------------------------------
        print ("=====      togTracked       ==========")

        pidStr=str(pidInt)


        tagState = self.psCompleteDict[pidStr]['ourState']

        if self.psCompleteDict[pidStr]['tracked']=='tracked':
            #  untrack
            #update dict, plvTree and listbox on timegraph
            self.psCompleteDict[pidStr]['tracked']='notTracked'
            self.plvTree.item(pidStr, tag=[tagState,'notTracked'])
            index = self.lbSelected.get(0, "end").index(pidStr)
            self.lbSelected.delete(index)

        else:
            #  track
            self.psCompleteDict[pidStr]['tracked'] = 'tracked'
            self.lbSelected.insert(tk.END, pidStr)
            self.plvTree.item(pidInt, tag=[tagState,'tracked'])


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

