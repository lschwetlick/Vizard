#import OpenGL
from OpenGL import GLUT
from OpenGL import GL
#import OpenGL.GLUT
#import OpenGL.GLU
print("Imports successful!")



def showScreen():
    GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT) # Remove everything from screen (i.e. displays all white)


GLUT.glutInit()  # Initialize a glut instance which will allow us to customize our window
GLUT.glutInitDisplayMode(GLUT.GLUT_RGBA)  # Set the display mode to be colored
GLUT.glutInitWindowSize(500, 500)   # Set the width and height of your window
GLUT.glutInitWindowPosition(0, 0)   # Set the position at which this windows should appear
wind = GLUT.glutCreateWindow("OpenGL Coding Practice") # Give your window a title
GLUT.glutDisplayFunc(showScreen)  # Tell OpenGL to call the showScreen method continuously
GLUT.glutIdleFunc(showScreen)     # Draw any graphics or shapes in the showScreen function at all times
GLUT.glutMainLoop()  # Keeps the window created above displaying/running in a loop