i = [1,2,3]
a = i[:]

i.remove(2)
print(a,i)



    for i in b:  
        a.move(i, 0, -5)
        #if a.coords(i)[1] < 0:
            #a.delete(i); b.remove(i)

        for enemy2 in e2:
            for m in n :
                if (a.coords(m)[0] < a.coords(enemy2)[2] and 
                    a.coords(m)[2] > a.coords(enemy2)[0] and
                    a.coords(m)[1] < a.coords(enemy2)[3] and
                    a.coords(m)[3] > a.coords(enemy2)[1]):
                    a.delete(enemy2); e.remove(enemy2)
                    a.delete(m); b.remove(m)
                    score += 1
                    print("Score:", score)