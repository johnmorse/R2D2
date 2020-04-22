import r2buttons

xboxkey = "12345678912345678"
print(xboxkey)
systemkey = r2buttons.getKeyString(xboxkey, True)
print(systemkey)
newxboxkey = r2buttons.getKeyString(systemkey, False)
print(newxboxkey)


class Controller:
    def buttonCount(self):
        return self.__buttonCount
	
    def __init__(self, buttonCount):
        self.__buttonCount = buttonCount

x0 = Controller(10)
x1 = Controller(11)

print(x1.buttonCount())
print(x0.buttonCount())
