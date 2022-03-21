"""
Minimal texture on sphere demo
This is demo for showing how to put image
on sphere as texture in PyOpenGL.
"""
import cv2
import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from skimage.util import random_noise
import numpy as np


def draw_box(x1, x2, y1, y2):
    glBegin(GL_POLYGON)
    glNormal3f(0.0, 0.0, 1.0)
    glTexCoord2f(0, 0)
    glVertex3f(x1, y1, 0)
    glTexCoord2f(1, 0)
    glVertex3f(x2, y1, 0)
    glTexCoord2f(1, 1)
    glVertex3f(x2, y2, 0)
    glTexCoord2f(0, 1)
    glVertex3f(x1, y2, 0)
    glEnd()


def read_texture(filename):
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)

    image = pygame.image.load(f"{filename}.png")
    img = pygame.image.tostring(image, 'RGBA')

    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.get_width(), image.get_height(), 0,
                 GL_RGBA, GL_UNSIGNED_BYTE, img)
    return texture_id


def blur(img, shape=(6, 6)):
    return cv2.blur(img, shape)


def gaussian_noise(img):
    noise_img = random_noise(img, mode='gaussian', var=0.001)
    noise_img = (255 * noise_img).astype(np.uint8)
    return noise_img


def pepper_noise(img):
    noise_img = random_noise(img, mode='pepper')
    noise_img = (255 * noise_img).astype(np.uint8)
    return noise_img


def generate_variant(n, filename, angle_0=15, angle_1=4, x=1.0, y=0.1, angle_2=-1., translate_z=-2., scale1=1.3, scale2=1.3):
    image = pygame.image.load(f"{filename}.png")
    global texture_image
    # init window
    glutInit()

    w, h = 2000, 2000

    glutInitWindowSize(w, h)
    # glutInitWindowPosition(0, 0)

    # request for z-buffer via GLUT_DEPTH
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutCreateWindow("")

    # enable depth testing on z-buffer via GL_DEPTH_TEST
    glDisable(GL_BLEND)
    glEnable(GL_DEPTH_TEST)

    # add lighting
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    # to add another light: glEnable(GL_LIGHT1)
    glLightfv(GL_LIGHT0, GL_POSITION, [0, 0, 1, 1])
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.5, 0.5, 0.5, 1])
    # glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.5, 0.5, 0.5, 0])
    # glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1])
    glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 1.2)
    glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.03)

    # gluLookAt(xEye, yEye, zEye,
    #           xAt,  yAt,  zAt,
    #           xUp,  yUp,  zUp)
    gluLookAt(0, 0, 1,
              0, 0, 0,
              0, 1, 0)

    # set camera perspective
    glMatrixMode(GL_PROJECTION)
    # 3D Perspective Projection (fovy, aspect, zNear, zFar), relative to camera's eye
    # position
    gluPerspective(45, 1, 1, 50)

    # reset the Model - View matrix
    glMatrixMode(GL_MODELVIEW)

    glTranslatef(0, 0, translate_z)
    glRotatef(angle_0, x, y, 0)

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glPushMatrix()
    glRotatef(angle_1, 0, 0, 1)
    glEnable(GL_TEXTURE_2D)
    texture_image = read_texture(filename)
    glBindTexture(GL_TEXTURE_2D, texture_image)
    glMaterialfv(GL_FRONT, GL_AMBIENT, [0.5, 0.5, 0.5, 1])
    glMaterialfv(GL_FRONT, GL_SPECULAR, [0.2, 0.2, 0.2, 1])
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 50)
    iw = image.get_width()
    ih = image.get_height()
    draw_box(scale1 * -0.5, scale1 * 0.5, scale1 * -0.5 * (ih / iw), scale1 * 0.5 * (ih / iw))
    glDisable(GL_TEXTURE_2D)
    glPopMatrix()

    glPushMatrix()
    glRotatef(angle_2, 0, 0, 1)
    glTranslatef(0, 0, -0.1)
    glEnable(GL_TEXTURE_2D)
    texture_image = read_texture('стол')
    glMaterialfv(GL_FRONT, GL_AMBIENT, [0.5, 0.5, 0.5, 1])
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [0.5, 0.5, 0.5, 1])
    glBindTexture(GL_TEXTURE_2D, texture_image)
    draw_box(scale2 * -1.3, scale2 * 1.3, scale2 * -1.3, scale2 * 1.3)
    glDisable(GL_TEXTURE_2D)
    glPopMatrix()

    pixels = glReadPixels(0, 0, w, h, GL_RGB, GL_UNSIGNED_BYTE)

    img = cv2.cvtColor(np.frombuffer(pixels,
                                     dtype=np.uint8).reshape(w, h, 3), cv2.COLOR_RGB2BGR)

    img = blur(img, shape=(6, 6))
    img = gaussian_noise(img)
    img = blur(img, shape=(3, 3))
    cv2.imwrite(f"{filename}_result_{n}.png", img)


def main():
    for i in range(1, 11):
        generate_variant(0, i, angle_0=15, angle_1=4, x=1.0, y=0.1, angle_2=-1,
                         translate_z=-2,
                         scale1=1.3, scale2=1.3)
        generate_variant(1, i,  angle_0=7, angle_1=3, x=0.8, y=0.2, angle_2=3,
                         translate_z=-1.9,
                         scale1=1.3, scale2=1.4)
        generate_variant(2, i,  angle_0=-12, angle_1=4, x=0.74, y=0.1, angle_2=1,
                         translate_z=-1.8,
                         scale1=1.3, scale2=1.3)
        generate_variant(3, i,  angle_0=17, angle_1=-4, x=0.5, y=0.23, angle_2=2,
                         translate_z=-1.9,
                         scale1=1.3, scale2=1.4)
        generate_variant(4, i,  angle_0=-9, angle_1=1, x=1.0, y=0.1, angle_2=-1,
                         translate_z=-2.,
                         scale1=1.3, scale2=1.3)
        generate_variant(5, i, angle_0=13, angle_1=7, x=0.34, y=0.05, angle_2=-1,
                         translate_z=-1.9,
                         scale1=1.3, scale2=1.4)
        generate_variant(6, i, angle_0=8, angle_1=3, x=1.0, y=0.1, angle_2=-1,
                         translate_z=-2,
                         scale1=1.3, scale2=1.3)
        generate_variant(7, i, angle_0=9, angle_1=-3, x=0.2, y=0.1, angle_2=2,
                         translate_z=-1.99,
                         scale1=1.3, scale2=1.4)
        generate_variant(8, i, angle_0=-6, angle_1=5, x=2.0, y=0.4, angle_2=-1,
                         translate_z=-2,
                         scale1=1.3, scale2=1.3)
        generate_variant(9, i, angle_0=14, angle_1=2, x=1.0, y=0.11, angle_2=1.5,
                         translate_z=-2,
                         scale1=1.3, scale2=1.4)


if __name__ == '__main__':
    main()
