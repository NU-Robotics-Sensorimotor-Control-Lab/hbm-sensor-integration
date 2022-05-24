import ttkbootstrap as ttk
from ttkbootstrap.constants import *

app = ttk.Window(size=(500, 500))

gauge = ttk.Progressbar(
            master=app, 
            mode=INDETERMINATE, 
            bootstyle=(STRIPED, SUCCESS)
        )

gauge.pack(fill=BOTH, expand=YES, padx=10, pady=10)

# autoincrement the gauge
gauge.start()

# stop the autoincrement
gauge.stop()

# manually update the gauge value
gauge.configure(value=25)

# increment the value by 10 steps
gauge.step(10)

app.mainloop()