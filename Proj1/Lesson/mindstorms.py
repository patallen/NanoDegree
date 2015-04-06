import turtle

def draw_square(turtle):
    for x in range(4):
        turtle.forward(100)
        turtle.right(90)

def draw_art():
    window = turtle.Screen()
    window.bgcolor('red')
    brad = turtle.Turtle()
    brad.speed = 100

    for i in range(36):
        draw_square(brad)
        brad.right(10)
#    angie = turtle.Turtle()
#    angie.shape("arrow")
#    angie.color("blue")
#    angie.circle(100)

    window.exitonclick()

draw_art()
