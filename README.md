# EjerciciosMqtt

## Ejercicio 1

Esta dividido en 2 partes, el test como subscriptor y el test como publisher

## Ejercicio 2

Se subscribe al topic de numbers y va almacenando los numeros, asi como los separa en float e int. Ademas comprueba si es primo cuando estamos con un entero.

Cada 10s, por defecto, hace una actualizacion de los numeros que han ido apareciendo.

## Ejercicio 3

Se subscribe a todos los subtopics de temperature/, va almacenando las temperaturas en un diccionario, ya que asi las separa por sensores.

Cada 8s, por defecto, actualiza la temp maxima, minima y media para todos los sensores y en global.

## Ejercicio 4

Analogo al ejemplo del Ej4, generalizandolo con los valores K_{i} como constantes iniciales.

## Ejercicio 5
Analogo al ejemplo del Ej5.

## Ejercicio 6
Utiliza 2 clientes, el primero esta subscrito al topic numbers, y cada vez que hay un entero positivo par inicia un proceso.

El proceso que se ejecuta genera un entero que nos va a servir para el temporizador, primero inicializa un temporizador para ir guardando la temperatura y una vez acabado calcula su valor medio, si esta en rango el proceso acaba. Si no, inicializa otro temporizador pero esta vez para guardar la humedad y una vez acabado calcula su media. Devuelve por pantalla si estos datos esta en rango.

El segundo cliente esta subscrito al topic temperature/.. , humidity y /clients/timer que actuara como canal para el temporizador.
La funcion on message de este cliente se encargara de recivir la notificacion del temporizador y actuar en consecuencia.

