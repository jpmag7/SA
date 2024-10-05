from processData import getData
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

img = Image.open('C:/Users/franc/OneDrive/Ambiente de Trabalho/University/4Ano2Semestre/SensorizacaoeAmbiente/Projeto/salas24UM.png')



def main():
    #getData()
    img_array = np.asarray(img)
    
    heatmap = np.random.rand(img_array.shape[0], img_array.shape[1])

    plt.imshow(img_array)
    plt.imshow(heatmap, cmap='hot', alpha=0.5)
    plt.colorbar()
    plt.show()


if __name__ == "__main__":
    main()