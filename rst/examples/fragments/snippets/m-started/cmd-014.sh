g++ -I<dir>/include -c send-more-money.cpp
g++ -o send-more-money -L<dir>/lib send-more-money.o \
  -lgecodesearch -lgecodeint -lgecodekernel -lgecodesupport
