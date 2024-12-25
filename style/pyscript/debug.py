from pyscript import document

a = 1
def debug(event):
    global a
    print("hello")
    output = document.getElementById('debug')
    output.innerText = a
    a += 1
