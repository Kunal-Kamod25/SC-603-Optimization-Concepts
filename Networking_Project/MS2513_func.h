#ifndef MS2513_FUN_H
#define MS2513_FUN_H

#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <time.h>
#include "MS2513_param.h"

// Function declarations
void initialize(int numHosts);
void connectors(Port P1[], Port P2[], int numHosts);

void testPStrip(int id, int numHosts);
void LLLStrip(int id, int numHosts);
void LANStrip(int numHosts);
void scheduler();

#endif