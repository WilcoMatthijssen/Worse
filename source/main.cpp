#include "hwlib.hpp"

extern "C" void uart_put_char( char c ){
   hwlib::cout << c;
}

extern "C" int __main();

int main( void ){	
    
   // kill the watchdog
   WDT->WDT_MR = WDT_MR_WDDIS;
      
   hwlib::wait_ms( 500 );

   int result =__main();
   hwlib::cout<<result;

}

