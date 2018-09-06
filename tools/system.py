import os
import shutil
import tkMessageBox
import Tkinter

def ask_to_clean_dir(dirpath, gui=True):
    if os.path.exists(dirpath) and os.path.isdir(dirpath) and len(os.listdir(dirpath)) > 0:
        while True:
            question = dirpath+" is not empty, shall I clean it?"

            if gui:
                window = Tkinter.Tk()
                window.wm_withdraw()
                answer = tkMessageBox.askyesno('Clean directory',question, parent=window)
            else:
                reply = raw_input(question+" Y/N\n").lower()
                if reply.lower() == 'y':
                    answer=True
                elif reply.lower() == 'n':
                    answer=False
                else:
                    print "Wrong answer"

            if answer:
                shutil.rmtree(dirpath)
                os.mkdir(dirpath)
                break
            else:
                exit()

    elif not os.path.exists(dirpath):
        os.mkdir(dirpath)
    elif not os.path.isdir(dirpath):
        print "Output directory exists and is file"

def clear_dir(dirpath):
    import shutil

    if os.path.exists(dirpath):
        shutil.rmtree(dirpath)
    os.mkdir(dirpath)

def assert_dir_exists(dirpath):
    import os
    if not os.path.exists(dirpath):
        os.mkdir(dirpath)

def savefile(save_function, *args, **kwargs):
    """
    function that asserts that directory to which
    you want write exists. It is assumed that first argument
    of args is the path to a file
    """
    from os import makedirs
    from os.path import dirname
    from os.path import exists

    if not exists(dirname(args[0])):
        makedirs(dirname(args[0]))

    save_function(*args, **kwargs)