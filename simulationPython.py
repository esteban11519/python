import os 
import time
import math
import subprocess
import ltspice
import matplotlib.pyplot as plt
import numpy as np


class Tools():

    def paralelo(self,a,b):
        '''
        Calcula la impedancia en paralelo
        '''
        return a*b/(a+b)

    def escritura(self,data,archivo):
        '''
        data: valores a guardar
        archivo: Documento donde se guarda
        '''
        try:
            archivo= open(os.path.dirname(__file__)+'/'+archivo, "w" )
            archivo.write(data)
            archivo.close()
        except IOError:
            pass

    def circuito(self):
        print("El circuito que se va a realizar tiene la siguiente forma: ")
        c="\n        ---in--Lpi1_in---Lk1--nk--Lk2---Lm1--nm1--Lm2---Lpi1_out--out--\n\
           |                  |               |                    | \n\
           |                  |               |                    | \n\
        Lpi2_in               |              Lm3                Lpi2_out\n\
           |                  |               |                    | \n\
        np_in                Ck1             nm2                np_out \n\
           |                  |               |                    | \n\
        Cpi1_in               |              Cm1               Cpi1_out\n\
           |                  |               |                    | \n\
           |                  |               |                    | \n\
        ----------------------------------------------------------------gnd"

        print(c)
    def makeNetlist(self,f_c,f_infty,z_o,guardarDatosEn):
        # Especificación de parámetros para filtro pasa-bajos por método de imágenes
        omega_c=f_c*2*math.pi # [rad/s]
        omega_infty=f_infty*2*math.pi # [rad/s]
        Z_N=z_o # Debe ser igual a la impedancia característica


        # Desarrollo de cálculos
        m=(1-(omega_c/omega_infty)**2)**(0.5) # Parámetro m
        z_0=Z_N
            # Parámetros de filtros-k
        C=2/(z_0*omega_c)
        L=z_0**2*C

        Ck1=C
        Lk1=Lk2=L/2
     

        # Circuito equivalente m
        Lm1=Lm2=m*L/2
        Lm3=((1-m**2)/(4*m))*L
        Cm1=m*C
        print(Lm1)
        # Circuito compuesto

        mc=0.6 # Por el comportamiento de la impedancia normalizada de arreglo pi
        Lpi1_out=Lpi1_in=mc*L/2
        Lpi2_out=Lpi2_in=(1-mc**2)/(2*mc)*L
        Cpi1_out=Cpi1_in=mc*C/2



        netlist=".title filtro pasa altas mediante parámetro de imagen\n"\
        +"Vin in_1 0 dc 0 ac 1 "+"\n"\
        +"Rs in_1 in "+str(z_0)+"\n"\
        +"Lpi2_in in np_in "+str(Lpi2_in) +"\n"\
        +"Cpi1_in np_in 0 "+str(Cpi1_in) +"\n"\
        +"Lpi1_in_p_Lk1 in nk "+str(Lpi1_in+Lk1) +"\n"\
        +"Ck1 nk 0 "+str(Ck1)+ "\n"\
        +"Lk2_p_Lm1 nk nm1 "+str(Lk2+Lm1)+ "\n"\
        +"Lm3 nm1 nm2 "+str(Lm3)+ "\n"\
        +"Cm1 nm2 0 "+str(Cm1)+ "\n"\
        +"Lm2_p_Lpi1_out nm1 out "+str(Lm2+Lpi1_out) +"\n"\
        +"Lpi2_out out np_out "+str(Lpi2_out)+ "\n"\
        +"Cpi1_out np_out 0 "+str(Cpi1_out)+ "\n"\
        +"RL out 0 "+str(z_0)+"\n\n"\
        +".control\n"\
        +"ac dec 10000 100k 10meg\n"\
        +"plot (vdb(out)-vdb(in))\n"\
        +"write "+os.path.dirname(__file__)+'/'+guardarDatosEn+" all \n"\
        +".endc\n\n"\
        +".end"
        
        print(netlist)
        return netlist

    def simular(self,archivo):
        process = subprocess.Popen(['ngspice',archivo])
        try:
            print('Running in process', process.pid)
            process.wait(timeout=3) #En segundos
        except subprocess.TimeoutExpired:
            print('Timed out - killing', process.pid)
            process.kill()
            print("Done")
    def graficar(self,archivo):
        l = ltspice.Ltspice(os.path.dirname(__file__)+'/'+archivo) 
        # Make sure that the .raw file is located in the correct path
        l.parse()
        f= l.get_frequency()
        V_in =abs(l.get_data('V(in)'))
        V_out = abs( (l.get_data('V(out)')))
        H=20*np.log10(V_out)-20*np.log10(V_in)
        
        plt.semilogx(np.multiply(f,1e-6), H)
        plt.legend(['H'])
        plt.ylabel('[dB]')
        plt.xlabel('frecuencia [MHz]')
        plt.grid(True)
        plt.xticks(np.concatenate((np.arange(0.1,1,step=0.1),np.arange(1,11,step=1))))
        plt.show()


if __name__ == '__main__':
    guardarDatosEn="resultados.raw"
    circuito='pasa_bajas.cir'
    tools=Tools()
    tools.circuito()


    netlist=tools.makeNetlist(2E6,2.05E6,75,guardarDatosEn)
    tools.escritura(netlist,circuito)
    tools.simular(circuito)
    tools.graficar(guardarDatosEn)

  




