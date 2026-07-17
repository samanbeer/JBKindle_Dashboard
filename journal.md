### Basic Clock 
- I learned how to use eips, and with help of png drawing a ceated simple clock that refreshes every 1m. Just starting out with this : )
- The library functions and logic is pretty easy to understand once you get familiar with it and make a lot of mistakes : )
- ![image1](images/01.jpg)

### First Layout, Better clock and other
- The first whing i did today and it took me a lot of time, was making a script to determine what resolution is my screen beacause the layout i made was never centered. So it looked like this:
    ![image2](images/02.jpg) so I writed a script that showed me the resolution: ![image3](images/03.png).
- Now the basic layout looks like this: ![image4](images/04.jpg)
- I also fixed some issues that the kindle clock, battery and wifi icon appeared on top of my dashbaord somtimes. So i just killed the procees on background for it :)

- Then I finished making kindle system info block with avvll kind of informations. The challange here was to make the progress bars on Battery and Wifi, and in overall drawing the graphics and symbols. But now it look really good. ![image5](images/05.jpg)
- Now i need to finish the news and weather block wchich will be kinda hard :) 

### News and weather
- The next thing I did was to finish the weather block, and the weather it gets from openmetoe free endpoint. And you can change the city by editing LATITUDE and LONGITUDE in the code.
    - The weather shows current temperature, how clouds are now formed, Feel like temperature, Humidity and windspeed. 
    - I think it is very practical at the desk because you can just look at the desk and see what to wear outside : )
- The next thing I added are news. It is downloading them from rss feed set in code (now from BBC).

### Crypto and Stocks
- I also wanted to see current crypto and Apple stock on it so i moved system stats from 4th block to the top above all blocks as a status line.
- And after lot of corrections the crypto and stocks infromation looks sooo good.
- It shows:
    - Crypto or Stock Name
    - Current price
    - 24 hour change in percentage

## Here is Final image:
![image6](images/06_final_image.jpg).


### Chalanges
- The hardest part was probably the logic of the code for the text to be exacly where I want. It took a lot of time centering and placing the text : )
    - hardest was the status bar to fit with a good layout
- Someone would thing that the code is hard but since we learn python at school and I am using it a lot it was not really a chalange for me. It would be if i was programming it in C language which is possible

