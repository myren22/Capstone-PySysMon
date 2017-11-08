'''
Created on Oct 3, 2017

@author: KyleWin10
'''

#imports
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
#---#

print('start')

timeList=np.arange(0,99)
timeDict={}
for i in range(0,99):
    timeDict[i]={}
    timeDict[i]['curTime']='' #int or string?
    #timeDict[i][somePIDnum]={}

# boolTakeInData=True

pidDict={}
# pidList=[[7,7,7,7,7,7],[7,7,7,7,7,7]]#2d
# dictFrames={}

#time->pid->process traits
timeTick=0


class pySysMonitor_gui(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)#embeds this frame class in a parent

        self['relief']='raised'
        self['borderwidth']=4
        self.pack(fill='both', expand=1)#now it will be visible

        #setup window setting
        #name, size, exit button,

        #init class variables
        self.timeTick=0
        self.dictFrames={}
        self.pidDict={}
        self.boolTakeInData=True
        self.updateIntervalMS= 1000
        self.timeTrackDurat=60
        self.printSaveDir=r'/home/kyle/Software Downloads/Capstone/Screenshots'
        self.strPSatrFound=None
        self.desigCol='CPU%'
        self.desigDescend=1
        self.plvTree=None

        #run create gui methods
        self.create_widgets() #


    def create_widgets(self):
        pass
        #top bar
        self.grid_rowconfigure(2, weight=12)
        self.grid_columnconfigure(1, weight=1)

        topBarFrame = tk.Frame(self, relief='sunken', borderwidth=5, bg='teal')
        topBarFrame.grid(row=1,column=1, sticky='new')

        # aButtonBox.pack(side='top',fill='both', expand=1)

        topBarFrame.grid_columnconfigure(1,minsize=40, weight=1)
        # topBarFrame.grid_columnconfigure(2, minsize=80, weight=10)
        topBarFrame.grid_columnconfigure(3, minsize=80, weight=1)

        #left button frame and its contents
        leftButFrame = tk.Frame(topBarFrame)
        leftButFrame.grid(row=1,column=1,sticky='w')#grid(row=0, column=0)
        procListBut = tk.Button(leftButFrame, text= 'Process List')
        procListBut.grid(row=1, column=0)
        procListBut['command'] = lambda name='procList': self.raiseFrame(name)#self.raiseFrame('procList')
        timeGraphBut = tk.Button(leftButFrame, text= 'Time Graph')
        timeGraphBut.grid(row=1, column=1)
        timeGraphBut['command'] = lambda name='timeGraph': self.raiseFrame(name)

        #right button frame, and its contents
        rightButFrame = tk.Frame(topBarFrame)
        procPropBut = tk.Button(rightButFrame, text='Proc. Prop')  # ,padx=0.5,pady=0.5
        procPropBut.grid(row=1, column=1)
        procPropBut['command'] = self.open_singleProcProp
        optionsBut = tk.Button(rightButFrame, text='Options')#,padx=0.5,pady=0.5
        optionsBut.grid(row=1, column=2)
        optionsBut['command'] = self.open_optionsWindow #openOptionsWindow()
        rightButFrame.grid(row=1, column=3, sticky='e')
        printBut = tk.Button(rightButFrame, text='Print')
        printBut.grid(row=1, column=3)  # .grid(row=0, column=1)
        printBut['command'] = self.printScreen()
        resumeBut = tk.Button(rightButFrame, text= 'Resume')
        resumeBut.grid(row=1, column=4)
        resumeBut['command'] = lambda aBool=True: self.toggleUpdate(aBool)
        pauseBut = tk.Button(rightButFrame, text= 'Pause')
        pauseBut.grid(row=1, column=5)
        pauseBut['command']=  lambda aBool=False: self.toggleUpdate(aBool)

        ###begin everything in multi frame###
        plvANDtgFrame = tk.Frame(self)
        plvANDtgFrame.grid(row=2, column=1, sticky='nsew')

        # self.grid_columnconfigure(1, weight=1)
        # self.grid_rowconfigure(2, weight=1)
        plvANDtgFrame.grid_columnconfigure(1, weight=1)
        plvANDtgFrame.grid_rowconfigure(2, weight=1)

        proclistFrame = tk.Frame(plvANDtgFrame, relief='sunken', borderwidth=4, width=450)
        proclistFrame.grid(row=2, column=1, sticky='nsew')  # pack(side='left', )
        proclistFrame.grid_columnconfigure(2, weight=1)
        proclistFrame.grid_rowconfigure(2, weight=1)
        self.dictFrames['procList'] = proclistFrame

        ttk.Label(proclistFrame, text='Process List View').grid(row=0,column=2, sticky='nwe')

        procListTableFrame = tk.Frame(proclistFrame, relief='sunken', borderwidth=4)
        procListTableFrame.grid(row=2,column=2, sticky='nsew')
        self.plvTree, _=  self.make_procListViewFrame(procListTableFrame)
        #update tree. timer and check


        timeGraphFrame = tk.Frame(plvANDtgFrame, relief='sunken', borderwidth=4)
        timeGraphFrame.grid(row=2, column=1, sticky='nsew')
        timeGraphFrame.grid_columnconfigure(2, weight=1)
        timeGraphFrame.grid_rowconfigure(2, weight=1)
        self.dictFrames['timeGraph'] = timeGraphFrame

        ttk.Label(timeGraphFrame, text='Process Time Graph').grid(row=0, column=2, sticky='nwe')
        timeGraphTableFrame = tk.Frame(timeGraphFrame, relief='sunken', borderwidth=4)
        self.make_timeGraphContents(timeGraphTableFrame)
        timeGraphTableFrame.grid(row=2,column=2,sticky='nsew')

        print('1')
        plvANDtgFrame.after(self.updateIntervalMS, self.getProcIDs)

        ###end everythin in multiframe###

    def open_optionsWindow(self):
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
        titleLabel=tk.Label(optionsWindow, text= 'Configuration Options')
        titleLabel.grid(row=1,column=1, sticky='n')
        updateLabel=tk.Label(optionsWindow, text='Update Frequency(ms)')
        updateLabel.grid(row=2,column=1)
        updateEntry = tk.Entry(optionsWindow)
        updateEntry.grid(row=2,column=2)

        tk.Label(optionsWindow, text='Print Save Dir.').grid(row=3, column=1)
        printSaveDirEntry = tk.Entry(optionsWindow)
        printSaveDirEntry.grid(row=3, column=2)

        tk.Label(optionsWindow, text='Length Time Tracked(s)').grid(row=4, column=1)
        timeTrackEntry = tk.Entry(optionsWindow)
        timeTrackEntry.grid(row=4, column=2)

        tk.Label(optionsWindow, text='Columns Displayed').grid(row=5, column=1)
        #self.tree["displaycolumns"]=("artistCat", "artistDisplay") #just alter the headings listed
        pidCheckBut = tk.Checkbutton(optionsWindow, text='PID').grid(row=5, column=2)
        pcpuCheckBut = tk.Checkbutton(optionsWindow, text='pcpu').grid(row=5, column=3)
        pramCheckBut = tk.Checkbutton(optionsWindow, text='pram').grid(row=5, column=4)

        optionsWindow.grid_rowconfigure(1,minsize=50, weight=1)
        # optionsWindow.grid_rowconfigure(2, minsize=50, weight=1)
        optionsWindow.grid_columnconfigure(1, minsize=50, weight=1)
        optionsWindow.grid_columnconfigure(2, minsize=50, weight=1)

        #Accept, Cancel, Default
        def applyOptions():

            self.updateIntervalMS=int(updateEntry.get())
            self.timeTrackDurat= int(timeTrackEntry.get())
            self.printSaveDir = printSaveDirEntry.get()

        def restoreDefaults():
            updateEntry.delete(0,END)
            updateEntry.insert(END, str(self.updateIntervalMS))
            printSaveDirEntry.delete(0,END)
            printSaveDirEntry.insert(END, self.printSaveDir)
            timeTrackEntry.delete(0,END)
            timeTrackEntry.insert(END, self.timeTrackDurat)
        restoreDefaults()

        botButFrame = tk.Frame(optionsWindow)
        botButFrame.grid(row=6,column=2)
        acceptBut = tk.Button(botButFrame,text='Accept',command=applyOptions)
        acceptBut.grid(row=1, column=2)
        cancelBut = tk.Button(botButFrame,text='Cancel', command= lambda:optionsWindow.destroy())
        cancelBut.grid(row=1, column=3)
        defaultsBut = tk.Button(botButFrame,text='Defaults', command=restoreDefaults)
        defaultsBut.grid(row=1, column=4)
        # acceptBut['command'] = lambda aBool=False: self.toggleUpdate(aBool)

        #
        pass

    def open_singleProcProp(self):
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

        cancelBut = tk.Button(procPropWind, text='Cancel', command=lambda: procPropWind.destroy())
        cancelBut.grid(row=6, column=2)

        procPropWind.grid_rowconfigure(1, minsize=50, weight=1)
        # optionsWindow.grid_rowconfigure(2, minsize=50, weight=1)
        procPropWind.grid_columnconfigure(1, minsize=50, weight=1)
        procPropWind.grid_columnconfigure(2, minsize=50, weight=1)


        pass

    def columnSort(self,  *posArgs): #tree, col, descending,
        tree,col,descending=None,None,None
        if(len(posArgs) ==3):
            self.desigCol=posArgs[1]
            self.desigDescend = posArgs[2]

        tree=posArgs[0]
        col=self.desigCol
        descending=self.desigDescend

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
        floatsOnlyCols='CPU% RAM% PID'
        if col in floatsOnlyCols:
            for i in data:
                i[0] = float(i[0])

        data.sort(reverse=descending)

        for ix, item in enumerate(data):
            tree.move(item[1], '', ix)
        # switch the heading so it will sort in the opposite direction
        tree.heading(col, command=lambda col=col: self.columnSort(tree, col, int(not descending)))

    def make_procListViewFrame(self, parent):
        enabledColumns = ['PID', 'CPU%', 'RAM%','User','Comm']
        #pid,pcpu,pmem,user,comm

        procList=[
            [2,50],
            [1,7],
            [0,100],
            [3,9.5],
            [4,0],
            [5,9999]
        ]

        plvFrame = ttk.Frame(parent)
        plvFrame.pack(fill='both', expand=True)

        plvTree = ttk.Treeview(plvFrame, columns=enabledColumns, show='headings')

        vsb = ttk.Scrollbar(plvFrame, orient='vertical',command='self.tree.yview')
        hsb = ttk.Scrollbar(plvFrame, orient='horizontal',command='self.tree.xview')

        plvTree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        plvTree.grid(column=0, row=0, sticky='nsew', in_=plvFrame)

        vsb.grid(column=1, row=0, sticky='ns', in_=plvFrame)
        hsb.grid(column=0, row=1, sticky='ew', in_=plvFrame)

        plvFrame.grid_columnconfigure(0, weight=1)
        plvFrame.grid_rowconfigure(0, weight=1)


        #build tree
        for col in enabledColumns:
            plvTree.heading(col, text=col.title(),
                              command=lambda c=col: self.columnSort(plvTree, c, 0))
            # adjust the column's width to the header string
            plvTree.column(col,
                             width=tkFont.Font().measure(col.title()), anchor='e')

        for item in procList:   #2dlist
            plvTree.insert('', 'end', values=item)
            # adjust column's width if necessary to fit each value
            for ix, val in enumerate(item):
                col_w = tkFont.Font().measure(val)
                if plvTree.column(enabledColumns[ix], width=None) < col_w:
                    plvTree.column(enabledColumns[ix], width=col_w)
        #end build tree#

        plvFrame.after(self.updateIntervalMS, self.getProcIDs)


        return plvTree, plvFrame

        # frame - processes list view
        #plvFrame = tk.Frame(plvANDtgFrame)
        #dummyBut1= tk.Button(plvFrame, text='plvBut')
        #dummyBut1.pack()
        # reorganize columns click

    def getProcIDs(self):
        # 'ps', '-Ao', 'user,uid,comm,pid,pcpu,tty', '--sort=-pcpu', '|', 'head', '-n', '6' #head causes issues

        if(self.boolTakeInData): #for some reason this ins't getting the memo when pause is pressed.
            self.strPSatrFound='pid,comm,pcpu,pmem,user,uid'
            #'pid,pcpu,pmem,uid'
            #'comm,user'
            process = Popen(['ps', '-Ao', 'pid,pcpu,pmem,user,comm', '--sort=-pcpu'], stdout=PIPE, stderr=PIPE)
            stdout,_= process.communicate()
            # print(stdout)
            print('time:', time.time())
            # print('gmtime',time.gmtime(time.time()), ', localtime:',time.localtime(time.time()))
            # columns of numbers are right aligned
            # columns of text are left aligned

            # pidDict = {}
            print('---Contents of stdout follows----')
            i=-1
            self.pidList=[]
            for line in stdout.splitlines():
                i = i + 1
                if (i == 0):
                    continue
                decodeLine = line.decode('ascii')
                wordList=decodeLine.split()
                commStrJoin=''
                if(len(wordList)>5):
                    for aStr in wordList[4:]:
                        commStrJoin=commStrJoin+aStr
                else:
                    commStrJoin=wordList[4]
                # if(i<10):
                    # print(wordList)
                floatList=wordList[0:4]
                floatList.append(commStrJoin)
                self.pidDict[str(wordList[0])]=floatList  #((wordList[0:4]),(commStrJoin))
                    # self.pidList.append(wordList[0:4]+[commStrJoin])


            # print('----done parse to dict----')
            # print('Dict contents:')
            # print(self.pidDict)
            # print('pidList: ',self.pidList)


            #rewrite plvTree
            #save previous tree?
            #delete current contents
            self.plvTree.delete(*self.plvTree.get_children())

            for i in range(0,8):
                pass
            for dictKey in self.pidDict.keys():
                # self.plvTree.delete('')
                listEntries = self.pidDict[dictKey]
                # listEntries = str(dictEntry).split()
                self.plvTree.insert('','end',iid=dictKey, text=dictKey,values=(listEntries))
                # self.pidDict[str(wordList[0])])

                result = self.plvTree.identify_row(i)
                childr = self.plvTree.get_children()
                # print('row i=',str(i))
            # print('plvTree children:',self.plvTree.get_children)



            # pidCo
            # for rowEntry in self.plvTree['PID']:
            #     pass


            #for all pids in pid column, update the other columns.
                #if column pid found in procList, update value. reset any highlights
                    #remove pid from procList
                #if pid in column not found in current procList, highlight it
            #for all pids remaining in procList
                #insert value on column and highlight
            # for treeEntryPID in self.plvTree:
            #     pass

            #run column sort
            self.columnSort(self.plvTree)
            # if(self.desigCol is None):
            #     self.columnSort(self.plvTree, 'RAM%', 1)
            # else:
            #     self.columnSort(self.plvTree)



        else:
            print('not updating data')

        # print('bool is:'+str(self.boolTakeInData))
        self.after(self.updateIntervalMS, self.getProcIDs)
        ###########




    def make_timeGraphContents(self, parent):
        #  #frame - processes time graph
        cpuFrame = tk.Frame(parent)
        memFrame = tk.Frame(parent)
        idkFrame = tk.Frame(parent)

        cpuFrame.grid(row=2,column=2,sticky='nsew')
        memFrame.grid(row=4, column=2,sticky='nsew')
        idkFrame.grid(row=6, column=2,sticky='nsew')
        parent.grid_columnconfigure(2, weight=2)
        # parent.grid_rowconfigure(1, weight=1)#for test matplot
        parent.grid_rowconfigure(2, weight=2)
        parent.grid_rowconfigure(4, weight=2)
        parent.grid_rowconfigure(3, weight=1)
        parent.grid_rowconfigure(6, weight=2)

        # tk.Button(cpuFrame, text='cpu').pack(fill='both',expand=1,)
        # tk.Button(memFrame, text='mem').pack(fill='both',expand=1)
        # tk.Button(idkFrame, text='other').pack(fill='both',expand=1)


        tk.Button(parent, text='tgBut').grid(row=2, column=2,sticky='nsew',padx=5)
        tk.Button(parent, text='tgBut').grid(row=4, column=2,sticky='nsew',padx=5)
        tk.Button(parent, text='tgBut').grid(row=6, column=2,sticky='nsew',padx=5)

        tk.Label(parent, text='CPU',relief='sunken',borderwidth=2).grid(row=2, column=2, sticky='nw')
        tk.Label(parent, text='MEM',relief='sunken',borderwidth=2).grid(row=4, column=2, sticky='nw')
        tk.Label(parent, text='OTHER',relief='sunken',borderwidth=2).grid(row=6, column=2, sticky='nw')


        ####matplotlib###
        matplotFrame = tk.Frame(parent, relief='sunken',bg='blue')

        matplotFrame.grid(row=3, column=2, sticky='nsew')
        # aLabel = tk.Label(matplotFrame, text='matplot frame')
        # aLabel.grid(row=3, column=2)

        # fig,ax= plt.subplots()#3,sharex='col',sharey='row'
        fig = plt.figure(num=None, figsize=(4,3), dpi=80)
        ax = fig.add_subplot(111)

        ax.set_title('axes 1 title')
        ax.set_ylabel('% Consumption-Ylabel')
        ax.set_xlabel('Time(s)')
        # plt.setp([a.get_xticklabels() for a in ax])

        x=np.arange(0,6.74,0.01)
        # f = Figure(figsize=(5, 4), dpi=100)
        # ax = f.add_subplot(111)
        t = np.arange(0.0, 3.0, 0.01)
        s = np.sin(2 * np.pi * t)



        ax.plot(t, s)

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
    
    #toggle pause resume method
    def toggleUpdate(self, aBool):
        self.boolTakeInData = aBool
        # print('Update Data is:'+str(aBool))
    
    #bring proc or time graph to top
    def raiseFrame(self, frameRaised):
        frame = self.dictFrames[frameRaised]
        frame.tkraise()

    #save a screenshot of each window
    def printScreen(self):
        #save location is configurable in options window
        pass





##MAIN##
if __name__ == '__main__':
    #this runs if this is the first/start program in execution
    print(__name__)
    print('hey this is the main case')
    
    root = tk.Tk()#no idea what sN or bN do.
    root.title('PySysMonitor')#yep
    w=600
    h=400
    x=100
    y=100
    root.geometry('%dx%d+%d+%d' % (w, h, x, y))
#     root.minsize(400, 300)#wont let user shrink below this
    #define all the window preferences
    mainWindow = pySysMonitor_gui(root) #class made
    root.mainloop()
    print('program ending')
    
if __name__ != '__main__':
    #this runs if the .py file is called during a different classes execution
    print(__name__)
    print('hey this is the NOT main case')
    
print('end of file')
    
print('should always see this')


# strLine = line.decode('utf-8')
# strLine = strLine.lstrip(' ')
# user, uid, comm, pid, pcpu, tty = strLine.split(' ', 1)
# print('pid:' + pid + ', cmdline:' + comm)
# pidDict[pid] = comm
