
import dill
import jinja2
import os
import traceback

from matplotlib import use as Use
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from matplotlib.widgets import SpanSelector

from math import ceil
from time import sleep

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as fd
from tkinter import messagebox

from servo_popups import *
from settings_popup import *

from pprint import pprint

# Needed to embed matplotlib in tkinter
Use('TkAgg')


class MainApp():
    def __init__(self, width=800, height=600):
        
        self.main = tk.Tk()
        self.main.title('Servo Programmer')
        self.main.geometry('{}x{}'.format(width, height))
        self.main.resizable(False, False)
        self.main.update()
        
        # Set ttk style
        self.main.style = ttk.Style()
        self.main.style.theme_use('clam')
        
        self.buildPage()
        
        self.main.mainloop()
        
    def buildPage(self):
        # ----- Meubar configuration -----
        menubar = tk.Menu(self.main)
        
        self.file_menu = tk.Menu(menubar, tearoff=0)
        self.file_menu.add_command(label='Save',
            command=lambda: self.settings_tab.saveData(),
            state='disabled')
        self.file_menu.add_command(label='Load',
            command=lambda: self.settings_tab.loadData())
        self.file_menu.add_command(label='Quit',
            command=self.main.destroy)
        
        self.edit_menu = tk.Menu(menubar, tearoff=0)
        self.edit_menu.add_command(label='Add Servo', 
            command=lambda: self.settings_tab.addServo(),
            state='disabled')
        self.edit_menu.add_command(label='Import Servos',
            command=lambda: self.settings_tab.loadData(),
            state='disabled')
        self.edit_menu.add_command(label='Output Sketch',
            command=lambda: self.settings_tab.outputSketch(), 
            state='disabled')
        
        self.about_menu = tk.Menu(self.main, tearoff=0)
        self.about_menu.add_command(label='About', command=lambda: AboutPopup())
        
        menubar.add_cascade(label='File', menu=self.file_menu)
        menubar.add_cascade(label='Edit', menu=self.edit_menu)
        menubar.add_cascade(label='Help', menu=self.about_menu)
        
        # Add menubar to main window
        self.main.config(menu=menubar)
        
        # ----- Notebook/tab configuration -----    
        notebook = ttk.Notebook(self.main, width=self.main.winfo_width(),
            height=self.main.winfo_height())
        
        # Initial tab -----
        self.settings_tab = SettingsPage(notebook, self)
        notebook.add(self.settings_tab, text='Settings')
        
        notebook.pack(anchor=tk.CENTER, fill=tk.BOTH)
        

class SettingsPage(ttk.Frame):
    '''First tab w/ settings'''

    plot_pages = []    # Used when outputting data
    millis = 15        # Delay between each inBetweener value
    
    initial_load_flag = False    # True after first time loading data
    load_flag = False
    
    max_seconds = 360
    max_servos = 8
    node_default_val = 90
    
    def __init__(self, parent_notebook, parent):
        super().__init__()
        
        self.parent_notebook = parent_notebook
        self.parent = parent
        
        self.buildPage()
        
    def buildPage(self):
        '''Layout widgets for the tab'''
        
        self.num_of_seconds = tk.IntVar()
        self.num_of_servos = tk.IntVar()
        self.button_entry_val = tk.StringVar()
        self.btn_check_var = tk.IntVar()
        self.output_type_var = tk.StringVar()   # Pin nums or i2c
        
        # Used to update the labels when max seconds/servos changed
        self.seconds_label_var = tk.StringVar()
        self.servo_label_var = tk.StringVar()
        
        main_frame = ttk.Frame(self)
        main_frame.pack(expand=1, fill=tk.BOTH)
        
        # Use Shift+d to change max seconds/servos
        #~ main_frame.bind("<Shift-D>", lambda event: DevPopup(self))
        main_frame.bind("<Shift-D>", lambda event: self.changeDefaults())
        main_frame.bind("<Button-1>", lambda event: main_frame.focus_set())
        
        # --- Left side Frame ---
        left = ttk.Frame(main_frame)
        left.pack(side=tk.LEFT, anchor=tk.N)
        
        l_title = ttk.Label(left, text='Settings', font=(None, 25))
        l_title.grid(columnspan=5, pady=20)
        
        self.seconds_label_var.set('Routine length (in seconds)\
            \n(1-{}):'.format(SettingsPage.max_seconds))
        seconds_label = ttk.Label(left, textvariable=self.seconds_label_var)
        seconds_label.grid(padx=10, pady=15)
        
        self.seconds_entry = ttk.Entry(left, width=5, justify=tk.RIGHT,
            textvariable = self.num_of_seconds)
        self.seconds_entry.grid(padx=25, pady=15, row=1, column=1)
        
        self.servo_label_var.set(\
            'Number of servos (1-{})'.format(SettingsPage.max_servos))
        servo_total_label = ttk.Label(left, textvariable=self.servo_label_var)
        servo_total_label.grid(padx=10, pady=15)
        
        self.servo_total_entry = ttk.Entry(left, width=5, justify=tk.RIGHT,
            textvariable = self.num_of_servos)
        self.servo_total_entry.grid(padx=25, pady=15, row=2, column=1)
        
        self.generate_plots_button = ttk.Button(left, text='Generate Plots',
            command=self.generatePlots)
        self.generate_plots_button.grid(padx=25, pady=25, row=1, column=2,
            rowspan=2)
            
        self.add_servo_button = ttk.Button(left, text='Add Servo',
            state='disabled', command=self.addServo)
        self.add_servo_button.grid(pady=50)
        
        # --- Right side Frame ---
        right = ttk.Frame(main_frame)
        right.pack(anchor=tk.CENTER)
        
        r_title = ttk.Label(right, text='Output', font=(None, 25))
        r_title.grid(columnspan=5, pady=20)
        
        self.btn_check_var.set(False)
        button_checkbox = ttk.Checkbutton(right,
            text = 'Use button to Start Routine\n(Enter Pin Number)',
            variable=self.btn_check_var,
            command=self.toggle_btn_checkbox)
        button_checkbox.grid()
    
        self.button_entry = ttk.Entry(right, width=5, justify=tk.RIGHT,
            textvariable=self.button_entry_val, state='disabled')
        self.button_entry.grid(padx=25, pady=5, row=1, column=1)
        
        output_choice = ttk.LabelFrame(right, text='Servo Control Method')
        output_choice.grid(pady=15, sticky=tk.W)
        
        self.i2c = ttk.Radiobutton(output_choice, text='i2c PCA9865',
            variable=self.output_type_var, value='i2c')
        self.i2c.pack(side=tk.LEFT, padx=5)
        self.i2c.invoke()   # Sets as efault selection
        self.pins = ttk.Radiobutton(output_choice, text='Arduino Pins',
            variable=self.output_type_var, value='pins')
        self.pins.pack(side=tk.RIGHT, padx=5)
    
        self.output_button = ttk.Button(right, text='Output Sketch', width=15,
            state='disabled', command=self.outputSketch)
        self.output_button.grid(pady=50, columnspan=2)
        
        self.save_button = ttk.Button(right, text='Save', state='disabled',
            command=self.saveData)
        self.save_button.grid(sticky=tk.W)

        self.load_button = ttk.Button(right, text='Load',
            command=self.loadData)
        self.load_button.grid(row=4, column=1)
        

        self.resetEntries()
    
    def toggle_btn_checkbox(self):
        '''Toggle state of button entry based on checkbox'''
        
        if self.btn_check_var.get():
            self.button_entry.configure(state='normal')
        else:
            self.button_entry.configure(state='disabled')
            self.button_entry_val.set('None')
    
    def resetEntries(self):
        '''Clear the entry widgets'''
        
        self.num_of_seconds.set(10)
        self.num_of_servos.set(0)
        self.button_entry_val.set('None')
    
    def changeDefaults(self):
        '''Change class attribute defaults with popup'''
        
        cls = SettingsPage
        
        (ok_cancel, new_max_seconds, new_max_servos, new_default_val) = \
            DevPopup(cls.max_seconds, cls.max_servos, cls.node_default_val).show()
        
        # If ok button closed popup
        if ok_cancel:    
            current_total_routine_seconds =\
                self.num_of_seconds.get() * self.num_of_servos.get()
            
            if new_max_seconds < current_total_routine_seconds:
                messagebox.showerror('Error', 'New max runtime is less than\n'\
                    + 'current routine runtime')
                return
                
            if new_max_servos < self.num_of_servos.get():
                messagebox.showerror('Error', 'New max servos is less than\n'\
                    + 'current number of servos')
                self.destroy()
                return

            cls.max_seconds = new_max_seconds
            cls.max_servos = new_max_servos
            cls.node_default_val =\
                self.constrain(new_default_val, 0, 180)
            
            self.seconds_label_var.set('Routine length (in seconds)\
                \n(1-{}):'.format(new_max_seconds))
            self.servo_label_var.set(\
                'Number of servos (1-{})'.format(new_max_servos))
                
        # If cancel button closed popup        
        else:
            return
    
    def generatePlots(self):
        '''
        Generate specified number of Plot tabs each containing a plot
        of the specified routine length
        '''
        
        if SettingsPage.load_flag:
            self.loadServos()
            
        else:
            # Generate tabs/plots from inputs on Settings Page
            try: 
                # Check inputs for errors
                #~ constrain = lambda n, n_min, n_max: max(min(n, n_max), n_min)
                
                # Routine between 1 and (self.max_seconds)
                temp_secs= self.num_of_seconds.get()
                self.num_of_seconds.set(self.constrain(temp_secs, 1, SettingsPage.max_seconds))
                
                # Maximum of SettingsPage.max_servos
                temp_servos = self.num_of_servos.get()
                self.num_of_servos.set(self.constrain(temp_servos, 1, SettingsPage.max_servos))
                
                if (self.num_of_servos.get() * \
                        self.num_of_seconds.get()) > SettingsPage.max_seconds:
                    self.resetEntries()
                    messagebox.showerror('Limit Error', 'Total of all routines \
                        must be less than \
                        ({} seconds)'.format(SettingsPage.max_seconds))
                    return
        
            except Exception as e:
                print(e)
                print(traceback.format_exc())
                messagebox.showerror(title='Error!', message='Inputs must be numbers')
                self.resetEntries()
                return
            
            else:
                for i in range(self.num_of_servos.get()):
                    plot_title = 'Servo{}'.format(i+1)
                    tab_name = plot_title + '_tab'
                    plotPage = PlotPage(self, plot_title)
                    
                    self.parent_notebook.add(plotPage, text=plot_title)
                    SettingsPage.plot_pages.append(plotPage)
                    
                    SettingsPage.initial_load_flag = True
        
        # Change button states after loading or generating new plots
        self.generate_plots_button['state']='disabled'
        self.seconds_entry['state']='disabled'
        self.servo_total_entry['state']='disabled'
        self.add_servo_button['state'] = 'normal'
        
        self.save_button['state'] = 'normal'
        self.load_button['state'] = 'disabled'
        self.output_button['state'] = 'normal'
        
        # Change main menubar states
        self.parent.file_menu.entryconfig(0, state='normal')
        self.parent.file_menu.entryconfig(1, state='disabled')
        self.parent.edit_menu.entryconfig(0, state='normal')
        self.parent.edit_menu.entryconfig(1, state='normal')
        self.parent.edit_menu.entryconfig(2, state='normal')
    
    def addServo(self):
        '''Add additional no-data servo'''
        
        num = self.num_of_servos.get()
        
        if num >= SettingsPage.max_servos:
            messagebox.showerror('Error',
                'Limit of {} servos'.format(SettingsPage.max_servos))
            return
        if (num + 1) * self.num_of_seconds.get() > SettingsPage.max_seconds:
            messagebox.showerror('Error',\
                'Total routine time limited to {}'.format(SettingsPage.max_seconds)
                + ' seconds\n\nCannot add servo')
            return
            
        #~ plot_title = 'New_Servo{}'.format(self.num + 1)
        plot_title = 'New_Servo{}'.format(PlotPage.total_pages)
        tab_name = plot_title + '_tab'
        plotPage = PlotPage(self, plot_title)
        
        self.parent_notebook.add(plotPage, text=plot_title)
        SettingsPage.plot_pages.append(plotPage)
        
        self.num_of_servos.set(num + 1)
    
    def loadServos(self):
        '''Add additional servo(s) with previously recorded data'''
        
        # Use attribute 'settings' from self.loadData
        if not SettingsPage.initial_load_flag:
            # If initial load has not happened yet,
            # Fill entry boxes with values
            if self.settings['button_#'] == 'None':
                self.btn_check_var.set(False)
            else:
                self.btn_check_var.set(True)
                self.button_entry_val.set(self.settings['button_#'])
            if self.settings['output_type'] == 'i2c':
                self.i2c.invoke()
            else:
                self.pins.invoke()
            self.toggle_btn_checkbox()
            self.num_of_seconds.set(self.settings['seconds'])
            
        
        # Generate tabs/plots using loaded data
        
        # Prevent overloading max number of servos
        current_servos = self.num_of_servos.get()
        num_loaded_servos = len(self.settings['plot_pages'])
        if (num_loaded_servos + current_servos) > SettingsPage.max_servos:
            messagebox.showerror('Error', 'Loading will excede max number of servos')
            return
        new_num_servos = current_servos + len(self.settings['plot_pages'])
            
        # Prevent overloading max seconds / adjust length as necessary
        current_seconds = self.num_of_seconds.get()
        loaded_seconds = int((len(self.settings['plot_pages'][0][2])-1) / 2)
        
        if current_seconds > loaded_seconds:
            if (current_seconds * new_num_servos) > SettingsPage.max_seconds:
                messagebox.showerror('Error', 'Loading too many seconds')
                return
            else:
                seconds_to_add = int(current_seconds - loaded_seconds)
                nodes_to_add = seconds_to_add * 2
                
                # Add time to new loaded plots to match length of current plots
                for page in self.settings['plot_pages']:
                    page[2] +=\
                        [SettingsPage.node_default_val for i in range(nodes_to_add)]
                    
        elif current_seconds < loaded_seconds:
            if (loaded_seconds * new_num_servos) > SettingsPage.max_seconds:
                messagebox.showerror('Error', 'Loading too many seconds')
                return
            else:
                seconds_to_add = int(loaded_seconds - current_seconds)
                nodes_to_add = seconds_to_add * 2
                
                # Add time to current plots to match length of new loaded plots
                for page in SettingsPage.plot_pages:
                    page.plot.ys +=\
                        [SettingsPage.node_default_val for i in range(nodes_to_add)]
                    
                    page.plot.length = len(page.plot.ys)
                    page.plot.xs = [i for i in range(page.plot.length)]
                    
                    page.slider['to'] = (page.plot.length // 2) - 10
                    page.parent.num_of_seconds.set(int((len(page.plot.ys)-1)/2))    
                    page.plot.update()
                
        elif loaded_seconds == current_seconds:
            if (loaded_seconds * new_num_servos) > SettingsPage.max_seconds:
                messagebox.showerror('Error', 'Loading too many seconds')
                return
        
        for page in self.settings['plot_pages']:
            plot_title = page[0]
            tab_name = plot_title + '_tab'
            plotPage = PlotPage(self, plot_title)
            
            self.parent_notebook.add(plotPage, text=plot_title)
            SettingsPage.plot_pages.append(plotPage)
            
            plotPage.pin_num.set(page[1])
            plotPage.plot.ys = page[2]
            plotPage.plot.update()
        
        self.num_of_servos.set(new_num_servos)
        
        SettingsPage.initial_load_flag = True
    
    def outputSketch(self):
        '''
        Output all data into a usable Arduino sketch
        using jinja2 template
        '''

        # Verify all pin #s before doing anything else
        try:
            if self.btn_check_var.get():
                pin = int(self.button_entry_val.get())
            else:
                pin = self.button_entry_val.get()
        except Exception as e:
            print(e)
            messagebox.showerror('Error!', 'Bad button pin #')
            self.button_entry_val.set('None')
            return
        try:    # Checks for bad pin numberss and repeated pin numbers
            pin_nums = [int(tab.pin_num.get()) for tab in SettingsPage.plot_pages]
            if len(pin_nums) != len(set(pin_nums)):
                messagebox.showerror('Error', 'Repeated servo pin numbers')
                return
        except Exception:
            messagebox.showerror('Error', 'Check servo pin numbers')
            return
            
        # Verify no repeated names
        # Names potentially repeated when loading add'l saved servo data
        names = [page.name for page in self.plot_pages]
        if ( len(names) != len(set(names)) ):
            messagebox.showerror('Error', 'Repeated servo names')
            return
        
        # Temporary data needed for template output
        name_arr = [tab.name for tab in SettingsPage.plot_pages]
        tweener_arrays = [
            self.prettyOutput(self.inBetweeners(tab.plot.ys)) for tab in SettingsPage.plot_pages]
        pin_names = ['{}_PIN'.format(tab.name) for tab in SettingsPage.plot_pages]
        
        # Keys for template
        template_dict = {
            'list_of_names' : name_arr,
            'interval' : SettingsPage.millis,
            'tweenerArrays': tweener_arrays,
            'button' : pin,
            'pinNames' : pin_names,
            'pinNums' : pin_nums,
            'outputType' : self.output_type_var.get()}
        
        # Stuff for jinja2 template
        template_loader = jinja2.FileSystemLoader(
            searchpath=os.path.join(os.path.dirname(__file__)))
        template_env = jinja2.Environment(loader=template_loader)
        template_env.globals.update(zip=zip)
        if self.output_type_var.get() == 'i2c':
            template_index = template_env.get_template('i2c_template.txt')
        elif self.output_type_var.get() == 'pins':
            template_index = template_env.get_template('pin_template.txt')
        else:
            raise Exception
        
        file_name = fd.asksaveasfilename(
            initialdir=os.path.join(os.path.dirname(__file__)),
            defaultextension='.ino',
            title='Save Sketch',
            confirmoverwrite=True)
    
        if file_name:   # Prevents error if 'cancel' is pushed
            with open(file_name, 'w') as outFile:
                outFile.write(template_index.render(template_dict))
    
    @classmethod
    def inBetweeners(cls, arr):
        '''
        Divide raw datapoints linearly by millis interval
        for smooth servo movement 
        '''
        
        temp_arr = []
        divisor = int(500/cls.millis)
        
        for index, value in enumerate(arr):
            try:
                step = (arr[index+1] - value) / divisor
                for i in range(divisor):
                    temp_arr.append(round(value + (step*i)))
            except IndexError:
                temp_arr.append(value)
        
        return temp_arr
    
    def saveData(self):
        '''Save relevent info to file for later use'''
    
        try:
            info_dict = {
                         'seconds' : self.num_of_seconds.get(),
                         'plot_pages' : [],
                         'button_#' : self.button_entry_val.get(),
                         'output_type': self.output_type_var.get()
                        }
        
            for page in self.plot_pages:
                temp = []
                temp.append(page.name)
                temp.append(page.pin_num.get())
                temp.append(page.plot.ys)
            
                info_dict['plot_pages'].append(temp)
            
            file_name = fd.asksaveasfilename(
                initialdir=os.path.join(os.path.dirname(__file__)),
                defaultextension='.servo',
                title='Save Settings',
                confirmoverwrite=True)
            
            if file_name:   # Prevents error if dialog canceled
                with open(file_name, 'wb') as writer:
                    dill.dump(info_dict, writer)
            
        except Exception as e:
            print('Error saving...')
            print(e)

    def loadData(self):
        '''Loads all data from a previous session'''
        
        file_name = fd.askopenfilename(
                initialdir=os.path.join(os.path.dirname(__file__)),
                defaultextension='.servo',
                title='Load Settings')
            
        if file_name:
            SettingsPage.load_flag = True
            
            with open(file_name, 'rb') as reader:
                self.settings = dill.load(reader)
            
            self.generatePlots()
            
            del self.settings
    
    @staticmethod
    def constrain(n, n_min, n_max):
        '''Constrain value n between a min and max'''
        
        return max(min(n, n_max), n_min)
                
    @staticmethod
    def prettyOutput(arr):
        '''Outputs the plot values array in more human readable form'''
    
        tmp_str = ''
        for index, num in enumerate(arr):
            if (index+1) % 10 != 0:
                tmp_str += '{}, '.format(num).rjust(5)
            else:
                tmp_str += '{},\n'.format(num).rjust(5)
        return tmp_str 

    
class PlotPage(ttk.Frame):
    '''Tab containing interactive plot'''
    
    total_pages = 0
    
    def __init__(self, parent, name):
        super().__init__()
        
        PlotPage.total_pages += 1
        
        self.plot_num = PlotPage.total_pages
        self.parent = parent
        self.name = name    # Child plot uses this for title

        self.buildPage()
    
    def buildPage(self):
        '''Layout widgets for the tab'''
        
        self.pin_num = tk.IntVar()
        
        # To scroll along the plot
        # Needs to be created before Plot
        # Upper limit is seconds minus half the length of the plot 'x_window'
        self.slider = ttk.Scale(self, orient=tk.HORIZONTAL,
            to=self.parent.num_of_seconds.get()-10,
            length=self.parent.parent_notebook.winfo_width())
        
        
        # ----- Matplotlib Plot -----
        
        # Plot instance, bound to tab instance
        self.plot = Plot(self, self.parent.num_of_seconds.get(), self.plot_num)
        
        # Drawing area for the graph
        self.canvas = FigureCanvasTkAgg(self.plot.fig, master=self)
        # Bind mouse events to self.canvas to change data
        self.canvas.mpl_connect('pick_event', self.plot.onNodeClick)
        self.canvas.mpl_connect('button_release_event', self.plot.onRelease)
        self.canvas.mpl_connect('motion_notify_event', self.plot.onMotion)
        
        self.canvas.mpl_connect('button_press_event', self.plot.onClick)
        self.canvas.mpl_connect('key_release_event', self.plot.onDelKey)
        
        # Need to create SpanSelector widget after canvas is created
        self.plot.span = self.plot.createSpanSelector()
        
        # ----- End of Matplotlib plot -----
        
        
        pin_assign_frame = ttk.Frame(self, padding=10)
        pin_label = ttk.Label(pin_assign_frame, text='Pin # or address: ')
        self.pin_entry = ttk.Entry(
            pin_assign_frame,
            width=5,
            justify=tk.RIGHT,
            textvariable=self.pin_num)
       
        button_frame = ttk.Frame(self, padding=10) 
            
        self.settings_button = ttk.Button(button_frame, text='Settings',
            command=self.settingsDisplay)
        
        # Grid widgets into tab
        self.canvas.get_tk_widget().grid(columnspan=3)
        self.slider.grid(columnspan=3)
        
        pin_assign_frame.grid(sticky=tk.W)
        pin_label.grid()
        self.pin_entry.grid(row=0, column=1)
        
        button_frame.grid(row=2, column=2, sticky=tk.E)
        
        self.settings_button.pack(padx=5, side=tk.RIGHT)

    def settingsDisplay(self):
        '''Add settings tabs to empty settings popup'''
        
        #~ popup = SettingsPopup(self)
        tab, values = SettingsPopup(self).show()
        print(tab, values)
        
        if tab == 'NamePage':
            name = values
            
            for page in self.parent.plot_pages:
                if name == page.name:
                    messagebox.showerror('Error!', 'Names must be unique')
                    return
                    
                # Change text on tab
                index = self.parent.plot_pages.index(self) + 1
                self.parent.parent_notebook.tab(index, text=name)
                # Change title on plot
                self.name = name
                self.plot.update()
            
        if tab == 'LimitPage':
            pass
        

class Plot():
    '''
    A container for holding variables and methods needed for 
    animating the interactive plot, is a child of a PlotPage object
    '''
    
    def __init__(self, parent, seconds, num):
        self.parent = parent
        self.scale = self.parent.slider
        self.scale['command'] = self.updatePos
        
        self.scale_pos = 0
        self.num = num                 # Which number servo, for plot title
        self.length = (seconds*2)+1    # Number of nodes in plot, 2 per second
        
        self.node_clicked = False       # Node follows mouse only when clicked
        self.point_index = None        # Track which node has been selected
        
        # For keeping values within range of servo degrees
        self.upper_limit = 179
        self.lower_limit = 0
        self.limit_range = lambda n: max(min(self.upper_limit, n), self.lower_limit)
        
        # Initial Graph -----
        self.fig = Figure(figsize=(10,5), dpi=100)
        self.fig.subplots_adjust(bottom=0.18)
        self.ax = self.fig.add_subplot(111)
        
        self.xs = [i for i in range(self.length)]
        self.ys = [self.parent.parent.node_default_val for i in self.xs]
        
        # To hold values from span selector
        self.span_xs = []
        self.selection = False
        
        
        self.setPlot()
        self.drawPlot()
       
    def updatePos(self, *args):
        '''Read the scale to move plot viewing area,
           args are a tuple of scale value automatically passed in'''
           
        self.scale_pos = self.scale.get()
        self.update()
    
    def setPlot(self):
        '''Elements of the plot which do not need to be redrawn every update '''
        
        self.ax.set_ylim([-10,190])
        self.ax.set_yticks(range(0,190,20))
        
        self.ax.grid(alpha=.5)
        self.ax.set_xlabel('Seconds')
        self.ax.set_ylabel('Degree of Motion', fontname='BPG Courier GPL&GNU',
            fontsize=14)
        
    def clearPlotLines(self):
        '''Remove plotted lines so they can be redrawn'''
        
        self.line.remove()
        self.nodes.remove()
        self.upper.remove()
        self.lower.remove()
       
    def drawPlot(self):
        '''Draw the actual plot'''
        
        self.ax.set_title(label=self.parent.name, fontsize=18, y=1.03)
        
        x_window = 20                   # Num of ticks in 'viewport'
        pos = round(self.scale_pos*2)   # scale_pos is in seconds, pos is in ticks
        pos = max(pos, 0)               
        
        # Confine y-values to within upper and lower limits
        self.ys = [self.limit_range(node) for node in self.ys]
        
        # Only 'x_window' of plot is viewable
        self.ax.set_xlim([pos-.5, pos+x_window+.5])
        self.ax.set_xticks([i for i in range(pos, pos+x_window+1)])
        self.ax.set_xticklabels([i/2 for i in self.ax.get_xticks()])
        for tick in self.ax.get_xticklabels():
            tick.set_rotation(45)
        
        #~ # Plot upper and lower limits
        self.upper, = self.ax.plot(self.xs, [self.upper_limit for i in self.xs],
            'k--', alpha=.6, linewidth=1)
        self.lower, = self.ax.plot(self.xs, [self.lower_limit for i in self.xs],
            'k--', alpha=.6, linewidth=1)
        
        # Line
        self.line, = self.ax.plot(self.xs, self.ys, color='orange',
            markersize=10)
            
        # Clickable nodes
        self.nodes, = self.ax.plot(self.xs, self.ys, 'k.', 
            markersize=10, picker=5.0)
   
    def createSpanSelector(self):
        '''Creates span selector widget'''
    
        return SpanSelector(self.ax, self.spanSelect, 'horizontal',
                    useblit=True, span_stays=False, button=1, minspan=.05,
                    rectprops=dict(alpha=0.50, facecolor='lightskyblue'))
    
    def onNodeClick(self, event):
        '''Which node has been clicked'''
        
        #~ point = event.artist
        index = event.ind
        
        self.point_index = int(index[0])
        
        # Single-click
        if not event.mouseevent.dblclick:
            self.node_clicked = True
            
        # Double-click
        else:
            self.span.active = False
            # If node is double-clicked open popup to change value
            sleep(.1)  # Needs short delay

            current_val = self.ys[self.point_index]
            new_val, ok_cancel = ValuePopup(current_val).show()
            
            # If 'ok button' closed ValuePopup
            if ok_cancel:
                # Update app points in highlight to value from ValuePopup
                if self.selection:
                    for xp in self.span_xs:
                        selected_index = self.xs.index(xp)
                        self.ys[selected_index] = new_val
                else:
                    self.ys[self.point_index] = new_val
            
                self.update()
    
    def spanSelect(self, x_min, x_max):
        '''Callback for span selector'''
        
        constrain = lambda n, n_min, n_max: max(min(n, n_max), n_min)
        
        xmin = constrain(ceil(x_min), 0, len(self.xs))
        xmax = constrain(ceil(x_max), 0, len(self.xs))
        
        selected_xs = self.xs[xmin:xmax]
        selected_ys = self.ys[xmin:xmax]
        
        if len(selected_xs) <= 1:
            self.span_xs = []
            return
        
        # Store selected points into lists
        self.span_xs = selected_xs
        
        # Create rectangle that remains, hightlighting selection
        self.highlight_rect = Rectangle((x_min, -10), width=(x_max-x_min),
            height=200, angle=0, **dict(alpha=0.35, facecolor='lightskyblue'))
        self.ax.add_patch(self.highlight_rect)
        self.selection = True
            
    def onClick(self, event):
        '''Mouse click makes span select go away,
           resets selection arrays'''
        
        # Some events cause canvas to lose focus, causing missed events
        # Bring focus back to canvas 
        self.parent.canvas._tkcanvas.focus_set()
        
        if event.button == 1:
            # If moving a node, deactivate spanselector
            if self.node_clicked:
                self.span.active= False
                
                if self.selection:
                    # Del highlight rect if selected node is not highlighted
                    if self.point_index not in self.span_xs:
                        self.removeHighlight()
                
            # Del highlight rect when anything non-node is clicked    
            elif not self.node_clicked:
                self.removeHighlight()
                
        elif event.button == 3:
            self.removeHighlight()
        
    def onMotion(self, event):
        '''Mouse can drag nodes'''
        
        if self.node_clicked and event.inaxes:
            prev_y_value = self.ys[self.point_index]
            
            # Point follows mouse on y-axis
            self.ys[self.point_index] = int(round(self.limit_range(event.ydata)))
            node_diff = (self.ys[self.point_index] - prev_y_value)
            
            # Update highlighted point lists
            if self.selection:
                
                #~ print('node index', self.point_index)
                for xp in self.span_xs:
                    if xp != self.point_index:
                        self.ys[xp] += node_diff
            
            self.update()
    
    def onRelease(self, event):
        # Spanselector deactivates on certain mouse events,
        # Any button release reactivates it
        self.span.active = True
        
        if self.point_index is not None:
            self.node_clicked = False
            self.point_index = None
    
    def removeHighlight(self):
        '''Removes highlight rect from plot'''
        
        if self.selection:
            self.highlight_rect.remove()
            delattr(self, 'highlight_rect')
            
            self.span_xs = []
            self.selection = False
            
            self.update()
    
    def onDelKey(self, event):
        '''Deletes selected nodes and adds same number of nodes at the default
           value to the end, to maintain routine length '''
           
        if self.selection and event.key=='delete':
            answer = messagebox.askyesno('Delete Nodes',
                message='Delete nodes?')
                
            if answer:
                # Delete selected nodes
                del self.xs[self.span_xs[0]: self.span_xs[-1]+1]
                del self.ys[self.span_xs[0]: self.span_xs[-1]+1]
                
                # Add default nodes to end to maintain routine length
                self.xs += [0 for i in self.span_xs]
                self.ys += [self.parent.parent.node_default_val for i in self.span_xs]
                # Re-number xs
                self.xs = [index for index, val in enumerate(self.xs)]
                
                self.removeHighlight()
                
                self.update()
        
    def update(self):
        '''Re-draw plot after moving a point'''

        self.clearPlotLines()
        
        self.drawPlot()
        self.fig.canvas.draw()
        
    
    
    

WIDTH = 1000
HEIGHT = 600

if __name__ == '__main__':
    
    app = MainApp(WIDTH, HEIGHT)
    
    
    
    
