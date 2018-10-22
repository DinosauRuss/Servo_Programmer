
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

import traceback

from servo_popups import Popup


class SettingsPopup(Popup):
    '''Generic popup with notebook to hold various settings pages'''
    
    def __init__(self, page):
        super().__init__(title='Settings')
        
        # To return data from tabs
        self.which_tab = ''
        self.values = ()
        
        self.notebook = ttk.Notebook(self, width=300, height=300)
        
        self.addTab(NamePage(self), 'Change Title')
        self.addTab(TimeAddPage(self), 'Add Time')
        self.addTab(TimeDelPage(self), 'Remove Time')
        self.addTab(LimitPage(page.plot.upper_limit,
                              page.plot.lower_limit,
                              self), 'Adjust Limits')
        self.addTab(ServoDeletePage(page.parent.num_of_servos.get(),
                                    self), 'Delete Tab')
        
        self.buildPage()
    
    def buildPage(self):
        self.notebook.pack(anchor=tk.CENTER, fill=tk.BOTH)
        
    def addTab(self, page, txt='Tab'):    
        self.notebook.add(page, text=txt)
    
    def show(self):
        self.wait_window()
        return ( self.which_tab, self.values )
    

class NamePage(ttk.Frame):
    '''Change the name/title of plot and tab'''
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self.parent = parent
        self.buildPage()
        
    def buildPage(self):
        self.name_var = tk.StringVar()
        
        main_frame = ttk.Frame(self)
        
        title = ttk.Label(main_frame, text='Enter New Name',
            font=(None, 14))
           
        self.name_entry = ttk.Entry(main_frame, textvariable=self.name_var)
        self.name_entry.focus()
        self.name_entry.bind('<Return>', self.update)
        
        button_frame = ttk.Frame(main_frame)
        
        ok_button = ttk.Button(button_frame, text='Ok',width=5, 
            command=self.update)
        cancel_button = ttk.Button(button_frame, text='Cancel', width=5,
            command=self.parent.destroy)
        
        main_frame.pack(side=tk.TOP, pady=20)
        title.pack()
        self.name_entry.pack(pady=15)
        button_frame.pack()
        ok_button.pack(side=tk.LEFT, padx=3)
        cancel_button.pack(side=tk.RIGHT, padx=3)
        
    def update(self, event=None):
        '''Make changes and close popup'''
        
        # Remove spaces and limit length of name
        name = str(self.name_var.get()).replace(' ', '')
        name = name[:10]
        
        if name:
            # Send data to parent so it can be returned
            self.parent.which_tab = self.__class__.__name__
            self.parent.values = name
            
            self.parent.destroy()    
            
        else:
            self.parent.destroy()
            

class LimitPage(ttk.Frame):
    '''Change value of individual node'''
    
    def __init__(self, upper_val, lower_val, parent):
        super().__init__(parent)
        
        self.parent = parent
        
        self.upper = upper_val
        self.lower = lower_val
        
        self.buildPage()
        
    def buildPage(self):
        self.upper_var = tk.IntVar()
        self.lower_var = tk.IntVar()
        self.upper_var.set(self.upper)
        self.lower_var.set(self.lower)
        
        main_frame = ttk.Frame(self, padding=5)
        
        title = ttk.Label(main_frame, text='Enter New Limits', font=(None, 12))
        
        upper_label = ttk.Label(main_frame, text='Upper:')
        self.upper_entry = ttk.Entry(main_frame,
            textvariable = self.upper_var,
            width=6)
        self.upper_entry.focus()
        
        lower_label = ttk.Label(main_frame, text='Lower:')
        self.lower_entry = ttk.Entry(main_frame,
            textvariable=self.lower_var,
            width=6)
     
        button = ttk.Button(main_frame, text='OK', command=self.update)
    
    
        main_frame.pack(side=tk.TOP, pady=20)
        title.grid(columnspan=2, padx=5, pady=5)
        
        upper_label.grid(row=1, column=0, sticky=tk.W)
        lower_label.grid(row=1, column=1, sticky=tk.E)
        
        self.upper_entry.grid(row=2, column=0,pady=5, sticky=tk.W)
        self.lower_entry.grid(row=2, column=1, sticky=tk.E)
        button.grid(columnspan=2, pady=5)
            
    def update(self, event=None):
        limit = lambda n, n_min, n_max: max(min(n, n_max), n_min)
        
        try:
            # Prevent limits from going out of servo range,
            # and from overlapping each other
            upper_limit = int(self.upper_var.get())
            upper_limit = limit(upper_limit, 5, 180)
            
            lower_limit = int(self.lower_var.get())
            lower_limit = limit(lower_limit, 0, self.upper-5)
            
            # Send data to parent so it can be returned
            self.parent.which_tab = self.__class__.__name__
            self.parent.values = (upper_limit, lower_limit)
            
        except Exception as e:
            print('VALUE ERROR: ', e)
            print(traceback.format_exc())
        
        finally:
            self.parent.destroy()
            
 
class TimeAddPage(ttk.Frame):
     
    def __init__(self, parent):
        super().__init__(parent)
         
        self.parent = parent
        
        self.buildPage()
       
    def buildPage(self):
        
        self.time_entry_var = tk.IntVar()
        self.where_var = tk.StringVar()
        
        main_frame = ttk.Frame(self, padding=5)
        
        title = ttk.Label(main_frame, text='Add Time To All Plots',
            font=(None, 14))
        
        entry_frame = ttk.Frame(main_frame)
        time_label = ttk.Label(entry_frame, text='Seconds   ')
        time_entry = ttk.Entry(entry_frame, width=5,
            textvariable=self.time_entry_var)
        
        where = ttk.Frame(main_frame)
        begin = ttk.Radiobutton(where, text = 'Beginning', value='begin',
            variable=self.where_var)
        end = ttk.Radiobutton(where, text= 'End', value='end',
            variable=self.where_var)
        
        button_frame = ttk.Frame(main_frame)
        ok_button = ttk.Button(button_frame, text='OK',
            command=self.update)
        cancel_button = ttk.Button(button_frame, text='Cancel',
            command=self.parent.destroy)
        
        main_frame.pack(side=tk.TOP, pady = 20)
        title.grid()
        
        entry_frame.grid(pady=10)
        time_label.pack(side=tk.LEFT)
        time_entry.pack(side=tk.LEFT)
        
        where.grid(pady=10)
        begin.grid(sticky=tk.W)
        end.grid(sticky=tk.W)
        
        button_frame.grid(pady=10)
        ok_button.pack(side=tk.LEFT, padx=5)
        cancel_button.pack(side=tk.RIGHT, padx=5)
        
    def update(self):
        try:
            seconds = self.time_entry_var.get()
        except Exception as e:
            print(e)
            messagebox.showerror('Error', 'Enter digits only')
            self.parent.destroy()
            return
        
        self.parent.which_tab = self.__class__.__name__
        self.parent.values = (self.where_var.get(), self.time_entry_var.get())
            
        self.parent.destroy()
        
        
class TimeDelPage(ttk.Frame):
     
    def __init__(self, parent):
        super().__init__(parent)
         
        self.parent = parent
        
        self.buildPage()
       
    def buildPage(self):
        
        self.time_entry_var = tk.IntVar()
        self.where_var = tk.StringVar()
        
        main_frame = ttk.Frame(self, padding=5)
        
        title = ttk.Label(main_frame, text='Delete Time From All Plots',
            font=(None, 14))
        
        entry_frame = ttk.Frame(main_frame)
        time_label = ttk.Label(entry_frame, text='Seconds   ')
        time_entry = ttk.Entry(entry_frame, width=5,
            textvariable=self.time_entry_var)
        
        where = ttk.Frame(main_frame)
        begin = ttk.Radiobutton(where, text = 'Beginning', value='begin',
            variable=self.where_var)
        end = ttk.Radiobutton(where, text= 'End', value='end',
            variable=self.where_var)
        
        button_frame = ttk.Frame(main_frame)
        ok_button = ttk.Button(button_frame, text='OK',
            command=self.update)
        cancel_button = ttk.Button(button_frame, text='Cancel',
            command=self.parent.destroy)
        
        main_frame.pack(side=tk.TOP, pady = 20)
        title.grid()
        
        entry_frame.grid(pady=10)
        time_label.pack(side=tk.LEFT)
        time_entry.pack(side=tk.LEFT)
        
        where.grid(pady=10)
        begin.grid(sticky=tk.W)
        end.grid(sticky=tk.W)
        
        button_frame.grid(pady=10)
        ok_button.pack(side=tk.LEFT, padx=5)
        cancel_button.pack(side=tk.RIGHT, padx=5)
        
    def update(self):
        try:
            seconds = self.time_entry_var.get()
        except Exception as e:
            print(e)
            messagebox.showerror('Error', 'Enter digits only')
            self.parent.destroy()
            return
        
        self.parent.which_tab = self.__class__.__name__
        self.parent.values = ( self.where_var.get(), self.time_entry_var.get() )
            
        self.parent.destroy()
        

class ServoDeletePage(ttk.Frame):
    
    def __init__(self, num_servos, parent):
        super().__init__(parent)
        
        self.num_servos = num_servos
        self.parent = parent
        
        self.buildPage()
    
    def buildPage(self):
        main_frame = ttk.Frame(self)
        button_frame = ttk.Frame(main_frame)
        
        title = ttk.Label(main_frame, text='Delete Tab?', font=(None, 14))
        del_button = ttk.Button(button_frame, text='Delete',
            command=self.update)
        cancel_button = ttk.Button(button_frame, text='Cancel',
            command=self.parent.destroy)
    
        title.pack()
        button_frame.pack(pady=10)
        del_button.grid(row=0, column=0, padx=5)
        cancel_button.grid(row=0, column=1, padx=5)
        
        main_frame.pack(side=tk.TOP, pady=20)
    
    def update(self):
        if self.num_servos > 1:
            if messagebox.askokcancel('Delete Tab?',
                'Are you sure you want to delet this tab?'):
                
                self.parent.which_tab = self.__class__.__name__
                
                self.parent.destroy()
            else:
                self.parent.destroy()
                
        else:
            self.parent.destroy()
            
                

        
    



