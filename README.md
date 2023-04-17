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
Genera 3 clientes, donde cada uno esta escuchando un topic (numbers, temperature, humidity). Cuando numbers lee un numero primo, inicia un temporizador, que le dice a temperatura que empiece a grabar hasta que este acaba. Entonces si calcula la media.

Si esta, se encuentra fuera de rango, se hace lo mismo para humedad y calculando la humedad media al final. Cuando acaba cada proceso, indica si estan dentro o fuera de rango.

El ejercicio esta a falta de afinar unos detalles sobre procesos y como pasar una lista compartida, o mas bien donde generarla.