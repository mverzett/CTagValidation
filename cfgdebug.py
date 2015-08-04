
def txt_diff(one, two):
   r1 = one.split('\n')
   mlen = max(len(i) for i in r1)
   r2 = two.split('\n')
   format = '%-'+str(mlen)+'s %s %s'
   for l1, l2 in zip(r1, r2):
      if l1 == l2:
         print format % (l1, ' ', l2)
      else:
         print format % (l1, '|', l2)
   return
   

def diff(par1, par2):
   txt_diff(par1.__repr__(), par2.__repr__())
   
