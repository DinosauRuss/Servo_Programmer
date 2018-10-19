
import dill
import jinja2
import os
import serial
import traceback

from matplotlib import use as Use
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.pyplot import pause

from PIL import Image, ImageTk

from time import sleep

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as fd
from tkinter import messagebox

from servo_popups import *
from settings_popup import *


# Needed to embed matplotlib in tkinter
Use('TkAgg')


class MainApp():
    def __init__(self, width=800, height=600):
        
        self.main = tk.Tk()
        self.main.title('Servo Input Recorder')
        self.main.geometry('{}x{}'.format(width, height))
        self.main.resizable(False, False)
        self.main.update()
        
        # Set ttk style
        self.main.style = ttk.Style()
        self.main.style.theme_use('clam')
        
        self.buildPage()
        
        self.main.protocol("WM_DELETE_WINDOW", self.onClose)
        self.main.mainloop()
        
    def buildPage(self):
        # ----- Meubar configuration -----
        menubar = tk.Menu(self.main)
        
        self.file_menu = tk.Menu(menubar, tearoff=0)
        self.file_menu.add_command(label='Quit', command=self.main.destroy)
        
        self.about_menu = tk.Menu(self.main, tearoff=0)
        self.about_menu.add_command(label='About', command=lambda: AboutPopup())
        
        menubar.add_cascade(label='File', menu=self.file_menu)
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
    
    def onClose(self):
        '''Close communication w/ arduino before closing app'''
        
        if self.settings_tab.record_state:
            messagebox.showerror('Error', 'Please stop recording first')
        else:    
            self.main.destroy()
        

class SettingsPage(ttk.Frame):
    '''First tab w/ settings'''

    plot_pages = []    # Used when outputting data
    millis = 15        # Delay between each inBetweener value
    record_state = False
    prev_record = False
    
    max_seconds = 360
    max_servos = 8
    
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
        
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(expand=1, fill=tk.BOTH)
        
        # Use Shift+d to change max seconds/servos
        self.main_frame.bind("<Shift-D>", lambda event: DevPopup(self))
        self.main_frame.bind("<Button-1>", lambda event: self.main_frame.focus_set())
        
        # --- Left side Frame ---
        left = ttk.Frame(self.main_frame)
        left.pack(side=tk.LEFT, anchor=tk.N)
        
        l_title = ttk.Label(left, text='Settings', font=(None, 25))
        l_title.grid(columnspan=5, pady=20)
                
        self.seconds_label_var.set('Routine length (in seconds)\
            \n(1-{}):'.format(SettingsPage.max_seconds))
        seconds_label = ttk.Label(left, textvariable=self.seconds_label_var)
        seconds_label.grid(padx=10, pady=15)
        
        self.seconds_entry = ttk.Entry(left, width=5, justify=tk.RIGHT,
            textvariable = self.num_of_seconds, state='disabled')
        self.seconds_entry.grid(padx=25, pady=15, row=1, column=1)
        
        self.servo_label_var.set(\
            'Number of servos (1-{})'.format(SettingsPage.max_servos))
        servo_total_label = ttk.Label(left, textvariable=self.servo_label_var)
        servo_total_label.grid(padx=10, pady=15)
        
        self.servo_total_entry = ttk.Entry(left, width=5, justify=tk.RIGHT,
            textvariable = self.num_of_servos, state='disabled')
        self.servo_total_entry.grid(padx=25, pady=15, row=2, column=1)
        
        self.generate_plots_button = ttk.Button(left, text='Generate Plots',
            command=self.generatePlots, state='disabled')
        self.generate_plots_button.grid(padx=25, pady=25, row=1, column=2,
            rowspan=2)
        
        # --- Right side Frame ---
        right = ttk.Frame(self.main_frame)
        right.pack(anchor=tk.CENTER)
        
        r_title = ttk.Label(right, text='Output', font=(None, 25))
        r_title.grid(columnspan=5, pady=20)
        
        self.btn_check_var.set(False)
        button_checkbox = ttk.Checkbutton(right,
            text = 'Use button to Start Routine\n(Enter Pin Number)',
            variable=self.btn_check_var,
            command=self.toggleBtnCheckbox)
        button_checkbox.grid(sticky=tk.W)
    
        self.button_entry = ttk.Entry(right, width=5, justify=tk.RIGHT,
            textvariable=self.button_entry_val, state='disabled')
        self.button_entry.grid(padx=25, pady=5, row=1, column=1)
        self.button_entry_val.set('None')
        
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
            command=self.loadData, state='disabled')
        self.load_button.grid(row=4, column=1)

        # Images for the record button
        record_image = Image.open('resources/record.png')
        record_image.thumbnail((100, 100), Image.ANTIALIAS)
        self.record_image = ImageTk.PhotoImage(record_image)
        stop_image = Image.open('resources/stop.png')
        stop_image.thumbnail((100, 100), Image.ANTIALIAS)
        self.stop_image = ImageTk.PhotoImage(stop_image)
        
        self.record_button = ttk.Button(right, 
            text='Record',
            command=self.toggleRecording, 
            compound=tk.BOTTOM,
            image=self.record_image)
        self.record_button.grid(row=5, columnspan=3, pady=50)
    
    def toggleBtnCheckbox(self):
        '''Toggle state of button entry based on checkbox'''
        
        if self.btn_check_var.get():
            self.button_entry.configure(state='normal')
        else:
            self.button_entry.configure(state='disabled')
            self.button_entry_val.set('None')
    
    def toggleRecording(self):
        if self.record_state == True:
            self.record_state = False
            self.record_button['image'] = self.record_image
            self.record_button['text'] = 'Record'
            
            self.save_button['state'] = 'normal'
            self.output_button['state'] = 'normal'
        else:
            self.record_state = True
            self.record_button['image'] = self.stop_image
            self.record_button['text'] = 'STOP'
        
            self.save_button['state'] = 'disabled'
            self.output_button['state'] = 'disabled'
        
        if self.record_state:
            self.talkToArduino()    
    
    def initializeArduino(self):
        '''Initialize required number of tabs/plots'''
        
        self.arduino.write(b'n') # Command arduino to send servo count 
        
        #####
        values = self.arduino.readline()
        values = values.strip()
        # Breakdown line of data into individual values
        new_tabs = values.decode().strip(',').split(',')
        num_servos = len(new_tabs)
        ####
                
        if num_servos > SettingsPage.max_servos:
            messagebox.showerror('Error', '{} servos max'.format(SettingsPage.max_servos))
            self.toggleRecording()
            return
        
        self.num_of_servos.set(num_servos)
        self.generatePlots(new_tabs)
        self.prev_record = True
        
        self.main_frame.unbind("<Shift-D>")
        self.main_frame.unbind("<Button-1>")
                
        # Let tkinter do what it needs
        self.parent.main.update_idletasks()
        self.parent.main.update()
        
    def talkToArduino(self):
        '''Open serial line with Arduino and read values.
           Arduino sketch expects 'r' to start sending values
           and 's' to stop sending values'''
        try:
            with serial.Serial('/dev/ttyUSB0', 9600) as self.arduino:
                print('Waiting for Arduino')
                sleep(2)   # Wait for arduino to be ready
                
                if not self.prev_record:
                    self.initializeArduino()
                
                # Disable buttons while recording    
                self.toggleButtonStates()
    
                # Send record signal
                self.arduino.write(b'r')            
                while self.record_state:
                    if self.arduino.inWaiting() > 0:
                        
                        values = self.arduino.readline()
                        values = values.strip()
                        # Breakdown line of data into individual values
                        new_ys = values.decode().strip(',').split(',')
                        
                        self.updatePlotData(new_ys)
                        
                        # Let tkinter do what it needs while stuck in this loop
                        self.parent.main.update_idletasks()
                        self.parent.main.update()
                
                # Command arduino to stop sending values        
                if not self.record_state:
                    self.arduino.write(b's')
                
                # Re-enable buttons
                self.toggleButtonStates()
                
        except serial.SerialException as e:
            self.record_state = False
            self.record_button['image'] = self.record_image
            self.record_button['text'] = 'Record'
            
            print(e)
            messagebox.showerror('Error', 'Cannot find Arduino')
        except Exception as e:
            self.toggleRecording()
            print('Something went wrong')
            print(e)
            print(traceback.format_exc())
 
    def updatePlotData(self, newYs):
        # Update all plots
        for index, data_point in enumerate(newYs):
            plot = SettingsPage.plot_pages[index].plot
            
            if (len(self.plot_pages) * ((len(plot.ys)-1)/2)) >= SettingsPage.max_seconds:
                self.toggleRecording()
                self.record_button['state'] = 'disabled'
                messagebox.showinfo('Memory Full',
                    'Total recording time limited to {} seconds'.format(SettingsPage.max_seconds))
                break
            
            plot.ys.append(int(data_point))
            plot.xs =[i for i in range(len(plot.ys))]
            
            #~ plot.length = len(plot.ys) + 1
            plot.parent.slider['to'] = (len(plot.ys) / 2) - 10
            plot.scale.set(len(plot.ys))
            self.num_of_seconds.set(int((len(plot.ys)-1)/2))
            
            plot.update()
 
    def toggleButtonStates(self):
        if self.record_state:
            for page in self.plot_pages:
                page.settings_button['state'] = 'disabled'
        else:
            for page in self.plot_pages:
                page.settings_button['state'] = 'normal'

    def generatePlots(self, servos):
        '''
        Generate specified number of Plot tabs with correct name,
        each containing a plot for recording
        '''

        # Generate tabs/plots from Arduino info
        for i in servos:
            tab_title = i[:10]
            tab_name = tab_title + '_tab'
            setattr(self, tab_name, PlotPage(self, tab_title))
            self.parent_notebook.add(getattr(self, tab_name), text=tab_title)
            SettingsPage.plot_pages.append(getattr(self, tab_name))
            
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
        try:    # Each servo must have unique pin number assigned
            pin_nums = [int(tab.pin_num.get()) for tab in SettingsPage.plot_pages]
            if len(pin_nums) != len(set(pin_nums)):
                messagebox.showerror('Error', 'Repeated servo pin numbers')
                return
        except Exception:
            messagebox.showerror('Error', 'Check servo pin numbers')
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
        '''Loads data from previous save'''
        
        file_name = fd.askopenfilename(
                initialdir=os.path.join(os.path.dirname(__file__)),
                defaultextension='.servo',
                title='Load Settings')
            
        if file_name:
            self.load_flag = True
            
            with open(file_name, 'rb') as reader:
                self.settings = dill.load(reader)
            
            self.generatePlots()
            
            del self.settings
                
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
        # Upper limit is seconds minus half the length of the plot 'x_window'
        self.slider = ttk.Scale(self, orient=tk.HORIZONTAL,
            to=self.parent.num_of_seconds.get()-10,
            length=self.parent.parent_notebook.winfo_width())
        
        # Plot instance, bound to tab instance
        self.plot = Plot(self, self.parent.num_of_seconds.get(), self.slider,
            self.plot_num)
        
        # Drawing area for the graph
        canvas = FigureCanvasTkAgg(self.plot.fig, master=self)
        # Bind mouse events to canvas to change data
        canvas.mpl_connect('pick_event', self.plot.onPress)
        canvas.mpl_connect('button_release_event', self.plot.onRelease)
        canvas.mpl_connect('motion_notify_event', self.plot.onMotion)
        
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
        canvas.get_tk_widget().grid(columnspan=3)
        self.slider.grid(columnspan=3)
        
        pin_assign_frame.grid(sticky=tk.W)
        pin_label.grid()
        self.pin_entry.grid(row=0, column=1)
        
        button_frame.grid(row=2, column=2, sticky=tk.E)

        self.settings_button.pack(padx=5, side=tk.RIGHT)

    def settingsDisplay(self):
        '''Add settings tabs to empty settings popup'''
        
        popup = SettingsPopup()
        
        popup.addTab(NamePage(self, popup), 'Change Title')
        popup.addTab(TimeAddPage(self, popup), 'Add Time')
        popup.addTab(TimeDelPage(self, popup), 'Delete Time')
        popup.addTab(LimitPage(self.plot, popup), 'Adjust Limits')
    

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
        self.length = 0
        
        self.click = False             # Node follows mouse only when clicked
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
        self.ys = [self.lower_limit for i in self.xs]
        
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
        
    def onPress(self, event):
        '''Which node has been clicked'''
        
        point = event.artist
        index = event.ind
        
        self.point_index = int(index[0])
        
        if not event.mouseevent.dblclick:
            self.click = True
        
        else:
            # If node is double-clicked open popup to change value
            sleep(.1)  # Short delay to end all events on mainloop
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

        self.clearPlotLines()
        
        self.drawPlot()
        self.fig.canvas.draw()
        


WIDTH = 1000
HEIGHT = 600

if __name__ == '__main__':
    
    app = MainApp(WIDTH, HEIGHT)
    
    
    
    
