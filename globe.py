from math import pi, sin

from numpy.fft import fft

class GlobeFreq(object):
    res = 128
    
    @classmethod
    def transform(cls, globe):
        samples = []
        
        d = pi / cls.res
        for i in range(cls.res):
            phi = i * d - pi/2

            for j in range(int(2 * cls.res * sin(phi + pi/2) + 0.5)):
                theta = pi - j * d

                samples.append(globe.sample(theta * 180/pi, phi * 180/pi))

        return fft(samples)

if __name__ == '__main__':
    from etopo import Earth
    freqs = GlobeFreq.transform(Earth())
    
    from matplotlib.pyplot import plot, show
    plot(abs(freqs))
    show()
