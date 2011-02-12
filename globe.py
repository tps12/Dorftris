from math import pi, sin

from numpy.fft import fft

class GlobeFreq(object):
    res = 128

    @classmethod
    def sample(cls, globe):
        samples = []
        
        dphi = pi / cls.res
        for i in range(cls.res):
            phi = i * dphi - pi/2

            n = int(2 * cls.res * sin(phi + pi/2) + 0.5)
            if not n:
                continue
            
            dtheta = 2 * pi/n
            r = range(n) if (i&1) else range(n-1,-1,-1)
            for j in r:
                theta = pi - j * dtheta

                samples.append(globe.sample(phi * 180/pi, theta * 180/pi))
        return samples        
    
    @classmethod
    def transform(cls, globe):
        return fft(cls.sample(globe))

if __name__ == '__main__':
    from matplotlib.pyplot import plot, show, subplot

    def showfreq(planet):
        from numpy import linspace

        y = GlobeFreq.sample(planet)
        L = len(y)            # signal length
        fs = 5.0              # sampling rate
        T = 1/fs                # sample time
 
        f = fs*linspace(0,L/10,L/10)/L  # single side frequency vector, real frequency up to fs/2
        Y = fft(y)

        plot(f,2*abs(Y[0:L/10]))

    from planet import Planet
    from etopo import Earth
    planets = (Planet(), Earth())
    for i in range(len(planets)):
        subplot(len(planets), 1, i+1)
        showfreq(planets[i])
    show()
