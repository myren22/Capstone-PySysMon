'''
Created on Oct 3, 2017

@author: KyleWin10
'''
# -------------------------------------------------------------------------------------
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
#      open_optionsWindow(self):
#      make_procListViewFrame (self, parent)   return plvTree, plvFrame
#      getProcIDs(self)
#      make_timeGraphContents(self, parent)
#      toggleUpdate(self, aBool)
#      raiseFrame(self, frameRaised)
#      printScreen(self)
#    end class
#  Main code (part 2)
# -------------------------------------------------------------------------------------
# Revision History:
#  2017-11-13   Added comments.
#               Added filter to prevent logging of this command repeatedly to the PID.
#               Added PID to process ID, to be used later in the graphing.
#               Added CLEAR button to top of form, and wipe out the list and start from
#                  scratch.
#
# ------------------------------------------------------------------------------------
# Ideas:   Start Page:    Get page to start wider and higher.
#          Process Page:  Detect a click on a row, and use the  PID in that row
#                           to kick off the Graphical draw.
#
# ------------------------------------------------------------------------------------

# imports
import matplotlib

matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
# implement the default mpl key bindings
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.animation as mAnimation

import tkinter as tk
import tkinter.font as tkFont
import tkinter.ttk as ttk
import numpy as np
import time
from tkinter import *
from tkinter.ttk import *
# import re
# import subprocess
# import sys
from subprocess import Popen, PIPE

# ---#

# ---- MAIN -------------------------------------------
print('start')




# -----------------------------------------------
class PySysMonitor_gui(tk.Frame):
    # -----------------------------------------------
    # Purpose: PySysMonitor_gui provides ..
    #
    # -----------------------------------------------

    # -----------------------------------------------
    def __init__(self, parent):
        # -----------------------------------------------
        # Purpose:  To be the contructor/initialize variables in the class
        # -----------------------------------------------
        tk.Frame.__init__(self, parent)  # embeds this frame class in a parent

        self['relief'] = 'raised'
        self['borderwidth'] = 4
        self.pack(fill='both', expand=1)  # now it will be visible

        # setup window setting
        # name, size, exit button,

        # init class variables
        self.timeTick = 0
        self.dictFrames = {}
        self.pidDict = {}
        self.boolTakeInData = True
        self.updateIntervalMS = 4000
        self.timeTrackDurat = 60
        self.printSaveDir = r'/home/kyle/Software Downloads/Capstone/Screenshots'
        self.strPSatrFound = None
        self.desigCol = 'CPU%'
        self.desigDescend = 1
        self.plvTree = None

        # run create gui methods
        self.create_widgets()  #

    # ----------------------------------------------------------------------------
    def create_widgets(self):
        # ----------------------------------------------------------------------------
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
        # ----------------------------------------------------------------------------


        pass
        # topBarFrame:
        self.grid_rowconfigure(2, weight=12)
        self.grid_columnconfigure(1, weight=1)
        #region topBarFrame
        topBarFrame = tk.Frame(self, relief='sunken', borderwidth=5, bg='teal')
        topBarFrame.grid(row=1, column=1, sticky='new')

        # aButtonBox.pack(side='top',fill='both', expand=1)

        # ===============================================================================
        # Create the buttons for the Top Bar
        # Row:
        # 0:  topBarFrame
        #     buttons: PROCESS_LIST, TIME_GRAPH, PROC_PROP, OPTIONS, PRINT, RESUME, PAUSE
        #              |----------------------|  |--------------------------------------|
        #                 LEFT_BAR                          RIGHT_BAR
        #
        # ===============================================================================

        topBarFrame.grid_columnconfigure(1, minsize=40, weight=1)
        # topBarFrame.grid_columnconfigure(2, minsize=80, weight=10)
        topBarFrame.grid_columnconfigure(3, minsize=80, weight=1)

        # left button frame and its contents
        leftButFrame = tk.Frame(topBarFrame)
        leftButFrame.grid(row=1, column=1, sticky='w')  # grid(row=0, column=0)

        # TOP_BAR: LEFT_FRAME: will have buttons PROCESS_LISTS and TIME_GRAPH
        # button: PROCESS_LIST
        procListBut = tk.Button(leftButFrame, text='Process List')
        procListBut.grid(row=1, column=0)
        procListBut['command'] = lambda name='procList': self.raiseFrame(name)  # self.raiseFrame('procList')
        # Note:  python keyword "lambda" means don't execute the method, but instead just pass the method as a value

        # button: TIME_GRAPH
        timeGraphBut = tk.Button(leftButFrame, text='Time Graph')
        timeGraphBut.grid(row=1, column=1)
        timeGraphBut['command'] = lambda name='timeGraph': self.raiseFrame(name)

        # button: CLEAR
        CLEARBut = tk.Button(leftButFrame, text='CLEAR')
        CLEARBut.grid(row=1, column=2)
        CLEARBut['command'] = self.clearData  # call method clearData

        # TOP_BAR:  RIGHT_FRAME: will have PROC_PROP, OPTIONS, PRINT, RESUME, PAUSE
        # right button frame, and its contents
        rightButFrame = tk.Frame(topBarFrame)

        # button: PROC_PROP
        procPropBut = tk.Button(rightButFrame, text='Proc. Prop')  # ,padx=0.5,pady=0.5
        procPropBut.grid(row=1, column=1)
        procPropBut['command'] = self.open_singleProcProp

        # button: OPTIONS
        optionsBut = tk.Button(rightButFrame, text='Options')  # ,padx=0.5,pady=0.5
        optionsBut.grid(row=1, column=2)
        optionsBut['command'] = self.open_optionsWindow  # openOptionsWindow()
        rightButFrame.grid(row=1, column=3, sticky='e')

        # button: PRINT
        printBut = tk.Button(rightButFrame, text='Print')
        printBut.grid(row=1, column=3)  # .grid(row=0, column=1)
        printBut['command'] = self.printScreen()

        # button: RESUME
        resumeBut = tk.Button(rightButFrame, text='Resume')
        resumeBut.grid(row=1, column=4)
        resumeBut['command'] = lambda aBool=True: self.toggleUpdate(aBool)

        # button: PAUSE
        pauseBut = tk.Button(rightButFrame, text='Pause')
        pauseBut.grid(row=1, column=5)
        pauseBut['command'] = lambda aBool=False: self.toggleUpdate(aBool)
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

        # region Overlay #1:    ProcessListView
        proclistFrame = tk.Frame(plvANDtgFrame, relief='sunken', borderwidth=4, width=450)
        proclistFrame.grid(row=2, column=1, sticky='nsew')  # pack(side='left', )
        proclistFrame.grid_columnconfigure(2, weight=1)
        proclistFrame.grid_rowconfigure(2, weight=1)
        self.dictFrames['procList'] = proclistFrame

        ttk.Label(proclistFrame, text='Process List View').grid(row=0, column=2, sticky='nwe')

        procListTableFrame = tk.Frame(proclistFrame, relief='sunken', borderwidth=4)
        procListTableFrame.grid(row=2, column=2, sticky='nsew')
        self.plvTree, _ = self.make_procListViewFrame(procListTableFrame)
        #           ^ ^^
        #      comma   underscore equals

        # update tree. timer and check

        # Overlay #2:   TimeGraphFrame
        timeGraphFrame = tk.Frame(plvANDtgFrame, relief='sunken', borderwidth=4)
        timeGraphFrame.grid(row=2, column=1, sticky='nsew')
        timeGraphFrame.grid_columnconfigure(2, weight=1)
        timeGraphFrame.grid_rowconfigure(2, weight=1)
        self.dictFrames['timeGraph'] = timeGraphFrame

        ttk.Label(timeGraphFrame, text='Process Time Graph').grid(row=0, column=2, sticky='nwe')
        timeGraphTableFrame = tk.Frame(timeGraphFrame, relief='raised', borderwidth=20)
        self.make_timeGraphContents(timeGraphTableFrame)
        timeGraphTableFrame.grid(row=2, column=2, sticky='nsew')

        # self.after(self.updateIntervalMS, self.getProcIDs)

        # end create_widgets

    # ----------------------------------------------------------------------------
    def open_optionsWindow(self):
        # ----------------------------------------------------------------------------
        # Purpose: To bring up the popup OPTIONS display.
        #    When the user clicks on the OPTIONS button, the popup window will appear
        #    where the user can custimize his options.
        #  The window contains some entry fields the user can enter data in such as:
        #   the FREQUENCY, the SAVE directory, the LENGTH OF TIME tracked, etc.
        #  There are three buttons at the bottom:  ACCEPT, CANCEL, DEFAULTS
        # ----------------------------------------------------------------------------
        optionsWindow = tk.Toplevel()
        optionsWindow.title('PySysMonitor - Options')  # yep
        w = 500
        h = 400
        x = 150
        y = 120
        optionsWindow.geometry('%dx%d+%d+%d' % (w, h, x, y))
        # options i may want to make to have changeable while running
        # print screenshot save location
        # frequency of process update
        # what columns are shown in process list view
        # length of time tracked
        #

        # ===============================================================================
        # Create some Option fields where the user can enter data.
        # ===============================================================================

        #       # The window contains some entry fields
        titleLabel = tk.Label(optionsWindow, text='Configuration Options')
        titleLabel.grid(row=1, column=1, sticky='n')
        updateLabel = tk.Label(optionsWindow, text='Update Frequency(ms)')
        updateLabel.grid(row=2, column=1)
        updateEntry = tk.Entry(optionsWindow)
        updateEntry.grid(row=2, column=2)

        tk.Label(optionsWindow, text='Print Save Dir.').grid(row=3, column=1)
        printSaveDirEntry = tk.Entry(optionsWindow)
        printSaveDirEntry.grid(row=3, column=2)

        tk.Label(optionsWindow, text='Length Time Tracked(s)').grid(row=4, column=1)
        timeTrackEntry = tk.Entry(optionsWindow)
        timeTrackEntry.grid(row=4, column=2)

        tk.Label(optionsWindow, text='Columns Displayed').grid(row=5, column=1)
        # self.tree["displaycolumns"]=("artistCat", "artistDisplay") #just alter the headings listed
        pidCheckBut = tk.Checkbutton(optionsWindow, text='PID').grid(row=5, column=2)
        pcpuCheckBut = tk.Checkbutton(optionsWindow, text='pcpu').grid(row=5, column=3)
        pramCheckBut = tk.Checkbutton(optionsWindow, text='pram').grid(row=5, column=4)

        optionsWindow.grid_rowconfigure(1, minsize=50, weight=1)
        # optionsWindow.grid_rowconfigure(2, minsize=50, weight=1)
        optionsWindow.grid_columnconfigure(1, minsize=50, weight=1)
        optionsWindow.grid_columnconfigure(2, minsize=50, weight=1)

        # Accept, Cancel, Default
        # --------------------------------------------------------
        def applyOptions():
            # --------------------------------------------------------
            # Purpose: The ACCEPT button has been pressed by the user
            #   and this method then saves the values the user has changed.
            # --------------------------------------------------------

            self.updateIntervalMS = int(updateEntry.get())
            self.timeTrackDurat = int(timeTrackEntry.get())
            self.printSaveDir = printSaveDirEntry.get()

        # --------------------------------------------------------
        def restoreDefaults():
            # --------------------------------------------------------
            # Purpose: The DEFAULTS button has been pressed by the user
            #   and this method restores the values of the defaults.
            # --------------------------------------------------------
            updateEntry.delete(0, END)
            updateEntry.insert(END, str(self.updateIntervalMS))
            printSaveDirEntry.delete(0, END)
            printSaveDirEntry.insert(END, self.printSaveDir)
            timeTrackEntry.delete(0, END)
            timeTrackEntry.insert(END, self.timeTrackDurat)

        # ===============================================================================
        # Create the buttons for the Bottom Bar:
        #       ACCEPT,             CANCEL,            DEFAULTS
        #       +--applyOptions                        +--restoreDefaults
        #
        # ===============================================================================
        restoreDefaults()  # start off by loading the GUI fields with the default values

        botButFrame = tk.Frame(optionsWindow)
        botButFrame.grid(row=6, column=2)

        acceptBut = tk.Button(botButFrame, text='Accept', command=applyOptions)
        acceptBut.grid(row=1, column=2)

        cancelBut = tk.Button(botButFrame, text='Cancel', command=lambda: optionsWindow.destroy())
        cancelBut.grid(row=1, column=3)

        defaultsBut = tk.Button(botButFrame, text='Defaults', command=restoreDefaults)
        defaultsBut.grid(row=1, column=4)
        # acceptBut['command'] = lambda aBool=False: self.toggleUpdate(aBool)

        # end of open_optionsWindow
        pass

    # ----------------------------------------------------------------------------
    def open_singleProcProp(self):
        # ----------------------------------------------------------------------------
        # Purpose: To bring up the popup PROCESS PROPERTIES display.
        #    When the user clicks on the PROC_PROP button, the popup window will appear
        #    where the user can custimize some options.
        #  The window contains some entry fields the user can enter data in such as:
        #   the FREQUENCY, the SAVE directory, the LENGTH OF TIME tracked, etc.
        #  There is a CANCEL button at the bottom.
        # ----------------------------------------------------------------------------
        procPropWind = tk.Toplevel()
        procPropWind.title('PySysMonitor - Process Properties')  # yep
        w = 500
        h = 400
        x = 150
        y = 120
        procPropWind.geometry('%dx%d+%d+%d' % (w, h, x, y))
        # options i may want to make to have changeable while running
        # print screenshot save location
        # frequency of process update
        # what columns are shown in process list view
        # length of time tracked
        #

        # ===============================================================================
        # Create some Option fields where the user can enter data.
        # ===============================================================================
        titleLabel = tk.Label(procPropWind, text='Process Properties')
        titleLabel.grid(row=1, column=1)
        updateLabel = tk.Label(procPropWind, text='Update Frequency(ms)').grid(row=2, column=1)
        updateEntry = tk.Entry(procPropWind).grid(row=2, column=2)

        tk.Label(procPropWind, text='Print Save Dir.').grid(row=3, column=1)
        tk.Entry(procPropWind).grid(row=3, column=2)

        tk.Label(procPropWind, text='Length Time Tracked').grid(row=4, column=1)
        tk.Entry(procPropWind).grid(row=4, column=2)

        tk.Label(procPropWind, text='Columns Displayed').grid(row=5, column=1)
        tk.Entry(procPropWind, text='make this a checkbox').grid(row=5, column=2)

        # ===============================================================================
        # Create the buttons for the Bottom Bar:
        #                    CANCEL
        #
        # ===============================================================================
        cancelBut = tk.Button(procPropWind, text='Cancel', command=lambda: procPropWind.destroy())
        cancelBut.grid(row=6, column=2)

        procPropWind.grid_rowconfigure(1, minsize=50, weight=1)
        # optionsWindow.grid_rowconfigure(2, minsize=50, weight=1)
        procPropWind.grid_columnconfigure(1, minsize=50, weight=1)
        procPropWind.grid_columnconfigure(2, minsize=50, weight=1)

        pass

    # ----------------------------------------------------------------
    def columnSort(self, *posArgs):  # tree, col, descending,
        # ----------------------------------------------------------------
        # Purpose:  To take the passed in tree (1st parameter)
        #    and for the given column          (2nd parameter)
        #    sort the tree                     (3rd parameter)
        # The tree is then returned.
        # ----------------------------------------------------------------
        tree, col, descending = None, None, None
        if (len(posArgs) == 3):
            self.desigCol = posArgs[1]
            self.desigDescend = posArgs[2]

        tree = posArgs[0]
        col = self.desigCol
        descending = self.desigDescend

        #
        # if kwargs.has_key('tree'):
        #     tree=kwargs['tree']
        # if kwargs.has_key('col'):
        #     col = kwargs['col']
        # if kwargs.has_key('descending'):
        #     descending = kwargs['descending']

        """sort tree contents when a column header is clicked on"""
        # grab values to sort
        data = [[tree.set(child, col), child] \
                for child in tree.get_children()]
        # print('formated DATA--', data)

        # this make it so that the columns with the given names get treated as purely filled with floats
        # as opposed to filled with strings.
        floatsOnlyCols = 'CPU% RAM% PID'
        if col in floatsOnlyCols:
            for i in data:
                i[0] = float(i[0])

        data.sort(reverse=descending)

        for ix, item in enumerate(data):
            tree.move(item[1], '', ix)
        # switch the heading so it will sort in the opposite direction
        tree.heading(col, command=lambda col=col: self.columnSort(tree, col, int(not descending)))

    # -----------------------------------------------
    def onlyDrawExistingPIDS(self):
        # -----------------------------------------------
        # Purpose:  to only draw the PIDS (not query the latest info)
        #           Used to draw the cleared list allowing the user to
        #           see the list was actually clear.
        # -----------------------------------------------

        self.plvTree.delete(*self.plvTree.get_children())

        for i in range(0, 8):
            pass
        for dictKey in self.pidDict.keys():
            # loop thru list of pids  (e.g. pidDict) and load the plvTree

            listEntries = self.pidDict[dictKey]

            self.plvTree.insert('', 'end', iid=dictKey, text=dictKey, values=(listEntries))

            result = self.plvTree.identify_row(i)
            childr = self.plvTree.get_children()

    # -----------------------------------------------
    def clearData(self):
        # -----------------------------------------------
        # Toggle pause resume method
        # -----------------------------------------------
        print(' ################# clearData  ==> clearing self.pidDict and self.dictFrames')
        self.pidDict = {}
        self.onlyDrawExistingPIDS()

    # ----------------------------------------------------------------
    def make_procListViewFrame(self, parent):
        # ----------------------------------------------------------------
        # Purpose:  Called once to initialize the table with minimal default values.
        #           parameter 1: "self"   used to see some class variables.
        #           parameter 2: "parent" used to attach new frame to parent.
        # returns  New
        # ----------------------------------------------------------------

        enabledColumns = ['PID', 'CPU%', 'RAM%', 'User', 'Comm']  # Column Titles displayed at Top of Table.
        # pid,pcpu,pmem,user,comm

        procList = [  # Just initialize the array (first two columns) to bogus values, just for future debugging.
            [2, 50],  # These will be overwritten later.
            [1, 7],
            [0, 100],
            [3, 9.5],
            [4, 0],
            [5, 9999]
        ]

        plvFrame = ttk.Frame(parent)
        plvFrame.pack(fill='both', expand=True)

        plvTree = ttk.Treeview(plvFrame, columns=enabledColumns, show='headings')  # Display Column headings

        vsb = ttk.Scrollbar(plvFrame, orient='vertical', command='self.tree.yview')
        hsb = ttk.Scrollbar(plvFrame, orient='horizontal', command='self.tree.xview')

        plvTree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        plvTree.grid(column=0, row=0, sticky='nsew', in_=plvFrame)

        vsb.grid(column=1, row=0, sticky='ns', in_=plvFrame)
        hsb.grid(column=0, row=1, sticky='ew', in_=plvFrame)

        plvFrame.grid_columnconfigure(0, weight=1)
        plvFrame.grid_rowconfigure(0, weight=1)

        PIDLabel = tk.Label(plvFrame, text='PID to Graph:')
        PIDLabel.grid(row=4, column=0, sticky='e')
        self.PIDEntry = tk.Entry(plvFrame)
        self.PIDEntry.grid(row=4, column=1)

        # build tree
        for col in enabledColumns:
            plvTree.heading(col, text=col.title(),
                            command=lambda c=col: self.columnSort(plvTree, c, 0))
            # adjust the column's width to the header string
            plvTree.column(col,
                           width=tkFont.Font().measure(col.title()), anchor='e')

        for item in procList:  # 2dlist
            plvTree.insert('', 'end', values=item)
            # adjust column's width if necessary to fit each value
            for ix, val in enumerate(item):
                col_w = tkFont.Font().measure(val)
                if plvTree.column(enabledColumns[ix], width=None) < col_w:
                    plvTree.column(enabledColumns[ix], width=col_w)
        # end build tree#

        def eventClick(event):
            print('item click')
            #get focus/selected value
            val = plvTree.focus()
            print(val)#tree item id
            print('itemText',plvTree.item(val)['text'])

        plvTree.bind("<<TreeviewSelect>>", eventClick)


        # plvTree.insert('', 'end', text='button', tags=('ttk', 'simple'))
        # plvTree.tag_configure('ttk', background='yellow')
        # plvTree.tag_bind('ttk', '<1>', eventClick)  # the item clicked can be found via tree.focus()





        # plvFrame.after(self.updateIntervalMS, self.getProcIDs)  # ----> periodic update

        return plvTree, plvFrame  # new Tree,  new Frame that the new Tree is in.

        # frame - processes list view
        # plvFrame = tk.Frame(plvANDtgFrame)
        # dummyBut1= tk.Button(plvFrame, text='plvBut')
        # dummyBut1.pack()
        # reorganize columns click

    # -----------------------------------------------------------------------------
    def getProcIDs(self):
        # -----------------------------------------------------------------------------
        # Purpose:  This method is called periodically
        # -----------------------------------------------------------------------------

        # 'ps', '-Ao', 'user,uid,comm,pid,pcpu,tty', '--sort=-pcpu', '|', 'head', '-n', '6' #head causes issues

        if (self.boolTakeInData):  # for some reason this ins't getting the memo when pause is pressed.

            self.strPSatrFound = 'pid,comm,pcpu,pmem,user,uid'
            # 'pid,pcpu,pmem,uid'
            # 'comm,user'
            #  command: "ps -Ao pid,pcpu,pmem,user,comm  --sort=-pcpu"
            #                "ps    -Ao    pid,pcpu,pmem,user,comm,cmd    --sort=-pcpu"
            process = Popen(['ps', '-Ao', 'pid,pcpu,pmem,user,comm,cmd', '--sort=-pcpu'], stdout=PIPE, stderr=PIPE)
            stdout, _ = process.communicate()

            # print(stdout)
            print('time:', time.time())
            # print('gmtime',time.gmtime(time.time()), ', localtime:',time.localtime(time.time()))
            # columns of numbers are right aligned
            # columns of text are left aligned

            timestamp = time.time()

            # pidDict = {}
            print('---Contents of stdout follows----')
            i = -1
            self.pidList = []
            print('pidEntry-',self.PIDEntry.get())

            # go through returned list of lines, and select lines to process.
            for line in stdout.splitlines():
                i = i + 1
                if (i == 0):
                    continue  # ---> skip this line

                ##### print ('line(', i, ')', line)   ## Debug: line read in.
                type(line)

                decodeLine = line.decode('ascii', 'ignore')
                #                                  ^^^^^^
                #                                  ignore is used to not fail on unicode names (like web items from firefox)

                # print ('line(', i, ')', line)   ## Debug print: line read in.

                wordList = decodeLine.split()  # wordList has a list created from the items in the line

                commStrJoin = ''

                # FILTER out our own command.   Look at all the fields specifically field 7.  If it
                # has our own command which can be identified by our "pid,pcpu,pmem" then don't use it (skip it)
                if (len(wordList) > 8):
                    SeventhField = wordList[7]
                    # print("SeventhField:", SeventhField)   # Debug print
                    if ("pid,pcpu,pmem" in SeventhField):
                        print('************ Skip this line!!!! *****')
                        continue  # ------> skip this line (as it's our own command line)

                # Add the PID to our list (pidDict)
                if (len(wordList) > 5):
                    for aStr in wordList[4:]:
                        commStrJoin = commStrJoin + aStr
                else:
                    commStrJoin = wordList[4]
                    # if(i<10):
                    # print(wordList)
                floatList = wordList[0:4]
                floatList.append(commStrJoin)
                self.pidDict[str(wordList[0])] = floatList  # ((wordList[0:4]),(commStrJoin))
                # self.pidList.append(wordList[0:4]+[commStrJoin])

            # Redraw our GUI table.
            # delete current GUI contents
            self.plvTree.delete(*self.plvTree.get_children())
            # create a new GUI table
            for i in range(0, 8):
                pass
            for dictKey in self.pidDict.keys():
                # self.plvTree.delete('')
                listEntries = self.pidDict[dictKey]
                # listEntries = str(dictEntry).split()
                self.plvTree.insert('', 'end', iid=dictKey, text=dictKey, values=(listEntries))
                # self.pidDict[str(wordList[0])])

                result = self.plvTree.identify_row(i)
                childr = self.plvTree.get_children()
                # print('row i=',str(i))
                # print('plvTree children:',self.plvTree.get_children)



                # pidCo
                # for rowEntry in self.plvTree['PID']:
                #     pass


                # for all pids in pid column, update the other columns.
                # if column pid found in procList, update value. reset any highlights
                # remove pid from procList
                # if pid in column not found in current procList, highlight it
                # for all pids remaining in procList
                # insert value on column and highlight
            # for treeEntryPID in self.plvTree:
            #     pass

            # run column sort
            self.columnSort(self.plvTree)
            # if(self.desigCol is None):
            #     self.columnSort(self.plvTree, 'RAM%', 1)
            # else:
            #     self.columnSort(self.plvTree)



        else:
            print('not updating data')

        # print('bool is:'+str(self.boolTakeInData))
        self.after(self.updateIntervalMS, self.getProcIDs)  # -------> periodic update
        ###########

    # -----------------------------------------------------------------------------
    def make_timeGraphContents(self, parent):
        # -----------------------------------------------------------------------------
        # Purpose:  To take the passed in tree (1st parameter)
        # -----------------------------------------------------------------------------
        #  #frame - processes time graph
        cpuFrame = tk.Frame(parent)
        memFrame = tk.Frame(parent)
        idkFrame = tk.Frame(parent)

        cpuFrame.grid(row=2, column=2, sticky='nsew')
        memFrame.grid(row=4, column=2, sticky='nsew')
        idkFrame.grid(row=6, column=2, sticky='nsew')
        parent.grid_columnconfigure(2, weight=2)
        # parent.grid_rowconfigure(1, weight=1)#for test matplot
        parent.grid_rowconfigure(2, weight=2)
        parent.grid_rowconfigure(4, weight=2)
        parent.grid_rowconfigure(3, weight=1)
        parent.grid_rowconfigure(6, weight=2)

        # tk.Button(cpuFrame, text='cpu').pack(fill='both',expand=1,)
        # tk.Button(memFrame, text='mem').pack(fill='both',expand=1)
        # tk.Button(idkFrame, text='other').pack(fill='both',expand=1)


        tk.Button(parent, text='tgBut').grid(row=2, column=2, sticky='nsew', padx=5)
        tk.Button(parent, text='tgBut').grid(row=4, column=2, sticky='nsew', padx=5)
        tk.Button(parent, text='tgBut').grid(row=6, column=2, sticky='nsew', padx=5)

        tk.Label(parent, text='CPU', relief='sunken', borderwidth=2).grid(row=2, column=2,
                                                                          sticky='nw')  # Top of Frame:    "CPU"
        tk.Label(parent, text='MEM', relief='sunken', borderwidth=2).grid(row=4, column=2,
                                                                          sticky='nw')  # Bottom of Frame: "MEM"
        tk.Label(parent, text='OTHER', relief='sunken', borderwidth=2).grid(row=6, column=2,
                                                                            sticky='nw')  # Bottom of Frame: "OTHER"

        ####matplotlib###
        matplotFrame = tk.Frame(parent, relief='sunken', bg='blue')

        matplotFrame.grid(row=3, column=2, sticky='nsew')
        # aLabel = tk.Label(matplotFrame, text='matplot frame')
        # aLabel.grid(row=3, column=2)

        # fig,ax= plt.subplots()#3,sharex='col',sharey='row'
        fig = plt.figure(num=None, figsize=(4, 3), dpi=80)
        ax = fig.add_subplot(111)

        ax.set_title('axes 1 title')  # Title of Graph.  Centered.  Above Graph.
        ax.set_ylabel('% Consumption-Ylabel')  # Title of Left   (Y)
        ax.set_xlabel('Time(s)')  # Title of Bottom (X)
        # plt.setp([a.get_xticklabels() for a in ax])

        x = np.arange(0, 6.74, 0.01)  # X range.  (From (Starting At), To(ending at), By Increment size)
        # f = Figure(figsize=(5, 4), dpi=100)
        # ax = f.add_subplot(111)

        # Python Note:   X is ALWAYS the first item set.
        t = np.arange(0.0, 3.0, 0.01)  # First Item  (X)  Go from 0.0 to 3.0 by size 0.1
        s = np.sin(2 * np.pi * t)  # Second Item (Y)  What to plot

        ax.plot(t, s)  # Plot the X (t)  and Y (s) values

        # a tk.DrawingArea
        canvas = FigureCanvasTkAgg(fig, master=matplotFrame)
        canvas.show()
        canvas.get_tk_widget().pack(side='top', fill='both', expand=1)

        toolbar = NavigationToolbar2TkAgg(canvas, matplotFrame)
        toolbar.update()
        canvas._tkcanvas.pack(side='top', fill='both', expand=1)

        def on_key_event(event):
            print('you pressed %s' % event.key)
            key_press_handler(event, canvas, toolbar)

        canvas.mpl_connect('key_press_event', on_key_event)
        #######

        pass

    # -----------------------------------------------
    def toggleUpdate(self, aBool):
        # -----------------------------------------------
        # Toggle pause resume method
        # -----------------------------------------------
        self.boolTakeInData = aBool
        # print('Update Data is:'+str(aBool))

    # -----------------------------------------------
    def raiseFrame(self, frameRaised):
        # -----------------------------------------------
        # Bring proc or time graph to top
        # -----------------------------------------------
        frame = self.dictFrames[frameRaised]
        frame.tkraise()

    # -----------------------------------------------
    def printScreen(self):
        # -----------------------------------------------
        # save a screenshot of each window
        # save location is configurable in options window
        # -----------------------------------------------
        pass


# ----------------------- MAIN ---------------------------------------------------
##MAIN##
if __name__ == '__main__':
    # this runs if this is the first/start program in execution
    print(__name__)
    print('hey this is the main case')

    root = tk.Tk()  # no idea what sN or bN do.
    root.title('PySysMonitor')  # yep
    w = 1000  # was 600
    h = 700  # was 400
    x = 50  # was 100
    y = 50  # was 100


    root.geometry('%dx%d+%d+%d' % (w, h, x, y))
    def on_closing():
        root.destroy()
    root.protocol("WM_DELETE_WINDOW",on_closing)



    #     root.minsize(400, 300)#wont let user shrink below this
    # define all the window preferences
    mainWindow = PySysMonitor_gui(root)  # class made
    root.mainloop()
    print('program ending')

if __name__ != '__main__':
    # this runs if the .py file is called during a different classes execution
    print(__name__)
    print('hey this is the NOT main case')

print('end of file')

print('should always see this')


