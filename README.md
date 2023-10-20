## Нахождение оптимального плана переработки различных партий сахарной свёклы
##### Authors:

GUI/validation : [4udoman](https://github.com/4udoman)

Обработка вычислений (algorithm.py, utils.py): [Sergey](https://github.com/sergey31415926)

### Установка необходимых пакетов

pip install pyqt6  
pip install numpy  
pip install matplotlib  
pip install scipy  
### Запуск с графическим интерфейсом
Находясь в ./beet/src  
python main_gui.py  
### Запуск с интерфейсом командной строки
Находясь в ./beet/src  
python main_cli.py  
### Для разработчиков
Находясь в ./beet/src  
python -m PyQt6.uic.pyuic -o window_for_gui.py -x window_for_gui.ui  
python -m PyQt6.uic.pyuic -o widget_for_gui.py -x widget_for_gui.ui  
С помощью данных команд, файлы с расширением .ui преобразуются в .py файлы, внутри которых написан код с использованием библиотеки PyQT6
