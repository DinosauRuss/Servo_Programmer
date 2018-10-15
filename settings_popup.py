
import tkinter as tk

from tkinter import messagebox
from tkinter import ttk

from servo_popups import Popup


class SettingsPopup(Popup):
    '''Generic popup with notebook to hold various settings pages'''
    
    def __init__(self):
        super().__init__(title='Settings')
        
        self.notebook = ttk.Notebook(self, width=300, height=300)
        
        self.buildPage()
    
    def buildPage(self):
        self.notebook.pack(anchor=tk.CENTER, fill=tk.BOTH)
        
    def addTab(self, page, txt='Tab'):    
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
        
        for page in self.page.parent.plot_pages:
            if name == page.name:
                messagebox.showerror('Error!', 'Names must be unique')
                self.parent.destroy()
                return
        if name:
            index = self.page.parent.plot_pages.index(self.page) + 1
            self.page.parent.parent_notebook.tab(index, text=name)
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
            
 
class TimeAddPage(ttk.Frame):
     
    def __init__(self, page, parent):
        super().__init__(parent)
         
        self.parent = parent
        self.page = page
        
        self.buildPage()
       
    def buildPage(self):
        
        self.time_entry_var = tk.IntVar()
        self.where_var = tk.StringVar()
        
        main_frame = ttk.Frame(self, padding=5)
        
        title = ttk.Label(main_frame, text='Add Time', font=(None, 14))
        
        entry_frame = ttk.Frame(main_frame)
        time_label = ttk.Label(entry_frame, text='Seconds   ')
        time_entry = ttk.Entry(entry_frame, width=5,
            textvariable=self.time_entry_var)
        time_label.pack(side=tk.LEFT)
        time_entry.pack(side=tk.LEFT)
        
        where = ttk.Frame(main_frame)
        begin = ttk.Radiobutton(where, text = 'Beginning', value='begin',
            variable=self.where_var)
        end = ttk.Radiobutton(where, text= 'End', value='end',
            variable=self.where_var)
        begin.grid(sticky=tk.W)
        end.grid(sticky=tk.W)
        
        button_frame = ttk.Frame(main_frame)
        ok_button = ttk.Button(button_frame, text='OK',
            command=self.update)
        cancel_button = ttk.Button(button_frame, text='Cancel',
            command=self.parent.destroy)
        ok_button.pack(side=tk.LEFT, padx=5)
        cancel_button.pack(side=tk.RIGHT, padx=5)
        
        main_frame.pack(side=tk.TOP, pady = 20)
        title.grid()
        entry_frame.grid(pady=10)
        where.grid(pady=10)
        button_frame.grid(pady=10)
        
    def update(self):
        try:
            seconds = self.time_entry_var.get()
        except Exception as e:
            print(e)
            messagebox.showerror('Error', 'Enter digits only')
            self.parent.destroy()
            return
        
        for plot_page in self.page.parent.plot_pages:
                
            # Verify not going over 360 seconds total (Arduino memory limit)
            temp_length = \
                ((len(plot_page.plot.ys)-1)/2) + (seconds)
            if temp_length * len(self.page.parent.plot_pages) > 360:
                messagebox.showerror('Limit Error', 'Total of all routines \
                must be less than 6 minutes \
                (360 seconds)')
                self.parent.destroy()
                return
            
            temp_arr = [0 for i in range(seconds * 2)]
            
            if self.where_var.get() == 'begin':
                plot_page.plot.ys = temp_arr + plot_page.plot.ys
                plot_page.plot.length = len(plot_page.plot.ys)
                plot_page.plot.xs = [i for i in range(plot_page.plot.length)]
                
            elif self.where_var.get() == 'end':
                plot_page.plot.ys += temp_arr
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
        
        
class TimeDelPage(ttk.Frame):
     
    def __init__(self, page, parent):
        super().__init__(parent)
         
        self.parent = parent
        self.page = page
        
        self.buildPage()
       
    def buildPage(self):
        
        self.time_entry_var = tk.IntVar()
        self.where_var = tk.StringVar()
        
        main_frame = ttk.Frame(self, padding=5)
        
        title = ttk.Label(main_frame, text='Delete Time', font=(None, 14))
        
        entry_frame = ttk.Frame(main_frame)
        time_label = ttk.Label(entry_frame, text='Seconds   ')
        time_entry = ttk.Entry(entry_frame, width=5,
            textvariable=self.time_entry_var)
        time_label.pack(side=tk.LEFT)
        time_entry.pack(side=tk.LEFT)
        
        where = ttk.Frame(main_frame)
        begin = ttk.Radiobutton(where, text = 'Beginning', value='begin',
            variable=self.where_var)
        end = ttk.Radiobutton(where, text= 'End', value='end',
            variable=self.where_var)
        begin.grid(sticky=tk.W)
        end.grid(sticky=tk.W)
        
        button_frame = ttk.Frame(main_frame)
        ok_button = ttk.Button(button_frame, text='OK',
            command=self.update)
        cancel_button = ttk.Button(button_frame, text='Cancel',
            command=self.parent.destroy)
        ok_button.pack(side=tk.LEFT, padx=5)
        cancel_button.pack(side=tk.RIGHT, padx=5)
        
        main_frame.pack(side=tk.TOP, pady = 20)
        title.grid()
        entry_frame.grid(pady=10)
        where.grid(pady=10)
        button_frame.grid(pady=10)
        
    def update(self):
        try:
            seconds = self.time_entry_var.get()
        except Exception as e:
            print(e)
            messagebox.showerror('Error', 'Enter digits only')
            self.parent.destroy()
            return
        
        for plot_page in self.page.parent.plot_pages:
                
            nodes_to_remove = self.time_entry_var.get() * 2
            
            # Verify plot will still exist
            #~ if nodes_to_remove >= plot_page.plot.length:
            if nodes_to_remove >= (len(plot_page.plot.ys) - 1):
                messagebox.showerror('Error',
                    'Removing too many seconds')
                self.parent.destroy()
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
        

class ServoDeletePage(ttk.Frame):
    
    def __init__(self, plot, parent):
        super().__init__(parent)
        
        self.plot = plot
        self.parent = parent
        
        self.buildPage()
    
    def buildPage(self):
        main_frame = ttk.Frame(self)
        button_frame = ttk.Frame(main_frame)
        
        title = ttk.Label(main_frame, text='Delete Tab?', font=(None, 14))
        del_button = ttk.Button(button_frame, text='Delete',
            command=self.deleteTab)
        cancel_button = ttk.Button(button_frame, text='Cancel',
            command=self.parent.destroy)
    
        title.pack()
        button_frame.pack(pady=10)
        del_button.grid(row=0, column=0, padx=5)
        cancel_button.grid(row=0, column=1, padx=5)
        
        main_frame.pack(side=tk.TOP, pady=20)
    
    def deleteTab(self):
        if self.plot.parent.parent.num_of_servos.get() > 1:
            if messagebox.askokcancel('Delete Tab?',
                'Are you sure you want to delet this tab?'):
                
                name = self.plot.parent.name + '_tab'
                
                self.plot.parent.parent.plot_pages.remove(self.plot.parent)
                self.plot.parent.parent.parent_notebook.forget(self.plot.parent)
                self.plot.parent.parent.num_of_servos.set(len(self.plot.parent.parent.plot_pages))
                
                self.plot.parent.__class__.total_pages -= 1
                
                self.parent.destroy()
            else:
                self.parent.destroy()
            
                
        
    



