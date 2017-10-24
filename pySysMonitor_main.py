'''
Created on Oct 3, 2017

@author: KyleWin10
'''

#imports
import tkinter as tk
import subprocess
import sys
from tkinter.constants import ANCHOR
#---#

print('start')

class pySysMonitor_gui(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)#embeds this frame class in a parent
        self['relief']='raised'
        self['borderwidth']=4
        self.pack(fill='both')#now it will be visible
        
        #setup window setting
        #name, size, exit button, 
        
        self.create_widgets()

    def create_widgets(self):
        #top bar
        topBarFrame = tk.Frame(self, relief='raised', borderwidth=8)
        topBarFrame.grid(row=1, sticky='nsew')
#         topBarFrame.pack(side='bottom', anchor='n', fill='x')
        leftButFrame = tk.Frame(topBarFrame)
        leftButFrame.pack(side='left', fill='x')#grid(row=0, column=0)
        procListBut = tk.Button(leftButFrame, text= 'Process List')
        procListBut.grid(row=0, column=0)
        timeGraphBut = tk.Button(leftButFrame, text= 'Time Graph')
        timeGraphBut.grid(row=0, column=1)
        
        
        
        rightButFrame = tk.Frame(topBarFrame)
        rightButFrame.pack(side='right')#grid(row=0, column=2)
        
        printBut = tk.Button(topBarFrame, text= 'Print')
        printBut.pack(side='right', padx=20)#.grid(row=0, column=1)
        
        
        resumeBut = tk.Button(rightButFrame, text= 'Resume')
        resumeBut.grid(row=0, column=3)
        pauseBut = tk.Button(rightButFrame, text= 'Pause')
        pauseBut.grid(row=0, column=4)
        
        
        frame2 = tk.Frame(self, relief='sunken', borderwidth=4)
        frame2.grid(row=2,stick='nsew')#pack(side='left', )
#         but1= tk.Button(frame2, text='Process List View Frame', relief='sunken', width=50, height=20)
#         but1.pack(side='bottom')
        
        aLabel = tk.Label(frame2, text='Process List', borderwidth=3)
        aLabel.grid(row=0, columnspan=2, pady=3)
        for i in range(1,12):
            for g in range(0,7):
                if i==1:
                    aLabel = tk.Label(frame2, text='Column '+str(g), borderwidth=3, relief='raised')
                    aLabel.grid(row=i, column=g)
                else:
                    aLabel = tk.Label(frame2, text='i='+str(i)+', g='+str(g), borderwidth=3, relief='sunken')
                    aLabel.grid(row=i, column=g)


        aButton = tk.Button(frame2, text='Open Process Properties', borderwidth=3, relief='raised')
        aButton.grid(row=13, columnspan=3, pady=5)

        # def task():  #update loop
        #     #  careful adding params, may make program not wait correctly and recurse into itself and crash
        #     print('button task update:(2s)')
        #     # aNum=aNum+1 # this caused an issue when a param
        #     aButton.after(2000, task)  # recursive call makes proc loop without blocking
        #     # ends up being executed during the mainloop along with other update events
        #
        # aButton.after(2000, task)#begins the infinite updates
        
        
#         text1 = tk.Label(frame2, text='text1', relief='sunken')
#         text1.pack(side='bottom', fill='both')
        
#         text2 = tk.Label(self, text='hola', relief='raised', borderwidth=4)
#         text2.grid(sticky='s' )
        
#         #frame - holds plv and tg
#         plvANDtgFrame = tk.Frame(self)
#         plvANDtgFrame.pack(anchor='n', fill='both')
#         
#         
#         #frame - processes list view
#         plvFrame = tk.Frame(plvANDtgFrame)
#         dummyBut1= tk.Button(plvFrame, text='plvBut')
#         dummyBut1.pack()
#         
#         #frame - processes time graph
#         tgFrame = tk.Frame(plvANDtgFrame)
#         dummyBut2= tk.Button(tgFrame, text='tgBut')
#         dummyBut2.pack(fill='both')
        
#         self.hi_there = tk.Button(self)
#         self.hi_there["text"] = "Hello World\n(click me)"
#         self.hi_there["command"] = self.say_hi
#         self.hi_there.pack()
# 
#         self.quit = tk.Button(self, text="QUIT", fg="red",
#                               command=root.destroy)
#         self.quit.pack(side="bottom")

    def say_hi(self):
        print("hi there, everyone!")
        print('test button cmd, it worked!')
        
    def open_singleProcProp(self):

        pass
    
    def make_timeGraphContents(self):
        pass
    
    #toggle pause resume method
    def toggleUpdate(self):
        pass
    
    #bring proc or time graph to top
    def raiseFrame(self):
        pass
    
    #reorganize columns click
    def columnClickReorganize(self):
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
    w=500
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

    root.after(5000, task)
    mainWindow = pySysMonitor_gui(master=root) #class made
    mainWindow.mainloop()
    print('program ending')
    
if __name__ != '__main__':
    #this runs if the .py file is called during a different classes execution
    print(__name__)
    print('hey this is the NOT main case')
    
print('end of file')
    
print('should always see this')
