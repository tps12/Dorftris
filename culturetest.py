import gettext
gettext.install('culturetest')

from culture import Culture

c = Culture()
print c.description()
