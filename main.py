import cv2
import serial
import math

camera = cv2.VideoCapture(0)  # веб камера
Arduino = serial.Serial(port='COM6', baudrate=115200, timeout=0)

while True:
    iSee = False  # флаг: был ли найден контур
    controlXY = 0  # нормализованное отклонение цветного объекта от центра кадра в диапазоне [-1; 1]
    success, frame = camera.read()  # читаем кадр с камеры
    if success:  # если прочитали успешно
        height, width = frame.shape[0:2]  # получаем разрешение кадра
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)  # переводим кадр из RGB в HSV

        #binary = cv2.inRange(hsv, (50, 100, 100), (70, 255, 255))          # пороговая обработка кадра (выделяем все зеленое)
        binary = cv2.inRange(hsv, (0, 100, 250), (20, 255, 255))            # пороговая обработка кадра (выделяем все красное)
        #binary = cv2.inRange(hsv, (0, 0, 0), (255, 255, 35))               # пороговая обработка кадра (выделяем все черное)

        # HSV в обычном формате                           |   HSV в OPENCV
        # H - 0...360                                     |   H - 0...180
        # S - 0...100                                     |   S - 0...255
        # V - 0...100                                     |   V - 0...255
        """
        # Чтобы выделить все красное необходимо произвести две пороговые обработки, т.к. тон красного цвета в hsv
        # находится в начале и конце диапазона hue: [0; 180), а в openCV, хз почему, этот диапазон не закольцован.
        # поэтому выделяем красный цвет с одного и другого конца, а потом просто складываем обе битовые маски вместе
        bin1 = cv2.inRange(hsv, (0, 60, 70), (10, 255, 255)) # красный цвет с одного конца
        bin2 = cv2.inRange(hsv, (160, 60, 70), (179, 255, 255)) # красный цвет с другого конца
        binary = bin1 + bin2  # складываем битовые маски
        """
        roi = cv2.bitwise_and(frame, frame, mask=binary)  # за счет полученной маски можно выделить найденный объект из общего кадра
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)  # получаем контуры выделенных областей
        if len(contours) != 0:  # если найден хоть один контур
            maxcont = max(contours, key=cv2.contourArea)  # находим наибольший контур
            moments = cv2.moments(maxcont)  # получаем моменты этого контура

            """
            # moments["m00"] - нулевой момент соответствует площади контура в пикселях,
            # поэтому, если в битовой маске присутствуют шумы, можно вместо
            # if moments["m00"] != 0:  # использовать
            if moments["m00"] > 20: # тогда контуры с площадью меньше 20 пикселей не будут учитываться
            """

            if moments["m00"] > 20:                             # контуры с площадью меньше 20 пикселей не будут учитываться
                cx = int(moments["m10"] / moments["m00"])       # находим координаты центра контура (найденного объекта) по x
                cy = int(moments["m01"] / moments["m00"])       # находим координаты центра контура (найденного объекта) по y
                iSee = True                                     # устанавливаем флаг, что контур найден

                controlXY = 510 * (cx - width / 2) / width                   # находим отклонение найденного объекта от центра кадра и нормализуем его (приводим к диапазону [-255; 255])
                controlXY = controlXY * 1
                cv2.drawContours(frame, maxcont, -1, (0, 255, 0), 2)         # рисуем контур
                cv2.line(frame, (cx, 0), (cx, height), (0, 0, 255), 6)       # рисуем линию линию по x
                cv2.line(frame, (0, cy), (width, cy), (0, 255, 0), 6)        # линия по y

        cv2.putText(frame, 'iSee: {};'.format(iSee), (width - 370, height - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2, cv2.LINE_AA)             # текст
        cv2.putText(frame, 'controlX: {:.2f}'.format(controlXY), (width - 200, height - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2, cv2.LINE_AA)  # текст



        controlXY = [int(controlXY)]                                                 #Создаем список аргументов
        contorlXY = str((list(map(abs, controlXY))))                             #Преобразовываем в строку
        contorlXY = contorlXY.replace("[", "").replace("]", "")
        print(contorlXY)




        """Функция отправки данных на ардуино"""
        def serialSend(data):  # Гл
            txs = ','.join(map(str, data)) + ';'
            Arduino.write(txs.encode())

        green_val = "0, " + contorlXY + ", 0"
        def checkYELLOW():
            iSee = True
            serialSend([1, green_val])
        checkYELLOW()
        print(green_val)




        #cv2.circle(frame, (width//2, height//2), radius=4, color=(0, 0, 255), thickness=-1)    # центр кадра
        cv2.imshow('frame', frame)      # Вывод обычный + контур цвета
        cv2.imshow('binary', binary)    # Вывод Бинаризации кадров (Белый - черный)
        cv2.imshow('roi', roi)          # Вывод маски цвета (Будет показан цвет объекта черный - красный*)
    if cv2.waitKey(1) == ord('q'):      # Выход на 'q'
        break
camera.release()
cv2.destroyAllWindows()



















#
#
#
#
#
#
#
#
# "Обнаружения красного цвета. Преобразование значений от 255 - 0 - 255"
# import cv2
# import serial
# camera = cv2.VideoCapture(0)  # веб камера
# Arduino = serial.Serial(port='COM6', baudrate=115200, timeout=0)
# while True:
#     iSee = False  # флаг: был ли найден контур
#     controlXY = 0  # нормализованное отклонение цветного объекта от центра кадра в диапазоне [-1; 1]
#     success, frame = camera.read()  # читаем кадр с камеры
#     if success:  # если прочитали успешно
#         height, width = frame.shape[0:2]  # получаем разрешение кадра
#         hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)  # переводим кадр из RGB в HSV
#         binary = cv2.inRange(hsv, (0, 100, 250), (20, 255, 255))  # пороговая обработка кадра (выделяем все красное)
#         roi = cv2.bitwise_and(frame, frame, mask=binary)  # за счет полученной маски можно выделить найденный объект из общего кадра
#         contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)  # получаем контуры выделенных областей
#         if len(contours) != 0:  # если найден хоть один контур
#             maxcont = max(contours, key=cv2.contourArea)  # находим наибольший контур
#             moments = cv2.moments(maxcont)  # получаем моменты этого контура
#             if moments["m00"] > 20:                             # контуры с площадью меньше 20 пикселей не будут учитываться
#                 cx = int(moments["m10"] / moments["m00"])       # находим координаты центра контура (найденного объекта) по x
#                 cy = int(moments["m01"] / moments["m00"])       # находим координаты центра контура (найденного объекта) по y
#                 iSee = True                                     # устанавливаем флаг, что контур найден
#                 controlXY = 510 * (cx - width / 2) / width         # находим отклонение найденного объекта от центра кадра и нормализуем его (приводим к диапазону [-255; 255])
#                 controlXY = controlXY * 1
#                 cv2.drawContours(frame, maxcont, -1, (0, 255, 0), 2)         # рисуем контур
#                 cv2.line(frame, (cx, 0), (cx, height), (0, 255, 0), 2)       # рисуем линию линию по x
#                 cv2.line(frame, (0, cy), (width, cy), (0, 255, 0), 2)        # линия по y
#         cv2.putText(frame, 'iSee: {};'.format(iSee), (width - 370, height - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2, cv2.LINE_AA)             # текст
#         cv2.putText(frame, 'controlX: {:.2f}'.format(controlXY), (width - 200, height - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2, cv2.LINE_AA)  # текст
#         controlXY = [int(controlXY)]                                                 #Создаем список аргументов
#         contorlXY = str((list(map(abs, controlXY))))                             #Преобразовываем в строку
#         contorlXY = contorlXY.replace("[", "").replace("]", "")
#         print(contorlXY)
#         def serialSend(data):  # Гл
#             txs = ','.join(map(str, data)) + ';'
#             Arduino.write(txs.encode())
#         green_val = "0, " + contorlXY + ", 0"
#         def checkYELLOW():
#             iSee = True
#             serialSend([1, green_val])
#         checkYELLOW()
#         print(green_val)
#         cv2.imshow('frame', frame)      # Вывод обычный + контур цвета
#         cv2.imshow('binary', binary)    # Вывод Бинаризации кадров (Белый - черный)
#         cv2.imshow('roi', roi)          # Вывод маски цвета (Будет показан цвет объекта черный - красный*)
#     if cv2.waitKey(1) == ord('q'):      # Выход на 'q'
#         break
# camera.release()
# cv2.destroyAllWindows()













# import cv2
# capture = cv2.VideoCapture(0)
# face_cascade = cv2.CascadeClassifier('haarcascade_lefteye_2splits.xml')
# face_cascade1 = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
# while True:
#     ret, img = capture.read()
#     if ret:
#         img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)  # переводим кадр из RGB в HSV
#         binary = cv2.inRange(img, (18, 60, 100), (32, 255, 255))  # пороговая обработка кадра (выделяем все желтое)
#         contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)  # получаем контуры выделенных областей
#     cv2.imshow('Kall', binary)
#     if cv2.waitKey(1) == ord('q'):
#         break
# capture.release()
# cv2.destroyAllWindows()

# import cv2
# capture = cv2.VideoCapture(0)
# face_cascade = cv2.CascadeClassifier('haarcascade_lefteye_2splits.xml')
# face_cascade1 = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
# while True:
#     ret, frame = capture.read()
#     if ret:
#         height, width = frame.shape[0:2]  # получаем разрешение кадра
#         frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)  # переводим кадр из RGB в HSV
#         binary = cv2.inRange(frame, (18, 60, 100), (32, 255, 255))  # пороговая обработка кадра (выделяем все желтое)
#         contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)  # получаем контуры выделенных областей
#         if len(contours) != 0:
#             maxc = max(contours, key=cv2.contourArea)
#             moments = cv2.moments(maxc)

#             if moments["m00"] > 20:
#                 cx = int(moments["m10"] / moments["m00"])
#                 cy = int(moments["m01"] / moments["m00"])
#                 iSee = True  # устанавливаем флаг, что контур найден
#                 controlX = 2 * (cx - width / 2) / width  # находим отклонение найденного объекта от центра кадра и
#                 # нормализуем его (приводим к диапазону [-1; 1])
#                 cv2.drawContours(frame, maxc, -1, (0, 255, 0), 1)  # рисуем контур
#                 cv2.line(frame, (cx, 0), (cx, height), (0, 255, 0), 1)  # рисуем линию линию по x
#                 cv2.line(frame, (0, cy), (width, cy), (0, 255, 0), 1)  # линия по y
#
#                 miniBin = cv2.resize(binary, (int(binary.shape[1] / 4), int(binary.shape[0] / 4)),  # накладываем поверх
#                                      interpolation=cv2.INTER_AREA)  # кадра маленькую
#                 miniBin = cv2.cvtColor(miniBin, cv2.COLOR_GRAY2BGR)  # битовую маску
#                 frame[-2 - miniBin.shape[0]:-2, 2:2 + miniBin.shape[1]] = miniBin  # для наглядности
#     cv2.imshow('Kall', frame)
#     if cv2.waitKey(1) == ord('q'):
#         break
# capture.release()
# cv2.destroyAllWindows()
#



# import cv2
# capture = cv2.VideoCapture(0)
# face_cascade = cv2.CascadeClassifier('haarcascade_lefteye_2splits.xml')
# face_cascade1 = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
# while True:
#     ret, img = capture.read()
#     faces = face_cascade.detectMultiScale(img, scaleFactor=1.5, minNeighbors=5, minSize=(20, 20))
#     for (x, y, w, h) in faces:
#         cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 255), 2)
#     faces = face_cascade1.detectMultiScale(img, scaleFactor=1.5, minNeighbors=5, minSize=(20, 20))
#     for (x, y, w, h) in faces:
#         cv2.rectangle(img, (x, y), (x+w, y+h), (0, 0, 255), 2)
#     cv2.imshow('Kall', img)
#     k = cv2.waitKey(30) & 0xFF
#     if k == 27:
#         break
# capture.release()
# cv2.destroyAllWindows()
#########
#Работает с двумя факторами



# import cv2
# capture = cv2.VideoCapture(0)
# face_cascade = cv2.CascadeClassifier('haarcascade_lefteye_2splits.xml')
# face_cascade1 = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
# while True:
#     ret, img = capture.read()
#     faces = face_cascade.detectMultiScale(img, scaleFactor=1.5, minNeighbors=5, minSize=(20, 20))
#     for (x, y, w, h) in faces:
#         cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 255), 2)
#     faces = face_cascade1.detectMultiScale(img, scaleFactor=1.5, minNeighbors=5, minSize=(20, 20))
#     for (x, y, w, h) in faces:
#         cv2.rectangle(img, (x, y), (x+w, y+h), (0, 0, 255), 2)
#     cv2.imshow('Kall', img)
#     k = cv2.waitKey(30) & 0xFF
#     if k == 27:
#         break
# capture.release()
# cv2.destroyAllWindows()
#########




































































#
#
#
# import cv2
# import serial
#
# camera = cv2.VideoCapture(0)  # веб камера
# Arduino = serial.Serial(port='COM6', baudrate=115200, timeout = 0)
#
# while True:
#     iSee = False  # флаг: был ли найден контур
#     controlX = -1  # нормализованное отклонение цветного объекта от центра кадра в диапазоне [-1; 1]
#     success, frame = camera.read()  # читаем кадр с камеры
#     if success:  # если прочитали успешно
#         height, width = frame.shape[0:2]  # получаем разрешение кадра
#         hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)  # переводим кадр из RGB в HSV
#         binary = cv2.inRange(hsv, (18, 60, 100), (32, 255, 255))  # пороговая обработка кадра (выделяем все желтое)
#         # binary = cv2.inRange(hsv, (0, 0, 0), (255, 255, 35))  # пороговая обработка кадра (выделяем все черное)
#
#         """
#         # Чтобы выделить все красное необходимо произвести две пороговые обработки, т.к. тон красного цвета в hsv
#         # находится в начале и конце диапазона hue: [0; 180), а в openCV, хз почему, этот диапазон не закольцован.
#         # поэтому выделяем красный цвет с одного и другого конца, а потом просто складываем обе битовые маски вместе
#
#         bin1 = cv2.inRange(hsv, (0, 60, 70), (10, 255, 255)) # красный цвет с одного конца
#         bin2 = cv2.inRange(hsv, (160, 60, 70), (179, 255, 255)) # красный цвет с другого конца
#         binary = bin1 + bin2  # складываем битовые маски
#         """
#         roi = cv2.bitwise_and(frame, frame,
#                               mask=binary)  # за счет полученной маски можно выделить найденный объект из общего кадра
#
#         contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL,
#                                        cv2.CHAIN_APPROX_NONE)  # получаем контуры выделенных областей
#
#         if len(contours) != 0:  # если найден хоть один контур
#             maxc = max(contours, key=cv2.contourArea)  # находим наибольший контур
#             moments = cv2.moments(maxc)  # получаем моменты этого контура
#             """
#             # moments["m00"] - нулевой момент соответствует площади контура в пикселях,
#             # поэтому, если в битовой маске присутствуют шумы, можно вместо
#             # if moments["m00"] != 0:  # использовать
#
#             if moments["m00"] > 20: # тогда контуры с площадью меньше 20 пикселей не будут учитываться
#             """
#             if moments["m00"] > 20:  # контуры с площадью меньше 20 пикселей не будут учитываться
#                 cx = int(moments["m10"] / moments["m00"])  # находим координаты центра контура (найденного объекта) по x
#                 cy = int(moments["m01"] / moments["m00"])  # находим координаты центра контура (найденного объекта) по y
#                 iSee = True  # устанавливаем флаг, что контур найден
#                 controlX = 2 * (
#                             cx - width / 2) / width  # находим отклонение найденного объекта от центра кадра и нормализуем его (приводим к диапазону [-1; 1])
#                 cv2.drawContours(frame, maxc, -1, (0, 255, 0), 2)  # рисуем контур
#                 cv2.line(frame, (cx, 0), (cx, height), (0, 255, 0), 2)  # рисуем линию линию по x
#                 cv2.line(frame, (0, cy), (width, cy), (0, 255, 0), 2)  # линия по y
#         cv2.putText(frame, 'iSee: {};'.format(iSee), (width - 370, height - 10),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2, cv2.LINE_AA)  # текст
#         cv2.putText(frame, 'controlX: {:.2f}'.format(controlX), (width - 200, height - 10),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2, cv2.LINE_AA)  # текст
#
#
#         def serialSend(data):  # Гл
#             txs = ','.join(map(str, data)) + ';'
#             Arduino.write(txs.encode())
#         controlX = (controlX + 1.0) / 2.0                       #с -1 до 1 преобразуем от 0 до 1
#         byte_value = str(int(controlX * 255))                   #с 0 до 1 преобразуем до 255 с помощью умножения пример(0.5 * 255 = 127)
#         green_val = byte_value + ", 0" + ", 0"
#         print(green_val)
#         def checkbox_click():
#             serialSend([1, int(byte_value)])
#         checkbox_click()
#
#         # cv2.circle(frame, (width//2, height//2), radius=4, color=(0, 0, 255), thickness=-1)    # центр кадра
#         cv2.imshow('frame', frame)  # выводим все кадры на экран
#         cv2.imshow('binary', binary)
#         cv2.imshow('roi', roi)
#     if cv2.waitKey(1) == ord('q'):  # чтоб выйти надо нажать 'q' на клавиатуре
#         break
# camera.release()
# cv2.destroyAllWindows()



######Работает!!!!






































# import cv2
# capture = cv2.VideoCapture(0)
# face_cascade = cv2.CascadeClassifier('haarcascade_lefteye_2splits.xml')
# face_cascade1 = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
# while True:
#     ret, img = capture.read()
#     if ret:
#         img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)  # переводим кадр из RGB в HSV
#         binary = cv2.inRange(img, (18, 60, 100), (32, 255, 255))  # пороговая обработка кадра (выделяем все желтое)
#         contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)  # получаем контуры выделенных областей
#     cv2.imshow('Kall', binary)
#     if cv2.waitKey(1) == ord('q'):
#         break
# capture.release()
# cv2.destroyAllWindows()

# import cv2
# capture = cv2.VideoCapture(0)
# face_cascade = cv2.CascadeClassifier('haarcascade_lefteye_2splits.xml')
# face_cascade1 = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
# while True:
#     ret, frame = capture.read()
#     if ret:
#         height, width = frame.shape[0:2]  # получаем разрешение кадра
#         frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)  # переводим кадр из RGB в HSV
#         binary = cv2.inRange(frame, (18, 60, 100), (32, 255, 255))  # пороговая обработка кадра (выделяем все желтое)
#         contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)  # получаем контуры выделенных областей
#         if len(contours) != 0:
#             maxc = max(contours, key=cv2.contourArea)
#             moments = cv2.moments(maxc)

#             if moments["m00"] > 20:
#                 cx = int(moments["m10"] / moments["m00"])
#                 cy = int(moments["m01"] / moments["m00"])
#                 iSee = True  # устанавливаем флаг, что контур найден
#                 controlX = 2 * (cx - width / 2) / width  # находим отклонение найденного объекта от центра кадра и
#                 # нормализуем его (приводим к диапазону [-1; 1])
#                 cv2.drawContours(frame, maxc, -1, (0, 255, 0), 1)  # рисуем контур
#                 cv2.line(frame, (cx, 0), (cx, height), (0, 255, 0), 1)  # рисуем линию линию по x
#                 cv2.line(frame, (0, cy), (width, cy), (0, 255, 0), 1)  # линия по y
#
#                 miniBin = cv2.resize(binary, (int(binary.shape[1] / 4), int(binary.shape[0] / 4)),  # накладываем поверх
#                                      interpolation=cv2.INTER_AREA)  # кадра маленькую
#                 miniBin = cv2.cvtColor(miniBin, cv2.COLOR_GRAY2BGR)  # битовую маску
#                 frame[-2 - miniBin.shape[0]:-2, 2:2 + miniBin.shape[1]] = miniBin  # для наглядности
#     cv2.imshow('Kall', frame)
#     if cv2.waitKey(1) == ord('q'):
#         break
# capture.release()
# cv2.destroyAllWindows()
#



# import cv2
# capture = cv2.VideoCapture(0)
# face_cascade = cv2.CascadeClassifier('haarcascade_lefteye_2splits.xml')
# face_cascade1 = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
# while True:
#     ret, img = capture.read()
#     faces = face_cascade.detectMultiScale(img, scaleFactor=1.5, minNeighbors=5, minSize=(20, 20))
#     for (x, y, w, h) in faces:
#         cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 255), 2)
#     faces = face_cascade1.detectMultiScale(img, scaleFactor=1.5, minNeighbors=5, minSize=(20, 20))
#     for (x, y, w, h) in faces:
#         cv2.rectangle(img, (x, y), (x+w, y+h), (0, 0, 255), 2)
#     cv2.imshow('Kall', img)
#     k = cv2.waitKey(30) & 0xFF
#     if k == 27:
#         break
# capture.release()
# cv2.destroyAllWindows()
#########
#Работает с двумя факторами



# import cv2
# capture = cv2.VideoCapture(0)
# face_cascade = cv2.CascadeClassifier('haarcascade_lefteye_2splits.xml')
# face_cascade1 = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
# while True:
#     ret, img = capture.read()
#     faces = face_cascade.detectMultiScale(img, scaleFactor=1.5, minNeighbors=5, minSize=(20, 20))
#     for (x, y, w, h) in faces:
#         cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 255), 2)
#     faces = face_cascade1.detectMultiScale(img, scaleFactor=1.5, minNeighbors=5, minSize=(20, 20))
#     for (x, y, w, h) in faces:
#         cv2.rectangle(img, (x, y), (x+w, y+h), (0, 0, 255), 2)
#     cv2.imshow('Kall', img)
#     k = cv2.waitKey(30) & 0xFF
#     if k == 27:
#         break
# capture.release()
# cv2.destroyAllWindows()
#########