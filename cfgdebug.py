
def diff(par1, par2):
   r1 = par1.__repr__().split('\n')
   mlen = max(len(i) for i in r1)
   r2 = par2.__repr__().split('\n')
   format = '%-'+str(mlen)+'s %s %s'
   for l1, l2 in zip(r1, r2):
      if l1 == l2:
         print format % (l1, ' ', l2)
      else:
         print format % (l1, '|', l2)
   return

      
