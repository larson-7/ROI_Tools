from cmath import polar, rect, pi as PI, e as E, phase

rad_to_deg = lambda r: r / 2 / PI * 360.0
deg_to_rad = lambda r: r * 2 * PI / 360.0
identity = lambda r: r







class Point(complex):
    def __repr__(self):
        return "<Point x:%.3f y:%.3f>" % self.as_euclidian()

    def as_euclidian(self):
        return (self.real, self.imag)

    def as_polar(self, measure="rad"):
        conv = measure == "rad" and identity or rad_to_deg
        return (abs(self), conv(phase(self)))


class Vector(Point):
    def __repr__(self):
        return "<Vector x:%.3f y:%.3f>" % self.as_euclidian()


class Rotation(Point):
    def __repr__(self):
        return "<Rotation r:%.3f theta:%.3f deg>" % self.as_polar("deg")

    def __init__(self, *a, **kw):
        if (abs(abs(self) - 1.0) > .0001):
            raise ValueError("norm must be 1")


I = complex("j")
point = center = Point(-1, -1)
vector = shape = Vector(2, 2)
rotation = r = Rotation(E ** (I * PI / 3))

print
"translating a point is as easy as"
print
"%r + %r = %r" % (point, vector, Point(point + vector))
print
"rotating a point is as easy as"
print
"%r * %r = %r" % (point, rotation, Point(point * rotation))


class Rectangle(object):
    def __init__(self, center, shape, rotation):
        self.center = center
        self.shape = shape
        self.rotation = rotation

    def __repr__(self):
        return "<Rectangle: Center %r, shape %r, rotation %r>" % (
            self.center, self.shape, self.rotation.as_polar('deg'))

    def area(self):
        return self.shape.imag * self.shape.real

    def as_points(self):
        return map(lambda p: Point((p / 2 + self.center) * self.rotation),
                   [-self.shape, Vector(-self.shape.real, self.shape.imag),
                    self.shape, Vector(self.shape.real, -self.shape.imag)])

    ### Quite trivial, pretty useless method
    def translation(self, vector):
        self.center += Vector(vector)

    def homothetia(self, factor):
        self.shape *= float(factor)

    def rotate(self, rotation):
        self.rotation *= Rotation(rotation)

    def rotate_from_origin(self, rotation):
        self.center *= Rotation(rotation)
        self.rotation *= Rotation(rotation)

    #### just for convenience, but really useless
    def as_polars(self, measure="rad"):
        return map(lambda p: p.as_polar(measure), self.as_points())

    def as_euclidians(self):
        return map(lambda p: p.as_euclidian(), self.as_points())

    def rotate_from_point(self, point, rotation):
        self.center -= Point(point)
        self.rotate_from_origin(Rotation(rotation))
        self.center += Point(point)


rec = Rectangle(center, shape, r)
print("let's see our rectangle true data %r" % rec)
print("list on euclidian coord  %r" % rec.as_euclidians())
print("let's list all the point in polar %r" % rec.as_polars())
print("rectangle area is %f" % rec.area())
print("center is %r" % rec.center)
print("apply a rotation of -60 degrees")
rec.rotate(rect(1, -PI / 3))
print("rotation becomes %r" % rec.rotation)
print("points are now %r" % rec.as_points())
print("distance from origin of all points of the rectangle %s" %
      (",".join(map(lambda p: "%.2f" % abs(p), rec.as_points()))))
print("angle in degrees from origin from all points of the rectangle %s" %
    ",".join(map(lambda r: "%.2f" % rad_to_deg(phase(r)), rec.as_points())))
print("let's center back the square to see")
rec.translation(-rec.center)
print("finally %r" % rec.as_points())

try:
    r = Rotation(1, 1)
except ValueError:
    print("Rotation is a complex with a norm of 1")
