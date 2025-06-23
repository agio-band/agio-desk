import os
from agio_desktop.tools.process_hub import ProcessHub


class DesktopMainProcess:
    def __init__(self):
        self.process_hub = ProcessHub()



def mian():
    print("Hello agio desktop")
    print(os.getpid())
    input("Press enter to continue...")


if __name__ == '__main__':
    # process hub
    #   tasks queue
    #   local server
    #   tray icon
    #   studio agent
    mian()