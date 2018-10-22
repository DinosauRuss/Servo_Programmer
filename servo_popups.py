
import tkinter as tk

from tkinter import messagebox
from tkinter import ttk

import traceback


class Popup(tk.Toplevel):
    '''Generic top level pop-up window'''

    def __init__(self, title='This is a Title', geometry=None):
        super().__init__()
        
        self.title(title)
        if geometry:
            self.geometry(geometry)
        self.resizable(False, False)
        
        # Freezes main window until popup is closed
        self.transient()
        self.grab_set()
        
    def buildPage(self):
        pass
    
    def update(self, event=None):
        pass


class AboutPopup(Popup):
    '''Popup window for the menubar'''
    
    def __init__(self, title='About', geometry='200x100'):
        super().__init__(title, geometry)
        
        self.buildPage()
        
    def buildPage(self):
        main_frame = ttk.Frame(self)
        
        title = ttk.Label(main_frame, text='Made by REK', font=(None, 14))
        title.pack(expand=1)
        
        button_frame = ttk.Frame(main_frame)
        
        help_button = ttk.Button(button_frame, text='Help', width=10,
            command=lambda: HelpPopup(filename='help_file.txt'))
        ok_button = ttk.Button(button_frame, text='OK', width=10,
            command=self.destroy)
        
        main_frame.pack(fill=tk.BOTH, expand=1)
        help_button.pack(padx=5, side=tk.LEFT)
        ok_button.pack(padx=5, side=tk.RIGHT)
        button_frame.pack(side=tk.BOTTOM, pady=10)


class ValuePopup(Popup):
    '''Returns new value for a node'''
    
    def __init__(self, current_value, title='Change Value', geometry='240x125'):
        super().__init__(title, geometry)
        
        self.current_value = current_value
        self.send_val = False
        
        self.buildPage()
        
    def buildPage(self):
        self.entry_value = tk.IntVar()
        self.entry_value.set(self.current_value)
        
        main_frame = ttk.Frame(self, padding=5)
        
        label = ttk.Label(main_frame, text='Enter a new value', font=(None, 12))
        self.new_val_entry = ttk.Entry(main_frame, width=6,
            textvariable=self.entry_value)
        self.new_val_entry.focus()
        self.new_val_entry.bind('<Return>', self.update)
        
        ok_button = ttk.Button(main_frame, text='OK', command=self.update)
        cancel_button = ttk.Button(main_frame, text='Cancel',
            command=self.destroy)
    
        main_frame.pack(fill=tk.BOTH, expand=1)
        
        label.pack(padx=5, pady=5)
        self.new_val_entry.pack(pady=5)
        ok_button.pack(pady=5, side=tk.LEFT)
        cancel_button.pack(pady=5, side=tk.RIGHT)
            
    def update(self, event=None):
        try:
            self.entry_value.get()
        except Exception as e:
            print('VAL ERROR: ', e)
            traceback.print_exc()
        else:
            self.send_val = True
        finally:
            self.destroy()
            
    def show(self):
        self.wait_window()
        
        if self.send_val:
            return (self.entry_value.get(), True)
        else:
            return (self.current_value, False)

        
class HelpPopup(Popup):
    """Text viewer dialog that shows help file"""
    def __init__(self, title='Help', filename=None):
        
        super().__init__(title)
        
        self.text = self.view_file(filename)
        
        self.configure(borderwidth=5)
        
        self.buildPage()

    def buildPage(self):
        text_frame = ttk.Frame(self, relief=tk.SUNKEN)
        button_frame = ttk.Frame(self)
        
        ok_button = ttk.Button(button_frame, text='Close',
                               command=self.destroy, takefocus=tk.FALSE)
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL,
                                       takefocus=tk.FALSE)
        self.text_view = tk.Text(text_frame, wrap=tk.WORD,
                             bg='#ffffff', fg='#000000')
        self.text_view.insert(0.0, self.text)
        self.text_view.config(state=tk.DISABLED)
                             
        scrollbar.config(command=self.text_view.yview)
        self.text_view.config(yscrollcommand=scrollbar.set)
        
        text_frame.pack(side=tk.TOP,expand=tk.TRUE,fill=tk.BOTH)
        button_frame.pack(side=tk.BOTTOM,fill=tk.X)
        
        ok_button.pack()
        scrollbar.pack(side=tk.RIGHT,fill=tk.Y)
        self.text_view.pack(side=tk.LEFT,expand=tk.TRUE,fill=tk.BOTH)

    @staticmethod
    def view_file(filename):
        try:
            with open(filename, 'r') as infile:
                return infile.read()
        except IOError:
            messagebox.showerror(title='File Load Error',
                message='Unable to load file {} '.format(filename))      
                
                
class DevPopup(Popup):
     
    def __init__(self, seconds, servos, default_val):
        super().__init__(title='Dev Page', geometry='250x150')
         
        self.seconds = seconds
        self.servos = servos
        self.default_val = default_val
        
        self.send_data = False
         
        self.buildPage()
         
    def buildPage(self):
        
        self.new_seconds_var = tk.IntVar()
        self.new_servos_var = tk.IntVar()
        self.new_node_default_val = tk.IntVar()
        self.new_seconds_var.set(self.seconds)
        self.new_servos_var.set(self.servos)
        self.new_node_default_val.set(self.default_val)
        
        main_frame = ttk.Frame(self, padding=5)
        
        seconds_label = ttk.Label(main_frame, text='Total runtime (seconds)')
        seconds_entry = ttk.Entry(main_frame, textvariable=self.new_seconds_var,
            width=6)
        
        servos_label = ttk.Label(main_frame, text='Total number of servos')
        servos_entry = ttk.Entry(main_frame, textvariable=self.new_servos_var,
            width=6)
        
        default_label = ttk.Label(main_frame, text='Servo default angle')
        default_entry = ttk.Entry(main_frame,
            textvariable=self.new_node_default_val,
            width=6)
        
        button_frame = ttk.Frame(main_frame)    
        ok_button = ttk.Button(button_frame, text='OK', command=self.update)
        cancel_button = ttk.Button(button_frame, text='Cancel',
            command=self.destroy)
        
        main_frame.pack(fill=tk.BOTH, expand=1)
        
        seconds_label.grid(row=0, column=0)
        seconds_entry.grid(row=0, column=1)
        servos_label.grid(row=1, column=0)
        servos_entry.grid(row=1, column=1)
        default_label.grid(row=2, column=0)
        default_entry.grid(row=2, column=1)
        
        button_frame.grid(columnspan=2, pady=10)
        ok_button.pack(side=tk.LEFT)
        cancel_button.pack(side=tk.RIGHT)
        
    def update(self):
        
        try:
            self.new_seconds_var.get()
            self.new_servos_var.get() 
            self.new_node_default_val.get()           
        except Exception as e:
            print('VALUE ERROR: ', e)
            traceback.print_exc()
        else:
            self.send_data = True
        finally:
            self.destroy()
        
    def show(self):
        self.wait_window()
        
        if self.send_data:
            return ( True,
                     self.new_seconds_var.get(),
                     self.new_servos_var.get(),
                     self.new_node_default_val.get() )
        else:
            return ( False, None, None, None )
    
    

