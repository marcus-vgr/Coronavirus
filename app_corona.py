from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
#import matplotlib

#matplotlib.use('Qt5Agg')
#plt.style.use('seaborn-darkgrid')
plt.style.use('dark_background')

from PyQt5 import QtCore, QtWidgets, QtGui, Qt, QtTest
from PyQt5.QtWidgets import QPushButton, QTabWidget, QApplication, QDialog, QVBoxLayout, QWidget
import sys

import pandas as pd 
import numpy as np


class MplCanvas_Basemap(FigureCanvas):
    
    def __init__(self, parent=None, width=5, height=4, dpi=50):
        fig = Figure(figsize=(width, height), dpi=dpi, tight_layout={'pad': 0})
        self.axes = fig.add_subplot(111)
        self.compute_initial_figure()

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    #"""
    def compute_initial_figure(self):
        m = Basemap(llcrnrlon=-53,llcrnrlat=-25,urcrnrlon=-44.6,urcrnrlat=-19.8,\
            rsphere=(6378137.00,6356752.3142),\
            resolution='l',projection='merc',\
            lat_0=-23.533773,lon_0=-46.625290, \
            ax=self.axes)

        m.drawcoastlines(linewidth=2.0, color='black')
        m.fillcontinents(color='green')

        m.drawmapboundary(fill_color='aqua')
        m.drawstates(linewidth=2.0, color='black')

        for munic in munics:
            lat = munics_infos[munic]['latitude']
            lon = munics_infos[munic]['longitude']
            radius = (munics_infos[munic]['area']/np.pi/100 * 10**6)**0.5
            casos_mm7d = munics_infos[munic]['last_casos_mm7d']
                    
            if casos_mm7d > 0:

                x, y = m(lon, lat) 
                alpha = (casos_mm7d/worst_casos_mm7d)**0.3
                circ = plt.Circle((x, y), radius, alpha=alpha, color='darkred')
                self.axes.add_patch(circ)
  

class MplCanvas_Munic(FigureCanvas):

    def __init__(self, munic='São Paulo', datahora='2020-02-25',parent=None, width=5, height=4, dpi=50):
        self.fig = Figure(figsize=(width, height), dpi=dpi, tight_layout={'pad': 1.0})

        self.ax_casos = self.fig.add_subplot(211)
        self.ax_obitos = self.fig.add_subplot(212)

        self.df_aux = df[(df['nome_munic'] == munic) & (df['datahora'] >= datahora)]

        self.munic = munic   
        self.compute_initial_figure()

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        self.fig.canvas.mpl_connect("motion_notify_event", self.hover)

    
    def compute_initial_figure(self):

        datahora = self.df_aux.datahora.values
        datahora = [i.split('-') for i in datahora]
        datahora = [i[2]+'/'+i[1] for i in datahora]

        ticks = range(0,len(datahora),int(len(datahora)/25)+1)
        ticksLabels = [datahora[i] for i in range(0,len(datahora),int(len(datahora)/25)+1)]
        for ax in [self.ax_casos, self.ax_obitos]:
            ax.set_xticks(ticks, minor=False)
            ax.set_xticklabels(ticksLabels, fontdict=None, minor=False, rotation=45)
            ax.tick_params(labelsize=18)

        
        self.ax_casos.bar(range(self.df_aux.shape[0]), self.df_aux['casos_novos'], color='#6694ec')
        self.ax_casos.plot(range(self.df_aux.shape[0]), self.df_aux['casos_mm7d'], color='red', linewidth=5.0)
        self.sc_casos = self.ax_casos.scatter(range(self.df_aux.shape[0]), self.df_aux['casos_mm7d'], color='red', s=100)
        self.ax_casos.set_title("Casos", loc='left', fontsize=17)

        self.ax_obitos.bar(range(self.df_aux.shape[0]), self.df_aux['obitos_novos'], color='#6694ec')
        self.ax_obitos.plot(range(self.df_aux.shape[0]), self.df_aux['obitos_mm7d'], color='red', linewidth=5.0)
        self.sc_obitos = self.ax_obitos.scatter(range(self.df_aux.shape[0]), self.df_aux['obitos_mm7d'], color='red', s=100)
        self.ax_obitos.set_title("Óbitos", loc='left', fontsize=17)

        self.fig.suptitle(self.munic, fontsize=20, y=0.99)

        self.annot_casos = self.ax_casos.annotate("", xy=(0,0), xytext=(-100,20),textcoords="offset points",
                    bbox=dict(boxstyle="round", fc="w"),
                    arrowprops=dict(arrowstyle="->"), fontsize=15, color='darkblue')
        self.annot_casos.set_visible(False)

        self.annot_obitos = self.ax_obitos.annotate("", xy=(0,0), xytext=(-100,20),textcoords="offset points",
                            bbox=dict(boxstyle="round", fc="w"),
                            arrowprops=dict(arrowstyle="->"), fontsize=15, color='darkblue')
        self.annot_obitos.set_visible(False)

    def update_annot(self, ind, tipo):
    
        def create_text():
            data = self.df_aux.iloc[ind["ind"][0]]['datahora']
            data = data.split('-'); data.reverse(); data = '/'.join(data)
            
            if tipo == "casos":
                mm7d = np.round(self.df_aux.iloc[ind["ind"][0]]['casos_mm7d'],0)
            elif tipo == "obitos":
                mm7d = np.round(self.df_aux.iloc[ind["ind"][0]]['obitos_mm7d'],0)
               
            return f'Data: {data}'+'\n'+f'Média Movel: {int(mm7d)}'
            

        if tipo == "casos":
            pos = self.sc_casos.get_offsets()[ind["ind"][0]]
            self.annot_casos.xy = pos
            text = create_text()
            self.annot_casos.set_text(text)
        elif tipo == "obitos":
            pos = self.sc_obitos.get_offsets()[ind["ind"][0]]
            self.annot_obitos.xy = pos
            text = create_text()
            self.annot_obitos.set_text(text)

    def hover(self, event):
        if event.inaxes == self.ax_casos:
            vis = self.annot_casos.get_visible()
            cont, ind = self.sc_casos.contains(event)
            if cont:
                self.update_annot(ind, "casos")
                self.annot_casos.set_visible(True)
                self.fig.canvas.draw_idle()
            else:
                if vis:
                    self.annot_casos.set_visible(False)
                    self.fig.canvas.draw_idle()

        if event.inaxes == self.ax_obitos:
            vis = self.annot_obitos.get_visible()
            cont, ind = self.sc_obitos.contains(event)
            if cont:
                self.update_annot(ind, "obitos")
                self.annot_obitos.set_visible(True)
                self.fig.canvas.draw_idle()
            else:
                if vis:
                    self.annot_obitos.set_visible(False)
                    self.fig.canvas.draw_idle()

    





class TabOverview(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        self.l = QtWidgets.QGridLayout()

        data = df.iloc[-1].datahora
        casos_totais = df[df.datahora == data]['casos'].sum()
        casos_novos = df[df.datahora == data]['casos_novos'].sum()
        obitos_totais = df[df.datahora == data]['obitos'].sum()
        obitos_novos = df[df.datahora == data]['obitos_novos'].sum()
        data = data.split('-'); data.reverse(); data = '/'.join(data)


        if casos_totais > 1e6:
            s = str(np.round(casos_totais, -4))
            casos_totais = s[:-4-2]+','+s[len(s)-4-2:-4]+' milhões'

        if obitos_totais > 1e6:
            s = str(np.round(obitos_totais, -4))
            obitos_totais = s[:-4-2]+','+s[len(s)-4-2:-4]+' milhões'
        

        self.text_data = QtWidgets.QLabel("Última atualização: "+data)
        self.text_data.setAlignment(QtCore.Qt.AlignCenter)

        self.text_casos = QtWidgets.QLabel('Número de casos no estado: \n'+
        f'{casos_totais} + {casos_novos}')
        self.text_casos.setAlignment(QtCore.Qt.AlignCenter)
        
        self.text_obitos = QtWidgets.QLabel('Número de óbitos no estado: \n'+
        f'{obitos_totais} + {obitos_novos}')
        self.text_obitos.setAlignment(QtCore.Qt.AlignCenter)
        
        
        self.canvas_basemap = MplCanvas_Basemap()
        
        self.l.addWidget(self.canvas_basemap, 0, 0, 8, 1)
        self.l.addWidget(self.text_data, 1, 1)
        self.l.addWidget(self.text_casos, 2, 1)
        self.l.addWidget(self.text_obitos, 3, 1)

        self.setLayout(self.l)


def transform_data(data, inverse=False):
    if inverse is not True:
        data = data.split('-')
        data.reverse()
        data = '/'.join(data)
    
    else:
        data = data.split('/')
        data.reverse()
        data = '-'.join(data)
        
    return data              


class TabMunic(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.munic = 'São Paulo'
        self.datahora = df.iloc[0].datahora
        self.datahora_print = transform_data(self.datahora)
        self.obtain_info()

        self.text_data = QtWidgets.QLabel("Última atualização: "+self.data)
        self.text_data.setAlignment(QtCore.Qt.AlignCenter)
        
        self.text_casos = QtWidgets.QLabel('Número de casos: \n'+
        f'{self.casos_totais} + {self.casos_novos}')
        self.text_casos.setAlignment(QtCore.Qt.AlignCenter)
        
        self.text_obitos = QtWidgets.QLabel('Número de óbitos: \n'+
        f'{self.obitos_totais} + {self.obitos_novos}')
        self.text_obitos.setAlignment(QtCore.Qt.AlignCenter)

        self.label = QtWidgets.QLabel('Selecione um município e uma data inicial:')
        self.datahora_label = QtWidgets.QLineEdit()
        self.datahora_label.setMaximumWidth(300)
        self.datahora_label.setText(self.datahora_print)
        self.datahora_label.returnPressed.connect(self.on_click2)

        self.canvas_munic = MplCanvas_Munic(self.munic, self.datahora)    
        
        self.comboBox = QtWidgets.QComboBox(self)
        self.comboBox.setStyleSheet("combobox-popup: 0;")
        for munic in munics:
            self.comboBox.addItem(munic)
        self.comboBox.activated[str].connect(self.on_click)
        #self.comboBox.setMaxVisibleItems(5)
        idx_munic_init = np.where(munics == self.munic)[0][0]
        self.comboBox.setCurrentIndex(idx_munic_init)
        
        
        self.l = QtWidgets.QGridLayout()
        
        self.l.addWidget(self.canvas_munic, 0, 1, 9, 1)
        self.l.addWidget(self.comboBox, 2,0)
        self.l.addWidget(self.text_data, 5, 0)
        self.l.addWidget(self.text_casos, 6, 0)
        self.l.addWidget(self.text_obitos, 7, 0)
        self.l.addWidget(self.label, 0,0)
        self.l.addWidget(self.datahora_label, 1, 0)
        
        self.setLayout(self.l)

    def on_click(self, munic):
        self.munic = munic
        self.datahora_print = self.datahora_label.text()
        self.datahora = transform_data(self.datahora_print, inverse=True) 
        self.obtain_info()

        self.l.removeWidget(self.canvas_munic)
        self.canvas_munic = MplCanvas_Munic(self.munic, self.datahora)
        self.l.addWidget(self.canvas_munic, 0, 1, 9, 1)

        self.text_data.setText("Última atualização: "+self.data)
        self.text_casos.setText('Número de casos: \n'+
        f'{self.casos_totais} + {self.casos_novos}')
        self.text_obitos.setText('Número de óbitos: \n'+
        f'{self.obitos_totais} + {self.obitos_novos}')

    def on_click2(self):
        self.on_click(self.munic)

    def obtain_info(self):
        
        self.df_aux = df[(df['nome_munic'] == self.munic) & (df['datahora'] >= self.datahora)].iloc[-1]
        
        self.data = self.df_aux.datahora
        self.casos_totais = self.df_aux.casos
        self.casos_novos = self.df_aux.casos_novos
        self.obitos_totais = self.df_aux.obitos
        self.obitos_novos = self.df_aux.obitos_novos
        self.data = self.data.split('-'); self.data.reverse(); self.data = '/'.join(self.data)



class MainWindow(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Coronavírus no Estado de São Paulo')
        self.setStyleSheet("background-color: black;"+"font-weight: bold")
        self.setFixedSize(800, 512)

        vbox = QVBoxLayout()
        self.tabWidget = QTabWidget()

        tab_overview = TabOverview()
        tab_munic = TabMunic()

        self.tabWidget.addTab(tab_overview, "Infos. Gerais")
        self.tabWidget.addTab(tab_munic, "Infos. Específicas")
        self.tabWidget.setStyleSheet("color: red;")


        vbox.addWidget(self.tabWidget)
        self.setLayout(vbox)
        self.showMaximized()





if __name__ == '__main__':

    #""" 
    print('Coletando os dados da secretaria do estado de São Paulo...')
    # Reading csv file
    #df = pd.read_csv('teste.csv')
    url = 'https://raw.githubusercontent.com/seade-R/dados-covid-sp/master/data/dados_covid_sp.csv'
    cols = ['nome_munic', 'datahora', 'casos', 'casos_novos', 'casos_mm7d', 'obitos', 'obitos_novos', 'obitos_mm7d',
        'area', 'latitude', 'longitude', 'pop']

    df = pd.read_csv(url, error_bad_lines=False, sep=';', decimal=',', usecols=cols)
    df.drop(df[df.nome_munic == 'Ignorado'].index)


    # Get the last informations about each munic and saving in a dictionary
    munics = df.nome_munic.unique()
    munics_infos = {}
    worst_casos_mm7d = 0  # We shall save the worst value for casos_mm7d
    for munic in munics:
        df_aux = df.loc[df['nome_munic'] == munic].iloc[-1]
        last_casos_mm7d = float(df_aux.casos_mm7d)
        area = float(df_aux.area)
        latitude = float(df_aux.latitude)
        longitude = float(df_aux.longitude)
        
        if last_casos_mm7d > worst_casos_mm7d:
            worst_casos_mm7d = df_aux.casos_mm7d
            
        munics_infos[munic] = {'last_casos_mm7d': last_casos_mm7d,
                            'area': area,
                            'latitude': latitude,
                            'longitude': longitude}

    print('Pronto! Abrindo aplicativo...')
    #"""

    # Run App
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()
    del window, app
