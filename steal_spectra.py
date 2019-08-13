"""
Controls the mouse and left clicks
at specified x, y coordiantes.

Author: Rasmus Nielsen
"""

from pynput.mouse import Button, Controller
import pyautogui
from pynput.mouse import Listener
from PIL import Image
import matplotlib.pyplot as plt
import imageio
import pandas as pd
import numpy as np
from scipy.interpolate import interp1d

# Debug mode
DEBUG = False

# Global x, y coordinates of Omnic
xx, yy = 0, 0

def on_click(x, y, button, pressed):
    """
    Saves the current position of the
    mouse when a right or left mouse
    button is pressed.
    """
    global xx, yy
    xx, yy = x, y
    
    if not pressed:
        # Stop listener
        return False

def save_screenshot(n):
    """
    Takes a screenshot and saves it
    to disk.

    Input:
        n - The current index of the
            spectra (int)
    return:
        file_name: Name of the screenshot
                   (string)
    """
    pic= pyautogui.screenshot()
    file_name = "screenshots/screenshot_{0}.png".format(n)
    pic.save(file_name)

    return file_name

def get_mouse_location():
    """
    Prints the location of
    the mouse to console.
    """
    while True:
       print(mouse.position)


def next_spectra(x, y):
    """
    Clicks the next button in Omnic
    to view the next spectra
    """
    # Initiate control of mouse
    mouse = Controller()
    
    # Location of next button
    mouse.position = (x, y)

    # Click next spectra button 
    mouse.click(Button.left, 1)

def init_omnic_variables():
    """
    Gets the button and corners of the spectra
    graph.

    return:
        x_button: Coordinate to the next button
        y_button: Coordinate to the next button
        x1: Upper left corner of the spectra graph
        y1: Upper left corner of the spectra graph
        x2: Lower right corner of the spectra graph
        y2: Lower right corner of the spectra graph
    """
    
    ## Get position of the next button
    print('Click on the location of the Omnic "next" button.')

    # Get pixel (x, y) position when mouse is clicked
    with Listener(on_click=on_click) as listener:
        listener.join()

    x_button, y_button = xx, yy

    print(x_button, y_button)
    # Update spectra image
    #next_spectra(x_button, y_button)

    ## Get position of upper and lower corners of spectra graph

    print("Click the upper left corner of the spectra graph.")

    # Get pixel (x, y) position when mouse is clicked
    with Listener(on_click=on_click) as listener:
        listener.join()

    x1, y1 = xx, yy
    print(x1, y1)

    print("Click the lower right corner of the spectra graph.")

    # Get pixel (x, y) position when mouse is clicked
    with Listener(on_click=on_click) as listener:
        listener.join()

    x2, y2 = xx, yy
    print(x2, y2)

    return x_button, y_button, x1, y1, x2, y2


def clip_screenshot(file_name, x1, y1, x2, y2, n):
    """
    Crops screenshot to only contain spectra graph.

    return:
        file_name: Name of the resulting graph (string)
    """
    # Load image
    img = Image.open(file_name)

    # Crop image using coordinates
    crop = img.crop((x1, y1, x2, y2))
    file_name = "spectra_graphs/spectra_grap_{0}.png".format(n)
    crop.save(file_name)

    return file_name

def get_red_colors_coordinates(img):    
    """
    Find pixels values for the "red"
    line in the spectra graph.
    """
    x_red = []
    y_red = []
    for x in range(0, img.shape[0]):
        for y in range(0, img.shape[1]):
            if (img[x, y, :].tolist() == [255, 00, 00]): # RGB-color
                y_red.append(x)
                x_red.append(y)
                #print 'Red pixel detected at x, y: ' + str(x) + ', ' + str(y)
    if DEBUG:
        # Plot image    
        plt.imshow(img)
        plt.scatter(x_red, y_red, s = 0.1, c = 'g')
    #    fig = plt.gcf()
    #    size = fig.get_size_inches()
    #    print size
        plt.show()
    return x_red, y_red

def remap(x, oMin, oMax, nMin, nMax):
    """
    Remaps number range to another range
    maintaining ratio.

    By PenguinTD: 
    https://stackoverflow.com/questions/
    929103/convert-a-number-range-to-
    another-range-maintaining-ratio
    """
    #range check
    if oMin == oMax:
        print("Warning: Zero input range")
        return None

    if nMin == nMax:
        print("Warning: Zero output range")
        return None

    #check reversed input range
    reverseInput = False
    oldMin = min( oMin, oMax )
    oldMax = max( oMin, oMax )
    if not oldMin == oMin:
        reverseInput = True

    #check reversed output range
    reverseOutput = False   
    newMin = min( nMin, nMax )
    newMax = max( nMin, nMax )
    if not newMin == nMin :
        reverseOutput = True

    portion = (x-oldMin)*(newMax-newMin)/(oldMax-oldMin)
    if reverseInput:
        portion = (oldMax-x)*(newMax-newMin)/(oldMax-oldMin)

    result = portion + newMin
    if reverseOutput:
        result = newMax - portion

    return result

def main():
    """
    main()
    """
    if DEBUG:
        print("Debug mode...")
    
    print("Loading compound list...")
    compound_names = pd.read_csv("compound_names.csv", 
            delimiter = ";")
    
    # Get the coordinates of the next button and
    # corners of the graph to clip the screenshots.
    x_button, y_button, x1, y1, x2, y2 = init_omnic_variables()
    
    for n, compound_name in enumerate(compound_names["compound"].tolist()):
        # Take screenshot
        screenshot_file_name = save_screenshot(n + 1)
        
        # Clip screenshot
        graph = clip_screenshot(screenshot_file_name, x1, y1, x2, y2, n + 1)

        # Load the graph
        img = imageio.imread(graph)
            
        # Get the x,y coordinates for the red pixels
        x_red, y_red = get_red_colors_coordinates(img)

        # The range of wavenumbers in the x-axis is
        # always constant!
        pixel_min = 0
        pixel_max = img.shape[1] 
        
        wavenumber_min = 4000
        wavenumber_max = 450
        
        # Remap the pixel scale to fit the wavenumber scale
        x_values = []
        for x in x_red:
            x_values.append(remap( x, pixel_min, pixel_max, wavenumber_min, wavenumber_max ))
        
        # The range of wavenumbers in the y-axis is
        # always constant!
        pixel_min = 0
        pixel_max = img.shape[0] 
        
        absorbance_min = 0
        absorbance_max = 1
        
        # Remap the pixel scale to fit the absorbance scale
        y_values = []
        for y in y_red: # 1 - remap() due to y-axis is calculated in reverse...
            y_values.append(1 - remap( y, pixel_min, pixel_max, absorbance_min, absorbance_max ))
        
        """
        # Interpolate new x and y
        f = interp1d(x_values, y_values)
        x_values = np.linspace(450, 4000, 1840)
        y_values = f(x_values)
        """
        if DEBUG:
            # Plot of detected pixels
            plt.scatter(x_red, y_red, s = 0.5)
            plt.title("Detected pixel values")
            plt.gca().invert_yaxis()
            plt.gcf().set_size_inches(6, 6)
            plt.show()

            # Plot of generated spectra
            plt.plot(x_values, y_values)
            plt.gca().invert_yaxis()
            plt.gca().invert_xaxis()
            plt.title("Transformed pixel values to spectra thingy")
            plt.ylabel("Absorbance")
            plt.xlabel("Wavenumbers [$cm^{-1}$]")
            plt.gcf().set_size_inches(6, 6)
            plt.show()

        d = {"wavenumbers": x_values,
             "absorbance": y_values}
        df = pd.DataFrame(data = d)
        
        df.to_csv("spectra_csv/index_{0}.csv".format(n + 1))
        
        # Witch to next spectra
        next_spectra(x_button, y_button)
        
        if DEBUG:
            break
    
    print("Done!")
    print("Ripped {0} spectras from database!".format(n + 1))

if __name__ == "__main__":
    main()
