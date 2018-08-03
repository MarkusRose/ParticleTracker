from GUI import guiMain
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-v',"--verbose", help="increase output verbosity",action="store_true")
args = parser.parse_args()


def main(argv):
    app = guiMain.mainWindow(None)
    app.title("MainWindow")
    app.mainloop()
    return

if __name__=="__main__":
    main(None)

