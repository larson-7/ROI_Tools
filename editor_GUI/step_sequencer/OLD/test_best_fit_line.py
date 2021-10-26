import numpy as np
import matplotlib.pyplot as plt
from classes.line import Line

points = np.array([[1, 4], [2, 5], [7, 6], [-1, -1]])

test_1d =np.array([1,2,3,4])

test_1d_rev = np.array([[1],[2],[3],[4]])

test_line = np.array([points[1], points[2]])
test_center = (test_line[0] + test_line[1])/2
dx = test_line[1][0] - test_center[0]
dy = test_line[1][1] - test_center[1]
norm = np.array([dx, dy])/np.linalg.norm(np.array([test_center, [dx, dy]])) + test_center
print(norm)
xn = [test_center[0], norm[0]]
yn = [test_center[1], norm[1]]
xl, yl = test_line.T
x,y = points.T

plt.plot(x,y, 'o', label='Original data', markersize=10)
plt.plot(xl, yl, 'r', label='Fitted line')
plt.plot(test_center[0],test_center[1], 'o', color='black', label='center', markersize=5)
plt.plot(xn, yn, 'b', label='normal vector')


plt.legend()
plt.show()
