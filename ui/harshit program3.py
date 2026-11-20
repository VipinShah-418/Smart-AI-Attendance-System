
import turtle
window = turtle.Screen()

player1 = turtle.Turtle()
player1.shape('turtle')
player1.color('turquoise')
player1.penup()
player1.goto(-150, 100)

player2 = turtle.Turtle()
player2.shape('turtle')
player2.color('red')
player2.penup()
player2.goto(-150, -60)

#Drawing Shapes
pen = turtle.Turtle()
pen.penup()
pen.goto(150, -140)
pen.pendown()
pen.color("black")
pen.begin_fill()

for fin in range(2):
    pen.forward(20)
    pen.left(90)
    pen.forward(300)
    pen.left(90)

pen.end_fill()
pen.penup()
pen.goto(-150, 60)
pen.pendown()
pen.circle(40)
pen.penup()
pen.goto(-150, -100)
pen.pendown()
pen.circle(40)