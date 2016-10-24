from Tkinter import *
from notebook import *   # window with tabs

from melody_gui import *

root = Tk( ) 
root.title('Hindustani Pedagogical Music Learning Tool')
nb = notebook(root, TOP) # make a few diverse frames (panels), each using the NB as 'master': 

# uses the notebook's frame
f1 = Frame(nb( )) 
dft = DftModel_frame(f1)


nb.add_screen(f1, "SARGAM Practice") 

nb.display(f1)

root.geometry('+0+0')
root.mainloop()
