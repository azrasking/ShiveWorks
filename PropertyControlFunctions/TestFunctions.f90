      module TestFunctions
      implicit none

      contains 

c     =================================================
      double precision function f(x)
c     =================================================

      implicit none

      double precision x

      common /pow/ power
      double precision power
  
cf2py intent(in) x
cf2py intent(out) f
 
      power=4.d0 

      if (x .gt. 0.d0) then
         f = 1.d0-1.d0/(1.d0+x**power)
      else
         f = 0.d0
      endif 
      
      return
      end function f





c     =================================================
      double precision function f_P(x)
c     =================================================

      implicit none
  
      double precision x
  
      common /pow/ power
      double precision power
   
cf2py intent(in) x
cf2py intent(out) f_P
      
      if (x .gt. 0.d0) then
         f_P = (power*x**(power-1.d0))/(1.d0+x**power)**2.d0
      else
         f_P = 0.d0
      endif

      return
      end function f_P





c     =================================================
      double precision function H(x,smt)
c     =================================================

      implicit none
      
      double precision x, smt

cf2py intent(in) x, smt
cf2py intent(out) H


      x = (x+smt/2.d0)/smt

      H = f(x)/(f(x)+f(1.d0-x))

      return
      end function H





c     =================================================
      double precision function H_P(x,smt)
c     =================================================

      implicit none

      double precision x, smt

cf2py intent(in) x, smt
cf2py intent(out) H_P


      x = (x+smt/2.d0)/smt

      H_P = (1.d0/smt)*(f(1.d0-x)*f_P(x)+f(x)*f_P(1.d0-x))/
     &                                        (f(x)+f(1.d0-x))**2

      return
      end function H_P





c     =================================================
      double precision function Rect(x,a,b,smt)
c     =================================================

      implicit none

      double precision x, a, b, smt

cf2py intent(in) x, a, b, smt
cf2py intent(out) Rect


      Rect = H(x-a,smt)-H(x-b,smt)

      return
      end function Rect





c     =================================================
      double precision function Rect_P(x,a,b,smt)
c     =================================================

      implicit none

      double precision x, a, b, smt

cf2py intent(in) x, a, b, smt
cf2py intent(out) Rect_P

      Rect_P = H_P(x-a,smt)-H_P(x-b,smt)

      return
      end function Rect_P





c     =================================================
      double precision function PI(x,t,a,b,c,d,smt_x,smt_t)
c     =================================================

      implicit none

      double precision x, t, a, b, c, d, smt_x, smt_t

cf2py intent(in) x, t, a, b, c, d, smt_x, smt_t
cf2py intent(out) PI

      PI = Rect(x,a,b,smt_x)*Rect(t,c,d,smt_t)

      return
      end function PI





c     =================================================
      double precision function PI_x(x,t,a,b,c,d,smt_x,smt_t)
c     =================================================

      implicit none

      double precision x, t, a, b, c, d, smt_x, smt_t

cf2py intent(in) x, t, a, b, c, d, smt_x, smt_t
cf2py intent(out) PI_x


      PI_x = Rect_P(x,a,b,smt_x)*Rect(t,c,d,smt_t)

      return
      end function PI_x





c     =================================================
      double precision function psi_lam(x,t,u1,u2,m,eps,V)
c     =================================================

      implicit none

      double precision x, t, u1, u2, m, eps, V
      double precision theta, eta, etaM, p1, p2, b1, b2

cf2py intent(in) x, t, u1, u2, m, eps, V
cf2py intent(out) psi_lam 

      theta=datan(V)  

      eta=dcos(theta)*x-dsin(theta)*t
      etaM=modulo(eta,eps)

         
      p1=Rect(etaM,  0.d0,       m*eps,       0.d0)
      p2=Rect(etaM,  m*eps,        eps,       0.d0)
      b1=Rect(etaM,-(1.d0-m)*eps, 0.d0,       0.d0)
      b2=Rect(etaM,   eps,       (1.d0+m)*eps,0.d0)

      psi_lam = (u1*p1+u2*p2)+(u2*b1+u1*b2)
 
c
      return
      end function psi_lam





c     =================================================
      double precision function psi_FG_lam(x,t,u1,u2,m,eps,V,smt)
c     =================================================

      implicit none

      double precision x, t, u1, u2, m, eps, V, smt
      double precision theta, eta, etaM, p1, p2, b1, b2

cf2py intent(in) x, t, u1, u2, m, eps, V, smt
cf2py intent(out) psi_FG_lam

      theta=datan(V)

      eta=dcos(theta)*x-dsin(theta)*t
      etaM=modulo(eta,eps)


      p1=Rect(etaM,  0.d0,       m*eps,       smt)
      p2=Rect(etaM,  m*eps,        eps,       smt)
      b1=Rect(etaM,-(1.d0-m)*eps, 0.d0,       smt)
      b2=Rect(etaM,   eps,       (1.d0+m)*eps,smt)

      psi_FG_lam = (u1*p1+u2*p2)+(u2*b1+u1*b2)

c
      return
      end function psi_FG_lam




c     =================================================
      double precision function psi_FG_cbd(x,t,u1,u2,m,n,eps,tau,
     &                                                smt_x,smt_t)
c     =================================================

      implicit none

      double precision x, t, u1, u2, m, n, eps, tau, smt_x, smt_t
      double precision xM, tM
      double precision p1, p2, p3, p4
      double precision b1, b2, b3, b4, b5, b6, b7, b8, b9, b10, b11, b12

cf2py intent(in) x, t, u1, u2, m, n, eps, tau, smt_x, smt_t
cf2py intent(out) psi_FG_cbd

      xM=modulo(x,eps)
      tM=modulo(t,tau)


c     #PI(x,t,a,b,c,d,smt_x,smt_t)

      p1=PI(xM,tM, 0.d0 , m*eps, 0.d0 , n*tau, smt_x,smt_t)
      p2=PI(xM,tM, m*eps, eps  , 0.d0 , n*tau, smt_x,smt_t)
      p3=PI(xM,tM, m*eps, eps  , n*tau, tau  , smt_x,smt_t)
      p4=PI(xM,tM, 0.d0 , m*eps, n*tau, tau  , smt_x,smt_t)

      b1=PI(xM,tM, 0.d0 , m*eps      ,-(1.d0-n)*tau,0.d0,smt_x,smt_t)
      b2=PI(xM,tM, m*eps,   eps      ,-(1.d0-n)*tau,0.d0,smt_x,smt_t)
      b3=PI(xM,tM, eps  ,(1.d0+m)*eps,-(1.d0-n)*tau,0.d0,smt_x,smt_t)

      b4=PI(xM,tM, eps  ,(1.d0+m)*eps, 0.d0 , n*tau      ,smt_x,smt_t)
      b5=PI(xM,tM, eps  ,(1.d0+m)*eps, n*tau, tau        ,smt_x,smt_t)
      b6=PI(xM,tM, eps  ,(1.d0+m)*eps,   tau,(1.d0+n)*tau,smt_x,smt_t)

      b7=PI(xM,tM, m*eps       ,   eps, tau, (1.d0+n)*tau, smt_x,smt_t) 
      b8=PI(xM,tM, 0.d0        , m*eps, tau, (1.d0+n)*tau, smt_x,smt_t)
      b9=PI(xM,tM,-(1.d0-m)*eps,  0.d0, tau, (1.d0+n)*tau, smt_x,smt_t)

      b10=PI(xM,tM,-(1.d0-m)*eps, 0.d0, n*tau,         tau,smt_x,smt_t)
      b11=PI(xM,tM,-(1.d0-m)*eps, 0.d0, 0.d0,        n*tau,smt_x,smt_t)
      b12=PI(xM,tM,-(1.d0-m)*eps, 0.d0,-(1.d0-n)*tau, 0.d0,smt_x,smt_t)

      psi_FG_cbd=u1*(p1+p3)+u2*(p2+p4)+
     &           u2*(b1+b3+b5+b7+b9 +b11)+
     &           u1*(b2+b4+b6+b8+b10+b12)

      return
      end function psi_FG_cbd





c     =================================================
      double precision function psi_cbd(x,t,u1,u2,m,n,eps,tau)
c     =================================================

      implicit none

      double precision x, t, u1, u2, m, n, eps, tau
      double precision xM, tM

cf2py intent(in) x, t, u1, u2, m, n, eps, tau
cf2py intent(out) psi_cbd

      xM=modulo(x,eps)
      tM=modulo(t,tau)


      if (( xM .lt. m*eps) .and. (tM .lt. n*tau )) then
         psi_cbd=u1
      elseif (( xM .ge. m*eps) .and. (tM .lt. n*tau )) then
         psi_cbd=u2
      elseif (( xM .lt. m*eps) .and. (tM .ge. n*tau )) then
         psi_cbd=u2
      else
         psi_cbd=u1
      endif

      return
      end function psi_cbd
      




c     =================================================
      double precision function f_u(x,t,u1,u2,geo)
c     =================================================
      
      implicit none
      
      double precision x, t, u1, u2
      double precision x1, x2      
      integer geo


c     # Following Lines Were Added By Bill to Adjust Clawpack to DM ##
c     ### Uncomment the following misssing blocks when compiling Clawpack 
c      !common /DM_Mat_Param/ k1, k2, rho1, rho2, Z1, Z2, v1, v2,
c     !&                      I1, I2,   c1,   c2
c      !double precision      k1, k2, rho1, rho2, Z1, Z2, v1, v2,
c     !&                      I1, I2,   c1,   c2

      common /DM_Geo_Param/ eps, tau, m1, n1, alp, bet, Vel, m2, n2
      double precision      eps, tau, m1, n1, alp, bet, Vel, m2, n2
c     ###############################################################


c     ## Remove the following Definitions When Compiling Clawpack#
      eps=1.d0; tau=1.0; m1=.4; n1=.5; alp=.5d0; bet=.5d0; Vel=1.d0 
      m2=1.d0-m1; n2=1.0-n1
c     ###############################################################

cf2py intent(in) x, t, u1, u2
cf2py intent(out) f_u

      x1=-2.0; x2=8.0;      


      select case (geo)

      case (1)
c        # Functionally Graded Lamination psi_FG_lam(x,t,u1,u2,m,eps,V,smt)
         if ((x .ge. x1).and.(x .le. x2)) then
            f_u=psi_lam(x,t,u1,u2,m1,eps,Vel)
         else
            f_u=u1
         endif

      case (2)
c        # Checkerboard psi_cbd(x,t,u1,u2,m,n,eps,tau)
         if ((x .ge. x1).and.(x .le. x2)) then
            f_u=psi_cbd(x,t,u1,u2,m1,n1,eps,tau)
         else
            f_u=u1
         endif

      case (3)
c        # FG Lamination - psi_FG_lam(x,t,u1,u2,m,eps,V,smt)
         if ((x .ge. x1).and.(x .le. x2)) then
            f_u=psi_FG_lam(x,t,u1,u2,m1,eps,Vel,alp)
         else
            f_u=u1
         endif
      
      case (4)
c        # FG Checkerboard - psi_FG_cbd(x,t,u1,u2,m,n,eps,tau,smt_x,smt_t)
         if ((x .ge. x1).and.(x .le. x2)) then
            f_u=psi_FG_cbd(x,t,u1,u2,m1,n1,eps,tau,alp,bet)
         else
            f_u=u1
         endif




      end select

      return
      end function f_u













      end module TestFunctions
