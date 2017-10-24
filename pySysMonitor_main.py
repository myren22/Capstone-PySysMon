'''
Created on Oct 3, 2017

@author: KyleWin10
'''

#imports
import tkinter as tk
import tkinter.font as tkFont
import tkinter.ttk as ttk
import numpy as np
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
global pidDict
pidDict={}
pidList=[[7,7,7,7,7,7],[7,7,7,7,7,7]]#2d
dictFrames={}

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
        
        self.create_widgets()

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

        leftButFrame = tk.Frame(topBarFrame)
        leftButFrame.grid(row=1,column=1,sticky='w')#grid(row=0, column=0)
        procListBut = tk.Button(leftButFrame, text= 'Process List')
        procListBut.grid(row=1, column=0)
        procListBut['command'] = lambda name='procList': self.raiseFrame(name)#self.raiseFrame('procList')
        timeGraphBut = tk.Button(leftButFrame, text= 'Time Graph')
        timeGraphBut.grid(row=1, column=1)
        timeGraphBut['command'] = lambda name='timeGraph': self.raiseFrame(name)


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
        resumeBut['command'] = self.toggleUpdate(True)
        pauseBut = tk.Button(rightButFrame, text= 'Pause')
        pauseBut.grid(row=1, column=5)
        pauseBut['command']= self.toggleUpdate(False)


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

        ttk.Label(proclistFrame, text='Process List View').grid(row=0,column=2, sticky='nwe')


        procListTableFrame = tk.Frame(proclistFrame, relief='sunken', borderwidth=4)
        procListTableFrame.grid(row=2,column=2, sticky='nsew')


        self.make_procListViewFrame(procListTableFrame)
        dictFrames['procList']=proclistFrame


        timeGraphFrame = tk.Frame(plvANDtgFrame, relief='sunken', borderwidth=4)
        timeGraphFrame.grid(row=2, column=1, sticky='nsew')
        timeGraphTableFrame = tk.Frame(timeGraphFrame, relief='sunken', borderwidth=4)
        timeGraphFrame.grid_columnconfigure(2, weight=1)
        timeGraphFrame.grid_rowconfigure(2, weight=1)

        # aButton = tk.Button(timeGraphTableFrame, text='Open Time Graph-----------------------', borderwidth=3, relief='raised')
        # aButton.pack(fill='both', expand=1)
        ttk.Label(timeGraphFrame, text='Process Time Graph').grid(row=0, column=2, sticky='nwe')
        self.make_timeGraphContents(timeGraphTableFrame)
        timeGraphTableFrame.grid(row=2,column=2,sticky='nsew')

        dictFrames['timeGraph'] = timeGraphFrame

    def open_optionsWindow(self):
        optionsWindow = tk.Toplevel()
        optionsWindow.title('PySysMonitor - Options')  # yep
        w = 500
        h = 400
        x = 100
        y = 100
        optionsWindow.geometry('%dx%d+%d+%d' % (w, h, x, y))
        # options i may want to make to have changeable while running
            # print screenshot save location
            # frequency of process update
            # what columns are shown in process list view
            # length of time tracked
        #
        titleLabel=tk.Label(optionsWindow, text= 'Configuration Options')
        titleLabel.grid(row=1,column=1)
        updateLabel=tk.Label(optionsWindow, text='Update Frequency(ms)').grid(row=2,column=1)
        updateEntry = tk.Entry(optionsWindow).grid(row=2,column=2)

        tk.Label(optionsWindow, text='Print Save Dir.').grid(row=3, column=1)
        tk.Entry(optionsWindow).grid(row=3, column=2)

        tk.Label(optionsWindow, text='Length Time Tracked').grid(row=4, column=1)
        tk.Entry(optionsWindow).grid(row=4, column=2)

        tk.Label(optionsWindow, text='Columns Displayed').grid(row=5, column=1)
        #self.tree["displaycolumns"]=("artistCat", "artistDisplay") #just alter the headings listed
        tk.Entry(optionsWindow, text='make this a checkbox').grid(row=5, column=2)

        optionsWindow.grid_rowconfigure(1,minsize=50, weight=1)
        # optionsWindow.grid_rowconfigure(2, minsize=50, weight=1)
        optionsWindow.grid_columnconfigure(1, minsize=50, weight=1)
        optionsWindow.grid_columnconfigure(2, minsize=50, weight=1)


        #
        pass

    def open_singleProcProp(self):
        procPropWind = tk.Toplevel()
        procPropWind.title('PySysMonitor - Process Properties')  # yep
        w = 500
        h = 400
        x = 100
        y = 100
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

        procPropWind.grid_rowconfigure(1, minsize=50, weight=1)
        # optionsWindow.grid_rowconfigure(2, minsize=50, weight=1)
        procPropWind.grid_columnconfigure(1, minsize=50, weight=1)
        procPropWind.grid_columnconfigure(2, minsize=50, weight=1)
        pass
    
    def make_procListViewFrame(self, parent):
        enabledColumns = ['PID', 'CPU%', 'RAM%','TTY']
        procList = [
            ('2', '0.1','5','0'),
            ('25', '2','4','1'),
            ('41', '4','10','2'),
            ('35', '5','1','3'),
            ('281', '6','0','4'),
            ('555', '7','20','5'),
            ('11', '20','2','6'),
            ('68', '5.5','23','7'),
            ('91', '2.3','1','8')
        ]

        def columnSort(tree, col, descending):
            """sort tree contents when a column header is clicked on"""
            # grab values to sort
            data = [(tree.set(child, col), child) \
                    for child in tree.get_children('')]
            # if the data to be sorted is numeric change to float
            # data =  change_numeric(data)
            # now sort the data in place
            data.sort(reverse=descending)
            for ix, item in enumerate(data):
                tree.move(item[1], '', ix)
            # switch the heading so it will sort in the opposite direction
            tree.heading(col, command=lambda col=col: columnSort(tree, col, \
                                                             int(not descending)))




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
                              command=lambda c=col: columnSort(plvTree, c, 0))
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

        return plvTree

        # frame - processes list view
        #plvFrame = tk.Frame(plvANDtgFrame)
        #dummyBut1= tk.Button(plvFrame, text='plvBut')
        #dummyBut1.pack()
        # reorganize columns click

    def make_timeGraphContents(self, parent):
        #  #frame - processes time graph
        cpuFrame = tk.Frame(parent)
        memFrame = tk.Frame(parent)
        idkFrame = tk.Frame(parent)

        cpuFrame.grid(row=2,column=2,sticky='nsew')
        memFrame.grid(row=4, column=2,sticky='nsew')
        idkFrame.grid(row=6, column=2,sticky='nsew')
        parent.grid_columnconfigure(2, weight=1)
        parent.grid_rowconfigure(2, weight=1)
        parent.grid_rowconfigure(4, weight=1)
        parent.grid_rowconfigure(6, weight=1)

        # tk.Button(cpuFrame, text='cpu').pack(fill='both',expand=1,)
        # tk.Button(memFrame, text='mem').pack(fill='both',expand=1)
        # tk.Button(idkFrame, text='other').pack(fill='both',expand=1)


        tk.Button(parent, text='tgBut').grid(row=2, column=2,sticky='nsew',padx=5)
        tk.Button(parent, text='tgBut').grid(row=4, column=2,sticky='nsew',padx=5)
        tk.Button(parent, text='tgBut').grid(row=6, column=2,sticky='nsew',padx=5)

        tk.Label(parent, text='CPU',relief='sunken',borderwidth=2).grid(row=2, column=2, sticky='nw')
        tk.Label(parent, text='MEM',relief='sunken',borderwidth=2).grid(row=4, column=2, sticky='nw')
        tk.Label(parent, text='OTHER',relief='sunken',borderwidth=2).grid(row=6, column=2, sticky='nw')

        pass
    
    #toggle pause resume method
    def toggleUpdate(self, aBool):
        pass
    
    #bring proc or time graph to top
    def raiseFrame(self, frameRaised):
        frame = dictFrames[frameRaised]
        frame.tkraise()

    


    #save a screenshot of each window
    def printScreen(self):
        #save location is configurable in options window
        pass



def task():
    print('task update')
    root.after(2000, task)

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

    # intI=0
    # print('task update:' + str(intI))
    # print('--')
    #adding an update event to that runs every 2s
    def task():#careful adding params, may make program not wait correctly and recurse into itself and crash
        print('task update:')
        # aNum=aNum+1

        root.after(5000, task)#recursive call makes proc loop without blocking
        #ends up being executed during the mainloop along with other update events

    def getProcIDs():
        # 'ps' '-Ao' 'user,uid,comm,pid,pcpu,tty' '--sort=-pcpu' '|' 'head' '-n' '6'
        # 'ps', '-Ao', 'user,uid,comm,pid,pcpu,tty', '--sort=-pcpu', '|', 'head', '-n', '6'
        process = Popen(['ps', '-Ao', 'pid,comm,pcpu,pmem,user,uid', '--sort=-pcpu'], stdout=PIPE, stderr=PIPE)
        stdout, notused = process.communicate()
        print(stdout)
        # pidDict = {}
        for line in stdout.splitlines():
            wordList=line.split()
            print('hello')
            print(pidList)
            pidDict[wordList[0]]=wordList


            # strLine = line.decode('utf-8')
            # strLine = strLine.lstrip(' ')
            # user, uid, comm, pid, pcpu, tty = strLine.split(' ', 1)
            print('')
            # print('pid:' + pid + ', cmdline:' + comm)
            # pidDict[pid] = comm
        print('done')
        print('')
        ###########


    getProcIDs()
    root.after(5000, task)
    mainWindow = pySysMonitor_gui(root) #class made
    root.mainloop()
    print('program ending')
    
if __name__ != '__main__':
    #this runs if the .py file is called during a different classes execution
    print(__name__)
    print('hey this is the NOT main case')
    
print('end of file')
    
print('should always see this')
