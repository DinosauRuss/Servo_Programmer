
import tkinter as tk

from tkinter import messagebox
from tkinter import ttk

from servo_popups import Popup


class SettingsPopup(Popup):
    
    def __init__(self):
        super().__init__(title='Settings')
        
        self.notebook = ttk.Notebook(self, width=300, height=300)
        
        self.buildPage()
    
    def buildPage(self):
        self.notebook.pack(anchor=tk.CENTER, fill=tk.BOTH)
        
    def addTab(self, page, txt='cheese'):    
        self.notebook.add(page, text=txt)
    

class NamePage(ttk.Frame):
    '''Change the name/title of plot and tab'''
    
    def __init__(self, page, parent):
        super().__init__(parent)
        
        self.parent = parent
        self.page = page
        self.buildPage()
        
    def buildPage(self): 
        main_frame = ttk.Frame(self)
        
        title = ttk.Label(main_frame, text='Enter New Name',
            font=(None, 14))
           
        self.name_entry = ttk.Entry(main_frame)
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
        
        name = str(self.name_entry.get()).replace(' ', '')
        name = name[:10]    # Limit length of name
        
        for tab in self.page.parent.plot_pages:
            if name == tab.name:
                messagebox.showerror('Error!', 'Names must be unique')
                self.destroy()
                return
        if name:
            self.page.parent.parent_notebook.tab(self.page.plot_num, text=name)
            self.page.name = name
            self.page.plot.update()
            self.parent.destroy()    
        else:
            self.parent.destroy()
            

class LimitPage(ttk.Frame):
    '''Change value of individual node'''
    
    def __init__(self, plot, parent):
        super().__init__(parent)
        
        self.parent = parent
        self.plot = plot
        self.upper = self.plot.upper_limit
        self.lower = self.plot.lower_limit
        
        self.buildPage()
        
    def buildPage(self):
        main_frame = ttk.Frame(self, padding=5)
        
        title = ttk.Label(main_frame, text='Enter New Limits', font=(None, 12))
        
        upper_label = ttk.Label(main_frame, text='Upper:')
        self.upper_entry = ttk.Entry(main_frame, width=6)
        self.upper_entry.insert(0, self.upper)
        self.upper_entry.focus()
        
        lower_label = ttk.Label(main_frame, text='Lower:')
        self.lower_entry = ttk.Entry(main_frame, width=6)
        self.lower_entry.insert(0, self.lower)
     
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
            self.plot.upper_limit = int(self.upper_entry.get())
            self.plot.upper_limit = limit(
                self.plot.upper_limit, 5, 180)
            
            self.plot.lower_limit = int(self.lower_entry.get())
            self.plot.lower_limit = limit(
                self.plot.lower_limit, 0, self.plot.upper_limit-5)
            
            self.plot.update()
            
        except Exception as e:
            print('VAL ERROR: ', e)
        
        finally:
            self.parent.destroy()
            

class TimeAdjustPage(ttk.Frame):
    '''Add or remove time from the plot'''
    
    def __init__(self, plot, parent):
        super().__init__(parent)
        
        self.parent = parent
        self.plot = plot
        
        self.buildPage()
    
    def buildPage(self):
        self.time_entry_var = tk.IntVar()
        self.where_var = tk.StringVar()
        self.plus_minus_var = tk.StringVar()
        
        main_frame = ttk.Frame(self, padding=5)
        
        entry_frame = ttk.Frame(main_frame)
        time_label = ttk.Label(entry_frame, text='Seconds   ')
        time_entry = ttk.Entry(entry_frame, width=5,
            textvariable=self.time_entry_var)
        time_label.pack(side=tk.LEFT)
        time_entry.pack(side=tk.LEFT)
        
        where = ttk.Labelframe(main_frame, text='Where:', width=25)
        begin = ttk.Radiobutton(where, text = 'Beginning', value='begin',
            variable=self.where_var)
        end = ttk.Radiobutton(where, text= 'End', value='end',
            variable=self.where_var)
        begin.grid(sticky=tk.W)
        end.grid(sticky=tk.W)
        
        plus_minus = ttk.Labelframe(main_frame, text = '+/-:', width=25)
        add = ttk.Radiobutton(plus_minus, text = 'Add Time', value='add',
            variable=self.plus_minus_var)
        remove = ttk.Radiobutton(plus_minus, text= 'Remove Time',
            value='subtract', variable=self.plus_minus_var)
        add.grid(sticky=tk.W)
        remove.grid(sticky=tk.W)
        
        button_frame = ttk.Frame(main_frame)
        ok_button = ttk.Button(button_frame, text='OK', command=self.update)
        cancel_button = ttk.Button(button_frame, text='Cancel',
            command=self.parent.destroy)
        ok_button.pack(padx=5, side=tk.LEFT)
        cancel_button.pack(padx=5, side=tk.RIGHT)
        
        main_frame.pack(side=tk.TOP, pady = 10)
        entry_frame.grid()
        where.grid(row=1, column=0, pady=10)
        plus_minus.grid(row=1, column=1, pady=10)
        button_frame.grid(row=2, columnspan=2, pady=10)
        
    def update(self):
        '''Make the changes to all tabs/plots'''

        for plot_page in self.plot.parent.plot_pages:
        
            # Add time
            if self.plus_minus_var.get() == 'add':
                
                # Verify not going over 360 seconds total (Arduino memory limit)
                temp_length = \
                    ((len(plot_page.plot.ys)-1)/2) + (self.time_entry_var.get())
                if temp_length * len(self.plot.parent.plot_pages) > 360:
                    messagebox.showerror('Limit Error', 'Total of all routines \
                    must be less than 6 minutes \
                    (360 seconds)')
                    self.destroy()
                    return
                
                temp_arr = [0 for i in range(self.time_entry_var.get() * 2)]
                
                if self.where_var.get() == 'begin':
                    plot_page.plot.ys = temp_arr + plot_page.plot.ys
                    plot_page.plot.length = len(plot_page.plot.ys)
                    plot_page.plot.xs = [i for i in range(plot_page.plot.length)]
                    
                elif self.where_var.get() == 'end':
                    plot_page.plot.ys += temp_arr
                    plot_page.plot.length = len(plot_page.plot.ys)
                    plot_page.plot.xs = [i for i in range(plot_page.plot.length)]
            
            # Remove time
            if self.plus_minus_var.get() == 'subtract':
                nodes_to_remove = self.time_entry_var.get() * 2
                
                # Verify plot will still exist
                #~ if nodes_to_remove >= plot_page.plot.length:
                if nodes_to_remove >= (len(plot_page.plot.ys) - 1):
                    messagebox.showerror('Error',
                        'Removing too many seconds')
                    self.destroy()
                    return
                            
                if self.where_var.get() == 'begin':
                    del plot_page.plot.ys[:nodes_to_remove]
                    plot_page.plot.length = len(plot_page.plot.ys)
                    plot_page.plot.xs = [i for i in range(plot_page.plot.length)]
                    
                elif self.where_var.get() == 'end':
                    del plot_page.plot.ys[-nodes_to_remove:]
                    plot_page.plot.length = len(plot_page.plot.ys)
                    plot_page.plot.xs = [i for i in range(plot_page.plot.length)]
            
            # Update slider length to scroll along the plot
            # Upper limit is seconds minus half the length of the plot 'x_window'
            plot_page.slider['to'] = (plot_page.plot.length // 2) - 10
            plot_page.slider.set(0)
            plot_page.parent.num_of_seconds.set(int((len(plot_page.plot.ys)-1)/2))
            
            # Redraw the plots
            plot_page.plot.update()
            
        self.parent.destroy()
        


