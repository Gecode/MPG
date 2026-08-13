g++ -std=c++17 -I<dir>/include -O3 -c send-more-money.cpp
g++ -std=c++17 -o send-more-money send-more-money.o \
  -L<dir>/lib -lgecodesearch -lgecodeint \
  -lgecodekernel -lgecodesupport
