
import tkinter as tk

from tkinter import messagebox
from tkinter import ttk


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


class NamePopup(Popup):
    '''Change the name/title of plot and tab'''
    
    def __init__(self, page, title='Change Name', geometry='200x100'):
        super().__init__(title, geometry)
        
        self.page = page
        self.buildPage()
        
    def buildPage(self):    
        self.name_entry = ttk.Entry(self)
        self.name_entry.focus()
        self.name_entry.bind('<Return>', self.update)
        
        button_frame = ttk.Frame(self)
        
        ok_button = ttk.Button(button_frame, text='Ok',width=5, 
            command=self.update)
        cancel_button = ttk.Button(button_frame, text='Cancel', width=5,
            command=self.destroy)
        
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
            self.destroy()    
        else:
            self.destroy()


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
            command=lambda: HelpPopup('Info', filename='help_file.txt'))
        ok_button = ttk.Button(button_frame, text='OK', width=10,
            command=self.destroy)
        
        main_frame.pack(fill=tk.BOTH, expand=1)
        help_button.pack(padx=5, side=tk.LEFT)
        ok_button.pack(padx=5, side=tk.RIGHT)
        button_frame.pack(side=tk.BOTTOM, pady=10)
    

class ValuePopup(Popup):
    '''Change value of individual node'''
    
    def __init__(self, plot, node_index, title='Change Value', geometry='240x125'):
        super().__init__(title, geometry)
        
        self.plot = plot
        self.index = node_index
        
        self.buildPage()
        
    def buildPage(self):
        self.entry_value = tk.IntVar()
        
        main_frame = ttk.Frame(self, padding=5)
        
        label = ttk.Label(main_frame, text='Enter a new value', font=(None, 12))
        self.new_val_entry = ttk.Entry(main_frame, width=6,
            textvariable=self.entry_value)
        self.entry_value.set(self.plot.ys[self.index])
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
            new_value = int(self.entry_value.get())
            self.plot.ys[self.index] = self.plot.limit_range(new_value)
            self.plot.update()
            
        except Exception as e:
            print('VAL ERROR: ', e)
        
        finally:
            self.destroy()


class LimitPopup(Popup):
    '''Change value of individual node'''
    
    def __init__(self, plot, title='Change Limits'):
        super().__init__(title)
        
        self.plot = plot
        self.upper = self.plot.upper_limit
        self.lower = self.plot.lower_limit
        
        self.buildPage()
        
    def buildPage(self):
        main_frame = ttk.Frame(self, padding=5)
        
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
            self.destroy()
            

class TimeAdjustPopup(Popup):
    '''Add or remove time from the plot'''
    
    def __init__(self, plot, title='Adjust Routine Time'):
        super().__init__(title)
        
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
            command=lambda: self.destroy())
        ok_button.pack(padx=5, side=tk.LEFT)
        cancel_button.pack(padx=5, side=tk.RIGHT)
        
        main_frame.grid()
        entry_frame.grid()
        where.grid(row=1, column=0, pady=10)
        plus_minus.grid(row=1, column=1, pady=10)
        button_frame.grid(row=2, columnspan=2, pady=10)
        
    def update(self):
        '''Make the changes to all tabs/plots'''

        for plot_page in self.plot.parent.parent.plot_pages:
        
            # Add time
            if self.plus_minus_var.get() == 'add':
                
                # Verify not going over 360 seconds total (Arduino memory limit)
                temp_length = \
                    ((len(plot_page.plot.ys)-1)/2) + (self.time_entry_var.get())
                if temp_length * len(self.plot.parent.parent.plot_pages) > 360:
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
                if nodes_to_remove >= plot_page.plot.length:
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
            
        self.destroy()
        
        
class HelpPopup(Popup):
    """A simple text viewer dialog for IDLE
    """
    def __init__(self, title, filename=None):
        
        super().__init__()
        
        self.text = self.view_file(filename)
        
        self.configure(borderwidth=5)
        self.geometry('500x400')

        self.title(title)
        self.bind('<Return>', lambda x: self.destroy())
        self.bind('<Escape>', lambda x: self.destroy())
        
        self.buildPage()
        
        self.transient()
        self.grab_set()
        self.wait_window()

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
    





