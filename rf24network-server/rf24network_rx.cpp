/*
 Update 2014 - TMRh20
 */

/**
 * Simplest possible example of using RF24Network,
 *
 * RECEIVER NODE
 * Listens for messages from the transmitter and prints them out.
 */

#include <RF24/RF24.h>
#include <RF24Network/RF24Network.h>
#include <iostream>
#include <ctime>
#include <stdio.h>
#include <time.h>
#include <fstream>

/**
 * g++ -L/usr/lib main.cc -I/usr/include -o main -lrrd
 **/
//using namespace std;

// CE Pin, CSN Pin, SPI Speed

// Setup for GPIO 22 CE and GPIO 25 CSN with SPI Speed @ 1Mhz
//RF24 radio(RPI_V2_GPIO_P1_22, RPI_V2_GPIO_P1_18, BCM2835_SPI_SPEED_1MHZ);

// Setup for GPIO 22 CE and CE0 CSN with SPI Speed @ 4Mhz
//RF24 radio(RPI_V2_GPIO_P1_15, BCM2835_SPI_CS0, BCM2835_SPI_SPEED_4MHZ); 

// Setup for GPIO 22 CE and CE0 CSN with SPI Speed @ 8Mhz
RF24 radio(RPI_V2_GPIO_P1_15, BCM2835_SPI_CS0, BCM2835_SPI_SPEED_8MHZ);  

RF24Network network(radio);

// Address of our node in Octal format
const uint16_t base_node = 00;

const unsigned long interval = 500; //ms  // How often to send 'hello world to the other unit

unsigned long last_sent;             // When did we last send?
unsigned long packets_sent;          // How many have we sent already


struct payload_t {                  // Structure of our payload
  long totalPeopleInside;
  int peopleIn;
  int peopleOut;
};

int main(int argc, char** argv) 
{
	// Refer to RF24.h or nRF24L01 DS for settings
	std::cout << "RADIO: Begin" << std::endl;
	radio.begin();
	
	delay(1);
	std::cout << "NETWORK: Begin" << std::endl;
	network.begin(/*channel*/ 90, /*node address*/ base_node);
	radio.printDetails();
	
	while(1)
	{
		//std::cout << "NETWORK: Update" << std::endl;
		network.update();
  		while ( network.available() ) {     // Is there anything ready for us?
			time_t ltime = time(NULL); /* get current cal time */
    		std::cout << "NETWORK: New Message on " << asctime(localtime(&ltime)) << std::endl;

		 	RF24NetworkHeader header;        // If so, grab it and print it out
			payload_t payload;
  			network.read(header,&payload,sizeof(payload));
			
			std::cout << "Total people inside: " << (long)payload.totalPeopleInside << std::endl;
			std::cout << "People IN: " << (int)payload.peopleIn << " , People OUT: " << (int)payload.peopleOut << "." << std::endl;

			if( payload.peopleIn || payload.peopleOut ){
				char filename[25];
				sprintf(filename, "%d - %d.dat", (int)ltime, (int)header.from_node);
				ofstream output;
  				output.open(filename);
  				output << asctime(localtime(&ltime)) << std::endl;
  				output << (int)header.from_node << std::endl;
  				output << (int)payload.peopleIn << std::endl;
  				output << (int)payload.peopleOut << std::endl;
  				output.close();
  				std::cout << "File created: " << filename << std::endl;
			}
  		}		  
		delay(interval);
	}

	return 0;
}

