from scipy import signal
from scipy import misc
import numpy as np
import matplotlib.pyplot as plt

plt.imshow(misc.lena())
plt.show()

lena = misc.lena() - misc.lena().mean()
template = np.copy(lena[235:295, 310:370]) # right eye
template -= template.mean()
lena = lena + np.random.randn(*lena.shape) * 50 # add noise
corr = signal.correlate2d(lena, template, boundary='symm', mode='same')
y, x = np.unravel_index(np.argmax(corr), corr.shape) # find the match
fig1, (ax1,ax2,ax3) = plt.subplots(1,3)
ax1.imshow(misc.lena(),cmap="Greys_r")
ax2.imshow(template,cmap="Greys_r")
ax3.imshow(corr)
plt.show()
