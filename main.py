import customtkinter as ctk
from package.gui.main_window import AppMainWindow
from package.database import inicializar_bd

def main():
    print("Inicializando o banco de dados...")
    inicializar_bd()
    print("Banco de dados pronto.")

    print("Iniciando a interface gráfica...")
    app = AppMainWindow()
    app.mainloop()

if __name__ == "__main__":
    main()