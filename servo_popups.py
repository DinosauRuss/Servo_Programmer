
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


#~ class ValuePopup(Popup):
    #~ '''Change value of individual node'''
    
    #~ def __init__(self, plot, node_index, title='Change Value', geometry='240x125'):
        #~ super().__init__(title, geometry)
        
        #~ self.plot = plot
        #~ self.index = node_index
        
        #~ self.buildPage()
        
    #~ def buildPage(self):
        #~ self.entry_value = tk.IntVar()
        #~ self.entry_value.set(self.plot.ys[self.index])
        
        #~ main_frame = ttk.Frame(self, padding=5)
        
        #~ label = ttk.Label(main_frame, text='Enter a new value', font=(None, 12))
        #~ self.new_val_entry = ttk.Entry(main_frame, width=6,
            #~ textvariable=self.entry_value)
        #~ self.new_val_entry.focus()
        #~ self.new_val_entry.bind('<Return>', self.update)
        
        #~ ok_button = ttk.Button(main_frame, text='OK', command=self.update)
        #~ cancel_button = ttk.Button(main_frame, text='Cancel',
            #~ command=self.destroy)
    
        #~ main_frame.pack(fill=tk.BOTH, expand=1)
        
        #~ label.pack(padx=5, pady=5)
        #~ self.new_val_entry.pack(pady=5)
        #~ ok_button.pack(pady=5, side=tk.LEFT)
        #~ cancel_button.pack(pady=5, side=tk.RIGHT)
            
    #~ def update(self, event=None):
        
        #~ try:
            #~ self.plot.ys[self.index] = self.plot.limit_range(self.entry_value.get())
            #~ self.plot.update()
            
        #~ except Exception as e:
            #~ print('VAL ERROR: ', e)
        
        #~ finally:
            #~ self.destroy()
class ValuePopup(Popup):
    '''Returns new value for a node,
       and ok(True) or cancel(False) button press'''
    
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
    """A simple text viewer dialog for IDLE
    """
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
     
    def __init__(self, settings_page):
        super().__init__(title='Dev Page', geometry='250x100')
         
        self.settings_page = settings_page
         
        self.buildPage()
         
    def buildPage(self):
        
        self.new_seconds_var = tk.IntVar()
        self.new_servos_var = tk.IntVar()
        self.new_seconds_var.set(self.settings_page.__class__.max_seconds)
        self.new_servos_var.set(self.settings_page.__class__.max_servos)
        
        main_frame = ttk.Frame(self, padding=5)
        
        seconds_label = ttk.Label(main_frame, text='Total runtime (seconds)')
        seconds_entry = ttk.Entry(main_frame, textvariable=self.new_seconds_var,
            width=6)
        
        servos_label = ttk.Label(main_frame, text='Total number of servos')
        servos_entry = ttk.Entry(main_frame, textvariable=self.new_servos_var,
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
        
        button_frame.grid(columnspan=2, pady=10)
        ok_button.pack(side=tk.LEFT)
        cancel_button.pack(side=tk.RIGHT)
        
    def update(self):
        
        current_total_servos = self.settings_page.num_of_servos.get()
        current_total_seconds =\
            self.settings_page.num_of_seconds.get() * current_total_servos
        
        if self.new_seconds_var.get() < current_total_seconds:
            messagebox.showerror('Error', 'New max runtime is less than\n'\
                + 'current routine runtime')
            self.destroy()
            return
        if self.new_servos_var.get() < current_total_servos:
            messagebox.showerror('Error', 'New max servos is less than\n'\
                + 'current number of servos')
            self.destroy()
            return

        self.settings_page.__class__.max_seconds = self.new_seconds_var.get()
        self.settings_page.__class__.max_servos = self.new_servos_var.get()
        
        self.settings_page.seconds_label_var.set('Routine length (in seconds)\
            \n(1-{}):'.format(self.settings_page.max_seconds))
        self.settings_page.servo_label_var.set(\
            'Number of servos (1-{})'.format(self.settings_page.max_servos))
        
        self.destroy()
    
    

