import os


class DesktopMainProcess:
    def __init__(self):
        self.process_hub = None



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