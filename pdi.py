
"""

%--------------------------------------------------------------------------
%--1. Inicializo el sistema -----------------------------------------------
%--------------------------------------------------------------------------

#IMPORTE DE LIBRERIAS
"""
import csv
import os
import random
import cv2
import copy
import math
import pygame
from pygame.math import Vector2
from pygame.draw import rect
import scipy.io as sio
import numpy as np
import cv2

cam = cv2.VideoCapture(0)                                                       #Inicializar el modulo de camara

"""Declaración de Constantes"""
Y = 250                     #Posición en Y
X = 0                       #Posición en X

# umbrlaes para la detección del color en la capa "a" del espacio de color LAB
maxmask = 196                                                                   #Valor Maximo    
minmask = 168                                                                   #Valor minimo


def pdifun():
    global Y, X
    ret_val, img = cam.read()                                                   #Leer la imagen de la cámara en cada ciclo                                        
    img1=copy.copy(img)                                                         #una copia, una imagen para mostrar en color y otra para implementar el filtro
    mask = np.full((img.shape[0], img.shape[1]), 255, dtype=np.uint8)               #definir dimensiones de la mascara segun las dimensiones de la imagen de la camara
    
    """"
    %--------------------------------------------------------------------------
    %-- 2. Paso de imagen a color en sus componentes L A B  -------------------
    %--------------------------------------------------------------------------
    ---------------------------------------------------------------------------
                            Filtro por Color
    ---------------------------------------------------------------------------
    """
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)                                   #pasar de RGB a LAB
    l0,a0,b0 = cv2.split(lab)                                                    #Descomponer extraer las capas l0, a0 y b0 del espacio de color LAB
    
    """Binarizar capa a0  en un rango -->Tonos rojos a magenta"""
    a0 [a0 > maxmask] = 0                                                        #   Valores mayores a maxmask van a cero
    a0 [a0 < minmask] = 0                                                        #   Valores menores a minmask van cero
    a0 [a0 > 0      ] = 255                                                      #   El rango que quedó, pasa a 255
    a0 = a0/255                                                                  #  ahora a0 esta binarizada
   
    mask[a0==0]=0                                                               # mascara de color a aplicar 1 capa   
    mask_rgb = np.dstack((mask,mask,mask))                                      #mascara de color 3 capas           
    
    img[mask_rgb==0]=0;                                                         #Enmascarado de imagen a color
    imgflip= cv2.flip(img,1)                                                    #Invertir horizontalmente para crear efecto espejo
    imgflip1=cv2.flip(img1,1)                                                   #Invertir horizontalmente para crear efecto espejo
    
    """
    ---------------------------------------------------------------------------
    %--------------------------------------------------------------------------
    %-- 3. Aplicación de Morfologia a la imagen  ------------------------------
    %--------------------------------------------------------------------------
    
    ---------------------------------------------------------------------------
    """
    gray_img = cv2.cvtColor(imgflip, cv2.COLOR_BGR2GRAY)                        #pasar a escala de grises
    
    ret,th = cv2.threshold(gray_img,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)    #Binarizar la imagén producto del enmascarado
   
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(10,10))               #se define el Elemento estructurante --> Elipse 
    
    dilatacion = cv2.dilate(th,kernel,iterations = 4)                           #Dilatacion la imagen binarizada para eliminar ruido y rellenar  vacios"""
    th=copy.copy(dilatacion)                                                    #Copia de img dilatada para erosionar 
    
    erosion = cv2.erode(th,kernel,iterations = 4)                               #Erosion de la imagen Dilatada, para volverla a su Diametro original"""
    th1=copy.copy(erosion)                                                      #Copia de la erosion para erosionar una vez mas 
    
    erosion = cv2.erode(th1,kernel,iterations = 1)                              # Erosion de  una iteracion mas para obtener controno"""
    
    contorno = th1-erosion                                                      #Se obtiene el contorno
    contornoColor= cv2.cvtColor(contorno,cv2.COLOR_GRAY2RGB)                    #Se para el contorno de grises a color  
   
    contornoColor[:,:,0] = 0                                                   #Cambiar color al contorno
      
    cv2.imshow('Objeto', th1)                                                   #Mostrar imagen Binarizada y filtrada y con morfologia
    
    mask = np.full((img.shape[0], img.shape[1]), 255, dtype=np.uint8)          #crear mascara de dimensiones de camara
    
    """
    ---------------------------------------------------------------------------
    ------- 4-Momentos de la Imagen -------------------------------------------
    ---------------------------------------------------------------------------
    """
    moment = cv2.moments(th1)                                                   #Calculo de momentos de objeto de interes, para hayar el centroide
    
    font_text = cv2.FONT_HERSHEY_SIMPLEX                                        #fuente para imprimir numeros sobre imagen 
    
    if(int(moment['m00'])>0) :                                                  #Condicon de denominador diferente de cero, evita fallo div por cero 
        #Posicion en x,Y        
        X = int(moment['m10']/moment['m00'])                                    # posición X del centroide                      
        Y = int(moment ["m01"] / moment["m00"])                                 # posición Y del centroide
     
    
    """Mostrar Video con contorno y coordenadas"""
    cv2.putText(imgflip1,str(X) +',' + str(Y),(X+50,Y),                         
                font_text, 1,  (255, 0, 0),   2)                                #superpone las cooredenada X,Y del centroide en la imagen a color
    imgflip1 = cv2.add(imgflip1,contornoColor)                                  #superpone el contorno del objeto de interes sobre la imagen a color
    imgflip1 = cv2.circle(imgflip1, (X,Y), radius = 2, 
                          color =( 0, 255, 255) , thickness = -1)               #Grafica el centroide sobre el objeto de interes
    cv2.imshow("Gamer",imgflip1)                                                #Muestra en pantalla la imagen del jugador a color con las adiciones de control
    
    return Y                                                                    #Retorna la corrdenada Y del avatar al main del Juego. 

"""
%--------------------------------------------------------------------------
%---------------------------  FIN DEL PROGRAMA ----------------------------
%--------------------------------------------------------------------------
"""