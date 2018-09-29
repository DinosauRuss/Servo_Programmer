
import jinja2

from matplotlib import use as Use
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as fd
from tkinter import messagebox
from tkinter.ttk import Notebook

import time

from servo_popups import *


# Needed to embed matplotlib in tkinter
Use('TkAgg')


class SettingsPage(ttk.Frame):
    '''First tab w/ settings'''
    
    def __init__(self, parent_notebook, primary_tk_window, template_file):
        super().__init__()
        
        self.parent_notebook = parent_notebook
        self.primary_tk_window = primary_tk_window  # Only needed to pass down to PlotPage
        self.template_file = template_file          # For outputting sketch
        
        self.num_of_seconds = 0
        self.num_of_sevos = 0
        self.plot_pages = []    # Used when outputting data
        self.millis = 15        # Delay between each inBetweener value
        
        self.buildPage()
        
    def buildPage(self):
        '''Layout widgets for the tab'''
        
        title = ttk.Label(self, text='Settings Page', font=(None, 25))
        title.grid(columnspan=5, pady=20)
                
        seconds_label = ttk.Label(self, text='Routine length (in seconds)\
            \n(1-360):')
        seconds_label.grid(padx=10, pady=15)
        
        self.seconds_entry = ttk.Entry(self, width=5, justify=tk.RIGHT)
        self.seconds_entry.grid(padx=25, pady=15, row=1, column=1)
        
        servo_total_label = ttk.Label(self, text='Number of servos (1-8)')
        servo_total_label.grid(padx=10, pady=15)
        
        self.servo_total_entry = ttk.Entry(self, width=5, justify=tk.RIGHT)
        self.servo_total_entry.grid(padx=25, pady=15, row=2, column=1)
        
        self.generate_plots = ttk.Button(self, text='Generate Plots',
            command=self.generatePlots)
        self.generate_plots.grid(padx=25, pady=25, row=1, column=2,
            rowspan=2)
        
        button_label = ttk.Label(self, text='Pin # of button')
        button_label.grid(padx=10, pady=15)
        
        self.button_entry = ttk.Entry(self, width=5, justify=tk.RIGHT)
        self.button_entry.grid(padx=25, pady=15, row=3, column=1)
        
        self.output_button = ttk.Button(self, text='Output Data', width=15,
            state='disabled', command=self.outputSketch)
        self.output_button.grid(padx=10, pady=50)

        self.resetEntries()

    def resetEntries(self):
        '''Clear the entry widgets'''
        
        self.seconds_entry.delete(0, tk.END)
        self.servo_total_entry.delete(0, tk.END)
        
        # Default values
        self.seconds_entry.insert(0, 1)
        self.servo_total_entry.insert(0, 1)

    def generatePlots(self):
        '''
        Generate specified number of Plot tabs each containing a plot
        of the specified routine length
        '''
        
        try:
            limit = lambda n, n_min, n_max: max(min(n, n_max), n_min)
            
            # Routine between 1 and 600 seconds
            self.num_of_seconds = int(self.seconds_entry.get())
            self.num_of_seconds = limit(self.num_of_seconds, 1, 360)
            
            # Maximum of 8 servos
            self.num_of_servos = int(self.servo_total_entry.get())
            self.num_of_servos = limit(self.num_of_servos, 1, 8)
            
            if (self.num_of_servos * self.num_of_seconds) > 360:
                messagebox.showerror('Limit Error', 'Total routine length must \
                    be less than 6 minutes (360 seconds)')
                self.resetEntries()
                return
            
        except Exception as e:
            print(e)
            messagebox.showerror(title='Error!', message='Inputs must be numbers')
            self.resetEntries()
            
        else:
            # Generate tabs/plots
            for i in range(self.num_of_servos):
                tab_name = 'Servo{}'.format(i+1)
                tab = 'self.{}_tab'.format(tab_name)
                tab = PlotPage(self.primary_tk_window, self.parent_notebook,
                    self, tab_name, self.num_of_seconds)
                self.parent_notebook.add(tab, text=tab_name)
                self.plot_pages.append(tab)
            
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
            pin = int(self.button_entry.get())
        except ValueError:
            messagebox.showerror('Error!', 'Bad button pin #')
            self.button_entry.delete(0, tk.END)
            return
        
        # Temporary data needed for template output
        name_arr = [tab.name for tab in self.plot_pages]
        tweener_arrays = [
            prettyOutput(self.inBetweeners(tab.plot.ys)) for tab in self.plot_pages]
        pin_names = ['{}_PIN'.format(tab.name) for tab in self.plot_pages]
        try:    # Each servo must have pin number assigned
            pin_nums = [int(tab.pin_entry.get()) for tab in self.plot_pages]
            if len(pin_nums) != len(set(pin_nums)):
                raise ValueError
        except ValueError:
            messagebox.showerror('Error', 'Check servo pin numbers')
            return
        
        # Stuff for jinja2 template
        template_loader = jinja2.FileSystemLoader(searchpath='./')
        template_env = jinja2.Environment(loader=template_loader)
        template_env.globals.update(zip=zip)
        template_index = template_env.get_template(self.template_file)
        
        # Keys for template
        template_dict = {
            'list_of_names' : name_arr,
            'interval' : self.millis,
            'tweenerArrays': tweener_arrays,
            'button' : pin,
            'pinNames' : pin_names,
            'pinNums' : pin_nums}
    
        file_name = fd.asksaveasfilename(defaultextension='.ino',\
            title='Save Servo Settings', confirmoverwrite=True)
    
        if file_name:   # Prevents error if 'cancel' is pushed
            with open(file_name, 'w') as outFile:
                outFile.write(template_index.render(template_dict))

    
    def inBetweeners(self, arr):
        '''
        Divide raw datapoints evenly by millis interval
        for smooth servo movement 
        '''
        
        temp_arr = []
        divisor = int(500/self.millis)
        
        for index, value in enumerate(arr):
            try:
                step = (arr[index+1] - value) / divisor
                for i in range(divisor):
                    temp_arr.append(round(value + (step*i)))
            except IndexError:
                temp_arr.append(value)
        
        return temp_arr
    
    
class PlotPage(ttk.Frame):
    '''Tab containing interactive plot'''
    
    total_pages = 0
    
    def __init__(self, primary_tk_window, parent_notebook, parent, name, seconds):
        super().__init__()
        
        PlotPage.total_pages += 1
        
        self.plot_num = PlotPage.total_pages
        self.primary_tk_window = primary_tk_window
        self.parent_notebook = parent_notebook
        self.parent = parent
        self.name = name
        self.num_of_seconds = seconds

        self.plot = None
        self.pin_entry = None
        
        self.buildPage()
    
    def buildPage(self):
        '''Layout widgets for the tab'''
        
        # To scroll along the plot
        # Upper limit is seconds - half the length of the viewport of the plot
        slider = ttk.Scale(self, orient=tk.HORIZONTAL, to=self.num_of_seconds-10,
            length=self.primary_tk_window.winfo_width())
        
        # Plot class instance, bound to tab instance
        self.plot = Plot(self, self.num_of_seconds, slider, self.plot_num)
        
        # Drawing area for the graph
        canvas = FigureCanvasTkAgg(self.plot.fig, master=self)
        # Bind mouse events to canvas to change data
        canvas.mpl_connect('pick_event', self.plot.onPress)
        canvas.mpl_connect('button_release_event', self.plot.onRelease)
        canvas.mpl_connect('motion_notify_event', self.plot.onMotion)
        
        pin_assign_frame = ttk.Frame(self, padding=10)
        pin_label = ttk.Label(pin_assign_frame, text='Pin # or address: ')
        self.pin_entry = ttk.Entry(pin_assign_frame, width=5, justify=tk.RIGHT)
        
        self.rename_button = ttk.Button(self, text='Change servo name', command=self.changeName)
        
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
        
        NamePopup(self, self.primary_tk_window)
        
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
        self.num = num                      # Which number servo, for plot title
        self.seconds = seconds              # Needed to limit scale for plot window
        self.length = (self.seconds*2)+1    # Number of nodes in plot, 2 per second
        
        self.click = False                  # Node follows mouse only when clicked
        self.point_index = None             # Track which node has been selected
        
        # For keeping values within range of servo degrees
        self.limit_range = lambda n: max(min(180, n), 0)
        
        # Initial Graph -----
        self.fig = Figure(figsize=(10,5), dpi=100)
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
        
        print('double', event.mouseevent.dblclick)
        
        point = event.artist
        index = event.ind
        
        self.point_index = int(index[0])
        
        if not event.mouseevent.dblclick:
            self.click = True
        
        else:
            # If node is double-clicked open popup to change value
            time.sleep(.1)  # Needs short delay to end all events on mainloop
            ValuePopup(self.parent.primary_tk_window)
        
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

main = tk.Tk()
main.title('Servo Programmer')
main.geometry('{}x{}'.format(WIDTH, HEIGHT))
main.resizable(False, False)
main.update()

# Set ttk style
main.style = ttk.Style()
main.style.theme_use('clam')


# ----- Meubar configuration -----
menubar = tk.Menu(main)

file_menu = tk.Menu(menubar, tearoff=0)
file_menu.add_command(label='Open', command=None)
file_menu.add_command(label='Quit', command=main.destroy)

about_menu = tk.Menu(main, tearoff=0)
#~ about_menu.add_command(label='About',
    #~ command=lambda: messagebox.showinfo('About', 'Made by REK'))
about_menu.add_command(label='About', command=aboutMenu)

menubar.add_cascade(label='File', menu=file_menu)
menubar.add_cascade(label='Help', menu=about_menu)

# Add menubar to main window
main.config(menu=menubar)


# ----- Notebook/tab configuration -----    
notebook = Notebook(main, width=WIDTH, height=HEIGHT)

# Initial tab -----
#~ settings_tab = SettingsPage(notebook)
settings_tab = SettingsPage(notebook, main, TEMPLATE_FILE)
notebook.add(settings_tab, text='Settings')

notebook.pack(anchor=tk.CENTER, fill=tk.BOTH)



main.mainloop()

