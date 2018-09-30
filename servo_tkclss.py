
import jinja2

from matplotlib import use as Use
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

import os
import time

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as fd
from tkinter import messagebox
from tkinter.ttk import Notebook

from servo_popups import *

import dill


# Needed to embed matplotlib in tkinter
Use('TkAgg')


class MainApp():
    def __init__(self, template_file, width=800, height=600):
        
        self.template_file = template_file
        
        self.main = tk.Tk()
        self.main.title('Servo Programmer')
        self.main.geometry('{}x{}'.format(width, height))
        self.main.resizable(False, False)
        self.main.update()
        
        # Set ttk style
        self.main.style = ttk.Style()
        self.main.style.theme_use('clam')
        
        self.buildPage()
        
    def buildPage(self):
        # ----- Meubar configuration -----
        menubar = tk.Menu(self.main)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label='Open', command=None)
        file_menu.add_command(label='Quit', command=self.main.destroy)
        
        about_menu = tk.Menu(self.main, tearoff=0)
        about_menu.add_command(label='About', command=lambda: AboutPopup())
        
        menubar.add_cascade(label='File', menu=file_menu)
        menubar.add_cascade(label='Help', menu=about_menu)
        
        # Add menubar to main window
        self.main.config(menu=menubar)
        
        # ----- Notebook/tab configuration -----    
        notebook = Notebook(self.main, width=self.main.winfo_width(),
            height=self.main.winfo_height())
        
        # Initial tab -----
        settings_tab = SettingsPage(notebook, self.template_file)
        notebook.add(settings_tab, text='Settings')
        
        notebook.pack(anchor=tk.CENTER, fill=tk.BOTH)
        

class SettingsPage(ttk.Frame):
    '''First tab w/ settings'''

    plot_pages = []    # Used when outputting data
    millis = 15        # Delay between each inBetweener value
    
    def __init__(self, parent_notebook, template_file):
        super().__init__()
        
        SettingsPage.template_file = template_file  # For outputting sketch
        SettingsPage.parent_notebook = parent_notebook

        self.buildPage()
        
    def buildPage(self):
        '''Layout widgets for the tab'''
        
        # --- Left side Frame ---
        left = ttk.Frame(self)
        left.pack(side=tk.LEFT, anchor=tk.N)
        
        l_title = ttk.Label(left, text='Settings', font=(None, 25))
        l_title.grid(columnspan=5, pady=20)
                
        seconds_label = ttk.Label(left, text='Routine length (in seconds)\
            \n(1-360):')
        seconds_label.grid(padx=10, pady=15)
        
        SettingsPage.num_of_seconds = tk.IntVar()
        self.seconds_entry = ttk.Entry(left, width=5, justify=tk.RIGHT,
            textvariable = SettingsPage.num_of_seconds)
        self.seconds_entry.grid(padx=25, pady=15, row=1, column=1)
        
        
        servo_total_label = ttk.Label(left, text='Number of servos (1-8)')
        servo_total_label.grid(padx=10, pady=15)
        
        SettingsPage.num_of_servos = tk.IntVar()
        self.servo_total_entry = ttk.Entry(left, width=5, justify=tk.RIGHT,
            textvariable = SettingsPage.num_of_servos)
        self.servo_total_entry.grid(padx=25, pady=15, row=2, column=1)
        
        
        self.generate_plots = ttk.Button(left, text='Generate Plots',
            command=self.generatePlots)
        self.generate_plots.grid(padx=25, pady=25, row=1, column=2,
            rowspan=2)
        
        button_label = ttk.Label(left, text='Pin # of button')
        button_label.grid(padx=10, pady=15)
        
        SettingsPage.button_num = tk.IntVar()
        button_entry = ttk.Entry(left, width=5, justify=tk.RIGHT,
            textvariable=SettingsPage.button_num)
        button_entry.grid(padx=25, pady=15, row=3, column=1)
        
        
        # --- Right side Frame ---
        right = ttk.Frame(self)
        right.pack(anchor=tk.CENTER)
        
        r_title = ttk.Label(right, text='Output', font=(None, 25))
        r_title.grid(columnspan=5, pady=20)
        
        self.output_button = ttk.Button(right, text='Output Sketch', width=15,
            state='disabled', command=self.outputSketch)
        self.output_button.grid(padx=10, pady=50)
        
        save_button = ttk.Button(right, text='Save', command=SettingsPage.saver)
        save_button.grid()

        load_button = ttk.Button(
            right,
            text='Load',
            command=lambda: SettingsPage.loader(self))
        load_button.grid()



        ### TESTING
        btn = ttk.Button(
            right,
            text='print info',
            command=SettingsPage.printStuff)
        btn.grid()
        #####


        self.resetEntries()
    
    # TESTING
    @classmethod
    def printStuff(cls):
        print()
        print('Button num: {}'.format(cls.button_num.get()))
        print('Length (sec) :', cls.num_of_seconds.get())
        print('Pages:')
        for page in cls.plot_pages:
           print('Name: ', page.name)
           print('Pin num: ', page.pin_num.get())
           print('Y-value list: ', page.plot.ys)
           print()
           
            
    
    
    @classmethod
    def resetEntries(cls):
        '''Clear the entry widgets'''
        
        cls.num_of_seconds.set(1)
        cls.num_of_servos.set(1)
        cls.button_num.set(0)
        
    def generatePlots(self):
        '''
        Generate specified number of Plot tabs each containing a plot
        of the specified routine length
        '''
        
        try:
            limit = lambda n, n_min, n_max: max(min(n, n_max), n_min)
            
            # Routine between 1 and 360 seconds
            temp_secs= SettingsPage.num_of_seconds.get()
            SettingsPage.num_of_seconds.set(limit(temp_secs, 1, 360))
            
            # Maximum of 8 servos
            temp_servos = SettingsPage.num_of_servos.get()
            SettingsPage.num_of_servos.set(limit(temp_servos, 1, 8))
            
            if (SettingsPage.num_of_servos.get() * \
                    SettingsPage.num_of_seconds.get()) >= 360:
                self.resetEntries()
                messagebox.showerror('Limit Error', 'Total routine length must \
                    be less than 6 minutes (360 seconds)')
                return
            
        except Exception as e:
            print(e)
            messagebox.showerror(title='Error!', message='Inputs must be numbers')
            self.resetEntries()
            
        else:
            # Generate tabs/plots
            for i in range(self.num_of_servos.get()):
                tab_name = 'Servo{}'.format(i+1)
                tab = 'self.{}_tab'.format(tab_name)
                tab = PlotPage(self, tab_name)
                SettingsPage.parent_notebook.add(tab, text=tab_name)
                SettingsPage.plot_pages.append(tab)
            
            self.generate_plots.configure(state='disabled')
            self.seconds_entry.configure(state='disabled')
            self.servo_total_entry.configure(state='disabled')
            self.output_button['state'] = 'normal'
    
    def outputSketch(self):
        '''
        Output all data into a usable Arduino sketch
        using jinja2 template
        '''

         # Verify all pin #s before doing anything else
        try:
            pin = self.button_num.get()
        except Exception:
            messagebox.showerror('Error!', 'Bad button pin #')
            self.button_num.set('')
            return
        
        # Temporary data needed for template output
        name_arr = [tab.name for tab in SettingsPage.plot_pages]
        tweener_arrays = [
            prettyOutput(self.inBetweeners(tab.plot.ys)) for tab in SettingsPage.plot_pages]
        pin_names = ['{}_PIN'.format(tab.name) for tab in SettingsPage.plot_pages]
        try:    # Each servo must have pin number assigned
            pin_nums = [int(tab.pin_num.get()) for tab in SettingsPage.plot_pages]
            if len(pin_nums) != len(set(pin_nums)):
                raise ValueError
        except ValueError:
            messagebox.showerror('Error', 'Check servo pin numbers')
            return
        
        # Stuff for jinja2 template
        template_loader = jinja2.FileSystemLoader(
            searchpath=os.path.join(os.path.dirname(__file__)))
        template_env = jinja2.Environment(loader=template_loader)
        template_env.globals.update(zip=zip)
        template_index = template_env.get_template(SettingsPage.template_file)
        
        # Keys for template
        template_dict = {
            'list_of_names' : name_arr,
            'interval' : SettingsPage.millis,
            'tweenerArrays': tweener_arrays,
            'button' : pin,
            'pinNames' : pin_names,
            'pinNums' : pin_nums}
    
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
    
    @classmethod
    def saver(cls):
        '''Save relevent info to file for later use'''
    
        try:
            info_dict = {
                         'seconds' : cls.num_of_seconds.get(),
                         'plot_pages' : [],
                         'button_#' : cls.button_num.get()
                        }
        
            for page in cls.plot_pages:
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
            
            if file_name:   # Prevents error if cancel pressed
                with open(file_name, 'wb') as writer:
                    dill.dump(info_dict, writer)
            
            #~ for k, v in info_dict.items():
                #~ print(k, ':', v)
        
        except Exception as e:
            print('some error')
            print(e)

    @classmethod
    def loader(cls, self):
        '''Loads data from previous save'''
        
        file_name = fd.askopenfilename(
                initialdir=os.path.join(os.path.dirname(__file__)),
                defaultextension='.servo',
                title='Load Settings')
            
        if file_name:
            with open(file_name, 'rb') as reader:
                settings = dill.load(reader)
            
            # Apply loaded data to current app
            cls.button_num.set(settings['button_#'])
            cls.num_of_seconds.set(settings['seconds'])
            cls.num_of_servos.set(len(settings['plot_pages']))
            
            cls.generatePlots(self)
            
            temp_page_list = settings['plot_pages']
            for index, page in enumerate(cls.plot_pages):
                page.name = temp_page_list[index][0]
                page.pin_num.set(temp_page_list[index][1])
                page.plot.ys = temp_page_list[index][2]
                page.plot.update()
                page.parent.parent_notebook.tab(index+1, text=page.name)
                
    
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
        
        # To scroll along the plot
        # Upper limit is seconds - half the length of the viewport of the plot
        slider = ttk.Scale(self, orient=tk.HORIZONTAL,
            to=self.parent.num_of_seconds.get()-10,
            length=self.parent.parent_notebook.winfo_width())
        
        # Plot instance, bound to tab instance
        self.plot = Plot(self, self.parent.num_of_seconds.get(), slider,
            self.plot_num)
        
        # Drawing area for the graph
        canvas = FigureCanvasTkAgg(self.plot.fig, master=self)
        # Bind mouse events to canvas to change data
        canvas.mpl_connect('pick_event', self.plot.onPress)
        canvas.mpl_connect('button_release_event', self.plot.onRelease)
        canvas.mpl_connect('motion_notify_event', self.plot.onMotion)
        
        pin_assign_frame = ttk.Frame(self, padding=10)
        pin_label = ttk.Label(pin_assign_frame, text='Pin # or address: ')
        self.pin_num = tk.IntVar()
        self.pin_entry = ttk.Entry(
            pin_assign_frame,
            width=5,
            justify=tk.RIGHT,
            textvariable=self.pin_num)
        
        self.rename_button = ttk.Button(self, text='Change servo name',
            command=self.changeName)
        
        # Grid widgets into tab
        canvas.get_tk_widget().grid(columnspan=3)
        slider.grid(columnspan=3)
        
        pin_assign_frame.grid(sticky=tk.W)
        pin_label.grid()
        self.pin_entry.grid(row=0, column=1)
        self.rename_button.grid(row=2, column=2, padx=10, pady=10, sticky=tk.E)

    def changeName(self):
        '''Change plot title name and tab text'''
        
        self.rename_button['state'] = 'disabled'
        
        NamePopup(self)
        
        self.rename_button['state'] = 'normal'
  
  
class Plot():
    '''
    A container for holding variables and methods needed for 
    animating the interactive plot, is a child of a PlotPage object
    '''
    
    def __init__(self, parent, seconds, scale, num):
        self.parent = parent
        self.scale = scale
        self.scale['command'] = self.updatePos
        
        self.scale_pos = 0
        self.num = num                 # Which number servo, for plot title
        self.length = (seconds*2)+1    # Number of nodes in plot, 2 per second
        
        self.click = False             # Node follows mouse only when clicked
        self.point_index = None        # Track which node has been selected
        
        # For keeping values within range of servo degrees
        upper_limit = 180
        lower_limit = 0
        self.limit_range = lambda n: max(min(upper_limit, n), lower_limit)
        
        # Initial Graph -----
        self.fig = Figure(figsize=(10,5), dpi=100)
        self.fig.subplots_adjust(bottom=0.18)
        self.ax = self.fig.add_subplot(111)
        
        self.xs = [i for i in range(self.length)]
        self.ys = [0 for i in self.xs]
        
        self.drawPlot()
       
    def updatePos(self, *args):
        '''Read the scale to move plot viewing area'''
        self.scale_pos = self.scale.get()
        self.update()
       
    def drawPlot(self):
        '''Draw the actual plot'''
        
        x_window = 20                   # Num of ticks in 'viewport'
        pos = round(self.scale_pos*2)   # scale_pos is in seconds, pos is in ticks
        pos = max(pos, 0)               
        
        # Only 'x_window' of plot is viewable
        self.ax.set_xlim([pos-.5, pos+x_window+.5])
        self.ax.set_xticks([i for i in range(pos, pos+x_window+1)])
        self.ax.set_xticklabels([i/2 for i in self.ax.get_xticks()])
        if self.length > 201:
            for tick in self.ax.get_xticklabels():
                tick.set_rotation(45)
        
        self.ax.set_ylim([-10,190])
        self.ax.set_yticks(range(0,190,20))
        
        self.ax.grid(alpha=.5)
        self.ax.set_title(label=self.parent.name)
        self.ax.set_xlabel('Seconds')
        self.ax.set_ylabel('Degree of Motion', fontname='BPG Courier GPL&GNU', fontsize=18)
        
        # Plot line
        self.line, = self.ax.plot(self.xs, self.ys, color='orange',
            markersize=10)
            
        # Plot clickable nodes
        self.line2, = self.ax.plot(self.xs, self.ys, 'k.', 
            markersize=10, picker=5.0)
        
    def onPress(self, event):
        '''Which node has been clicked'''
        
        point = event.artist
        index = event.ind
        
        self.point_index = int(index[0])
        
        if not event.mouseevent.dblclick:
            self.click = True
        
        else:
            # If node is double-clicked open popup to change value
            time.sleep(.1)  # Needs short delay to end all events on mainloop
            ValuePopup(self, self.point_index)
        
    def onMotion(self, event):
        if self.click and event.inaxes:
            # Point follows mouse on y-axis
            self.ys[self.point_index] = self.limit_range(event.ydata)
            # Round to nearest whole degree
            self.ys[self.point_index] = int(round(self.ys[self.point_index]))
            
            self.update()
    
    def onRelease(self, event):
        if self.point_index is not None:
            self.click = False
            self.point_index = None
    
    def update(self):
        '''Re-draw plot after moving a point'''
        self.ax.clear()
        self.drawPlot()
        self.fig.canvas.draw()        
        

def prettyOutput(arr):
    '''Outputs the plot values array in more human readable form'''
    
    tmp_str = ''
    for index, num in enumerate(arr):
        if (index+1) % 10 != 0:
            tmp_str += '{}, '.format(num).rjust(5)
        else:
            tmp_str += '{},\n'.format(num).rjust(5)
    return tmp_str 



    



WIDTH = 1000
HEIGHT = 600
TEMPLATE_FILE = 'pin_template.txt'

if __name__ == '__main__':
    
    app = MainApp(TEMPLATE_FILE, WIDTH, HEIGHT)
    app.main.mainloop()
    
    
    
    
