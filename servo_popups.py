
import tkinter as tk
from tkinter import ttk


class Popup():
    '''Generic top level pop-up window'''

    def __init__(self, title='This is a Title', geometry='200x100'):
        # Create new top-level window
        self.dialog=tk.Toplevel()
        self.dialog.title(title)
        self.dialog.geometry(geometry)
        self.dialog.resizable(False, False)
        
        self.buildPage()
        
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
        
    def buildPage(self):
        main_frame = ttk.Frame(self.dialog)
        
        title = ttk.Label(main_frame, text='Made by REK', font=(None, 14))
        title.pack(expand=1)
        
        button_frame = ttk.Frame(main_frame)
        
        help_button = ttk.Button(button_frame, text='Help')
        ok_button = ttk.Button(button_frame, text='OK', command=self.close)
        
        main_frame.pack(fill=tk.BOTH, expand=1)
        help_button.pack(padx=5, side=tk.LEFT)
        ok_button.pack(padx=5, side=tk.RIGHT)
        button_frame.pack(side=tk.BOTTOM, pady=10)
    
    def close(self):
        self.dialog.destroy()


class ValuePopup(Popup):
    '''Change value of individual node'''
    
    def __init__(self, plot, node_index, title='Change Value', geometry='250x125'):
        super().__init__(title, geometry)
        
        self.plot = plot
        self.index = node_index
        
    def buildPage(self):
        main_frame = ttk.Frame(self.dialog, padding=5)
        
        label = ttk.Label(main_frame, text='Enter a new value', font=(None, 12))
        self.new_val_entry = ttk.Entry(main_frame, width=6)
        self.new_val_entry.focus()
        self.new_val_entry.bind('<Return>', self.update)
        button = ttk.Button(main_frame, text='OK', command=self.update)
    
        main_frame.pack(fill=tk.BOTH, expand=1)
        
        label.pack(padx=5, pady=5)
        self.new_val_entry.pack(pady=5)
        button.pack(pady=5)
            
    def update(self, event=None):
        
        try:
            new_value = int(self.new_val_entry.get())
            self.plot.ys[self.index] = self.plot.limit_range(new_value)
            self.plot.update()
            
        except Exception as e:
            print('VAL ERROR: ', e)
        
        finally:
            self.dialog.destroy()







