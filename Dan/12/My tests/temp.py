class Main:
    num=0
    
    @staticmethod
    def divide(x,y):
        return Main.divideHelper(x,y)
        
    @staticmethod
    def divideHelper(x,y):
        if y>x:
            return 0
        q=Main.divideHelper(x,2*y)
        if((x-(Main.num))<y):
            return q+q
        else:
            Main.num=Main.num+y
            return q+q+1

print(Main.divide(13,3))