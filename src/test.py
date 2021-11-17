#%%
import pyseq

hs = pyseq.HiSeq()                  
hs.initializeCams()                
# hs.initializeInstruments()          # Initialize x,y,z & objective stages. Initialize lasers and optics (filters)

# %%
hs.image_path = 'C:\\Users\\sbsuser\\Documents\\PySeq2500\\Images\\'
hs.take_picture(32, "128")
# %%
hs.y.check_position()
# %%
hs.lasers['green'].set_power(100)   #Set green laser power to 100 mW
hs.lasers['red'].set_power(100)     #Set red laser power to 100 mW



hs.obj.move(30000)                  #Move objective to middle-ish

hs.optics.move_ex('green','open')                #Move excitation filter 1 to open position
hs.optics.move_ex('red','open')                #Move excitation filter 2 to open position

hs.lasers['green'].get_power()      #Get green laser power (mW i think)
hs.lasers['red'].get_power()        #Get red laser power   (mW i think)

# %%
print('Moving y')
hs.y.move(1500000)
#%%
print('Moving x')
hs.x.move(9500)
#%%
hs.z.move([21500, 21500, 21500])
# Set laser intensity to 100 mW
hs.lasers['green'].set_power(100)
hs.lasers['red'].set_power(100)

# %%
import time
def initializeOptics(hs: pyseq.HiSeq):
    """Initialize x,y,z, & obj stages, optics, and FPGA."""
    msg = 'HiSeq::'

    hs.message(msg+'Initializing FPGA')
    hs.f.initialize()
    hs.f.LED(1, 'green')
    hs.f.LED(2, 'green')

    #Initialize X Stage before Y Stage!
    hs.message(msg+'Initializing X & Y stages')
    hs.y.command('OFF')
    
    homed = hs.x.initialize()
    hs.y.initialize()
    hs.message(msg+'Initializing lasers')
    hs.lasers['green'].initialize()
    hs.lasers['red'].initialize()
    # hs.message(msg+'Initializing pumps and valves')
    # hs.p['A'].initialize()
    # hs.p['B'].initialize()
    # hs.v10['A'].initialize()
    # hs.v10['B'].initialize()
    # hs.v24['A'].initialize()
    # hs.v24['B'].initialize()

    # Initialize Z, objective stage, and optics after FPGA
    hs.message(msg+'Initializing optics and Z stages')
    hs.z.initialize()
    hs.obj.initialize()
    hs.optics.initialize()

    #Initialize ARM9 CHEM for temperature control
    hs.T.initialize()

    #Sync TDI encoder with YStage
    hs.message(msg+'Syncing Y stage')
    while not hs.y.check_position():
        time.sleep(1)
    hs.y.position = hs.y.read_position()
    hs.f.write_position(0)

    hs.message(msg+'Initialized!')
    return homed

initializeOptics(hs)
# %%
hs.optics.move_ex('green','open')
hs.optics.move_ex('red','open')
hs.optics.move_em_in(True)
# %%
x_begin = 20
y_begin = 15
size = 1
pos = hs.position('A', [x_begin, y_begin, x_begin-size, y_begin-size])
hs.y.move(pos['y_initial'])
hs.x.move(pos['x_initial'])

hs.lasers['green'].set_power(100)
hs.lasers['red'].set_power(100)
#%%
hs.y.move(pos['y_final'])
hs.x.move(pos['x_final'])
# %%
af = hs.autofocus(pos)
# %%
hs.take_picture(16, image_name='FirstHiSeqImage')
# %%
hs.lasers['green'].set_power(10)
hs.lasers['red'].set_power(10)
# %%
hs.z.move([20000, 20000, 20000])
# %%
hs.scan(pos['n_tiles'], 3, pos['n_frames'], image_name='FirstHiSeqScan')
# %%
