import numpy as np  #import the NumPy library for numerical operations

# Create 1D NumPy arrays
# Initializing 1-dimensional arrays
arr1 = np.array([1,2,3,4,5])
arr2 = np.array([5,4,3,2,1])

print (arr1)

# Create 2D NumPy arrays
# Initializing 2-dimensional arrays
arr3 = np.array([[1,2,3],[4,5,6]])
print (arr3)



a = np.array([1,2,3,4,5,6,7,8,9])
print(a)
b = a.reshape ((3,3))
print(b)


c = np.zeros((2,2))
print(c)

d = np.ones((1,5))
print(d)

array_2d = np.array([[1,2,3],[4,5,6],[7,8,9]])
element = array_2d[0,2]
print (element)

subset = array_2d[0:2,1:]
print (subset)
