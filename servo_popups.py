
import tkinter as tk
from tkinter import ttk


class Popup():
    '''Generic top level pop-up window'''

    def __init__(self, title='This is a Title', geometry=None):
        # Create new top-level window
        self.dialog=tk.Toplevel()
        self.dialog.title(title)
        if geometry:
            self.dialog.geometry(geometry)
        self.dialog.resizable(False, False)
        
        #~ self.buildPage()
        
        # Freezes main window until popup is closed
        self.dialog.transient()
        self.dialog.grab_set()
        
    def buildPage(self):
        pass
    
    def update(self, event=None):
        pass


class NamePopup(Popup):
    '''Change the name/title of plot and tab'''
    
    def __init__(self, page, title='Change Name', geometry='200x100'):
        super().__init__(title, geometry)
        
        self.page = page
        self.buildPage()
        
    def buildPage(self):    
        self.name_entry = ttk.Entry(self.dialog)
        self.name_entry.focus()
        self.name_entry.bind('<Return>', self.update)
        
        button_frame = ttk.Frame(self.dialog)
        
        ok_button = ttk.Button(button_frame, text='Ok',width=5, 
            command=self.update)
        cancel_button = ttk.Button(button_frame, text='Cancel', width=5,
            command=self.dialog.destroy)
        
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
                self.dialog.destroy()
                return
        if name:
            self.page.parent.parent_notebook.tab(self.page.plot_num, text=name)
            self.page.name = name
            self.page.plot.update()
            self.dialog.destroy()    
        else:
            self.dialog.destroy()


class AboutPopup(Popup):
    '''Popup window for the menubar'''
    
    def __init__(self, title='About', geometry='200x100'):
        super().__init__(title, geometry)
        
        self.buildPage()
        
    def buildPage(self):
        main_frame = ttk.Frame(self.dialog)
        
        title = ttk.Label(main_frame, text='Made by REK', font=(None, 14))
        title.pack(expand=1)
        
        button_frame = ttk.Frame(main_frame)
        
        help_button = ttk.Button(button_frame, text='Help', width=10)
        ok_button = ttk.Button(button_frame, text='OK', width=10,
            command=self.close)
        
        main_frame.pack(fill=tk.BOTH, expand=1)
        help_button.pack(padx=5, side=tk.LEFT)
        ok_button.pack(padx=5, side=tk.RIGHT)
        button_frame.pack(side=tk.BOTTOM, pady=10)
    
    def close(self):
        self.dialog.destroy()


class ValuePopup(Popup):
    '''Change value of individual node'''
    
    def __init__(self, plot, node_index, title='Change Value', geometry='240x125'):
        super().__init__(title, geometry)
        
        self.plot = plot
        self.index = node_index
        
        self.buildPage()
        
    def buildPage(self):
        self.entry_value = tk.IntVar()
        
        main_frame = ttk.Frame(self.dialog, padding=5)
        
        label = ttk.Label(main_frame, text='Enter a new value', font=(None, 12))
        self.new_val_entry = ttk.Entry(main_frame, width=6,
            textvariable=self.entry_value)
        self.entry_value.set(self.plot.ys[self.index])
        self.new_val_entry.focus()
        self.new_val_entry.bind('<Return>', self.update)
        
        ok_button = ttk.Button(main_frame, text='OK', command=self.update)
        cancel_button = ttk.Button(main_frame, text='Cancel',
            command=self.dialog.destroy)
    
        main_frame.pack(fill=tk.BOTH, expand=1)
        
        label.pack(padx=5, pady=5)
        self.new_val_entry.pack(pady=5)
        ok_button.pack(pady=5, side=tk.LEFT)
        cancel_button.pack(pady=5, side=tk.RIGHT)
            
    def update(self, event=None):
        
        try:
            new_value = int(self.entry_value.get())
            self.plot.ys[self.index] = self.plot.limit_range(new_value)
            self.plot.update()
            
        except Exception as e:
            print('VAL ERROR: ', e)
        
        finally:
            self.dialog.destroy()


class LimitPopup(Popup):
    '''Change value of individual node'''
    
    def __init__(self, plot, title='Change Limits'):
        super().__init__(title)
        
        self.plot = plot
        self.upper = self.plot.upper_limit
        self.lower = self.plot.lower_limit
        
        self.buildPage()
        
        
    def buildPage(self):
        main_frame = ttk.Frame(self.dialog, padding=5)
        
        title = ttk.Label(main_frame, text='Enter new values', font=(None, 12))
        
        upper_label = ttk.Label(main_frame, text='Upper:')
        self.upper_entry = ttk.Entry(main_frame, width=6)
        self.upper_entry.insert(0, self.upper)
        self.upper_entry.focus()
        
        lower_label = ttk.Label(main_frame, text='Lower:')
        self.lower_entry = ttk.Entry(main_frame, width=6)
        self.lower_entry.insert(0, self.lower)
     
        button = ttk.Button(main_frame, text='OK', command=self.update)
    
        main_frame.pack(fill=tk.BOTH, expand=1)
        
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
            self.dialog.destroy()

