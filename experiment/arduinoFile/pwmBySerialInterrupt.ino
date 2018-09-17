/* 
DESCRIPTION:
------------
Create two PWMs with Timer 1 (resolution > 8 bit,output is on pins 9 & 10). 
PWM value is updated by serial commands, received as USART interrupt. 

format for the serial command:

  "#%d: %d\r", with (%d) springNumber and (%d) PWMvalue


SETTINGS:
---------

setting the PWM on Timer 1 (16bit timer p.107 on the AVR ATmega32 manual: http://www.atmel.com/Images/doc2503.pdf ):
---------------------------
The PWM mode is selected by bits WGM13:10 (bits 3 to 0) (Table 47),
which are located on two registers: TCCR1A & TCCR1B
WGM13:12 are on TCCR1B (p. 110) & WGM11:10 are on TCCR1A (p. 107)

Mode selection: goal is to realize 2x PWMs with resolution > 8 bit. The intended purpose it to regulate
the el. current supplied to SMA wires, to activate them by Joule heating. Following the explanation for the 
different modes in http://www.avrfreaks.net/forum/tut-c-newbies-guide-avr-pwm-incomplete , Fast PWM is selected
(phase correctness does not matter), with the larger preset value for TOP (since we use both OCR1A/B 
registers to control the PWM-output)


Fast PWM - 10bit corresponds to Mode 7, i.e. #d07 --> #0b0111 (the values of WGM13:10), 
hence set WGM12:10, and leave WGM13 as is (at false))

The choice between inverting/ non-inverting PWM is by bits COMnx1:0 (with n=1:0 and x=A:B) on register TCCR1A,
the mapping depends on the values of WGM13:10 (Table 45 in the manual for fast-PWM): non-inverting --> set COM1x1

The prescaler value is set by bits CS12:10 (p.110), which controls the PWM frequency. For prescaler=1 --> set CS10 (on TCCR1A)

setting the USART
-----------------

the baud prescale is loaded on UBRR, which is formed by the two 8-bit registers UBRR0H:UBRR0L.
the baud prescale is described by the bits in UBRRL (7:0) and UBRRH (11:8). (p. 164)
the most significant bits (MSB) of UBRRH are: not available (14:12) and bit 15 is URSEL and must be zero when writing to UBRRH.
for an arduino UNO (atmega328p) f_cpu=16000000 at the lower possible rate (9600), the baud-prescale, is 0x67 (i.e. one byte), 
which means that you don't need the entire 8-bits of UBRRH. 

the way to load the prescaler is by right shifting the value and applying the mask to UBRR0H (the unavailable bits are dropped)
and apply the value (as is) on UBRRL (excessive bits are dropped)

UCSR0B:C hold the bits that enable RX/TX and interrupts on RX (used here)


using the USART
----------------
data is sent by verifying that there is no interrupt present; if so transmit data 1 x byte (char) at time:
(to check if interrupt is present)  UCSR0A & (1<<UDRE0): check if bit UDRE0 is 1 
this is because data for both RX/TX use register UDR

data is read by interrupt (served by the Interrupt Service Request), one character at a time and stored in a global variable. 
when the line terminator is read, the service routine is enabled, by setting the flag READ


 */

#include <avr/io.h>
#include <avr/interrupt.h>

#define USART_BAUDRATE 19200
#define BAUD_PRESCALE ((F_CPU / (USART_BAUDRATE * 16UL)) -1)  // set USART Baud Rate Register (Table 60)

char ReceivedBytes[20];
int i = 0;
boolean READ = false;

void setup(){
  TCCR1A |= B10100011; //(1<< COM1A1) | (1<< COM1B1) | (1<< WGM11)|(1<< WGM10);
  TCCR1B |= B00001001; // (1<< WGM12) | (1<< CS10);
  OCR1A = 0x02FF; // initialize register; remember: max = 0x03FF (10x bits)
  OCR1B = 0x02FF; 
  
  pinMode (9, OUTPUT);
  pinMode (10, OUTPUT);
 
  UCSR0B |= (1 << RXEN0)  | (1 << TXEN0); //turn on RX, TX circuits (p. 161)
  UCSR0C |= (3 << UCSZ00);  //frame format: 8-bit data (Table 66) (set bits UCSZ00 and UCSZ01 0d3=0b0011)

  UBRR0H = (BAUD_PRESCALE >> 8);  //load baud rate to register (example p.146)
  UBRR0L = BAUD_PRESCALE;

  UCSR0B |= (1 << RXCIE0);    // enable interrupts for USART0 (p. 161)
  sei();                      // enable global interrupts
}

// TX char by char (example code by the datasheet p.147)
void uart_transmit (char data)
{
    while (!( UCSR0A & (1<<UDRE0)));                // wait while register is free
      UDR0 = data;                                   // load data in the register
}

// send the string to the function char by char
void uart_string (char *send)    // this function is by: https://gist.github.com/adnbr/2629767
{
  while (*send) {
    uart_transmit (*send++);
  }
}


// check which pwm we are talking about
void process_pwm(char *fragment)
{
  int args_assigned;
  int int1, int2;
  
  args_assigned = sscanf (fragment, "#%d: %d", &int1, &int2);
  if (args_assigned != 2){
    uart_string("#e");
  }
  else{    
    switch (int1) {
      case 1:
        OCR1A = int2;
        uart_string("1");
        break;
      case 2:
        OCR1B = int2;
        uart_string("2");
        break;        
      default:
        uart_string("NA\n");
        break;
    }
  }
    
}

void loop(){
  if (READ){
    process_pwm( ReceivedBytes );
    READ = false;                                            // clear the flag set by ISR
    memset(&ReceivedBytes[0], 0, sizeof(ReceivedBytes));    // clear the buffer
  }

}


ISR(USART_RX_vect){
  char u;
  u = UDR0;
  if (u == '\r') {          // remember to use line terminator in the command from the PC
    READ = true;
    i = 0;                  // reset counter, to be able to read normally (FIFO)
  }
  else
  {
    ReceivedBytes[i++] = u;
  }
}

